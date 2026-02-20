"""Offline video analysis service for ClipForge Offline.

Features:
- Audio energy spike detection
- Silence detection
- Scene change detection with OpenCV
- Engagement scoring
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import wave
import contextlib

import cv2
import numpy as np
from moviepy.editor import VideoFileClip


@dataclass
class AnalysisResult:
    """Container for analysis output."""

    file_path: str
    duration: float
    fps: float
    audio_spikes: List[float]
    silence_segments: List[Tuple[float, float]]
    scene_changes: List[float]
    engagement_score: float
    details: Dict[str, float]


class VideoAnalyzerError(Exception):
    """Raised when analysis cannot be completed."""


class VideoAnalyzer:
    """Main class to orchestrate offline video analysis."""

    def __init__(self, scene_threshold: float = 28.0) -> None:
        self.scene_threshold = scene_threshold

    def analyze(self, video_path: str) -> AnalysisResult:
        """Run the full analysis pipeline.

        Args:
            video_path: Path to local video file.

        Returns:
            AnalysisResult with timeline information.
        """

        source = Path(video_path)
        if not source.exists():
            raise VideoAnalyzerError(f"Video not found: {video_path}")

        try:
            duration = self._get_duration(video_path)
            fps, scene_changes = self._detect_scene_changes(video_path)
            audio_spikes, silence_segments = self._analyze_audio(video_path, duration)
            engagement_score, details = self._calculate_engagement_score(
                duration=duration,
                scene_changes=scene_changes,
                spikes=audio_spikes,
                silence_segments=silence_segments,
            )
            return AnalysisResult(
                file_path=video_path,
                duration=duration,
                fps=fps,
                audio_spikes=audio_spikes,
                silence_segments=silence_segments,
                scene_changes=scene_changes,
                engagement_score=engagement_score,
                details=details,
            )
        except VideoAnalyzerError:
            raise
        except Exception as exc:  # broad catch to provide user-friendly error message
            raise VideoAnalyzerError(f"Analysis failed for {video_path}: {exc}") from exc

    def _get_duration(self, video_path: str) -> float:
        try:
            with VideoFileClip(video_path) as clip:
                return float(clip.duration or 0.0)
        except Exception as exc:
            raise VideoAnalyzerError(f"Could not read video duration: {exc}") from exc

    def _detect_scene_changes(self, video_path: str) -> Tuple[float, List[float]]:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoAnalyzerError("OpenCV could not open the video file.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        prev_gray = None
        frame_idx = 0
        scene_changes: List[float] = []

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                mean_diff = float(np.mean(diff))
                if mean_diff >= self.scene_threshold:
                    timestamp = frame_idx / fps
                    scene_changes.append(round(timestamp, 2))
            prev_gray = gray
            frame_idx += 1

        cap.release()
        return fps, scene_changes

    def _analyze_audio(self, video_path: str, duration: float) -> Tuple[List[float], List[Tuple[float, float]]]:
        """Extract temporary WAV and detect spikes + silence."""

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            wav_path = tmp_wav.name

        try:
            with VideoFileClip(video_path) as clip:
                if clip.audio is None:
                    return [], [(0.0, duration)] if duration > 0 else []
                clip.audio.write_audiofile(
                    wav_path,
                    fps=16000,
                    nbytes=2,
                    codec="pcm_s16le",
                    verbose=False,
                    logger=None,
                )

            samples, sample_rate = self._read_wav_mono(wav_path)
            if samples.size == 0:
                return [], []

            frame_size = int(sample_rate * 0.1)  # 100ms windows
            energies = self._window_rms(samples, frame_size)
            times = np.arange(len(energies), dtype=float) * 0.1

            median_energy = float(np.median(energies))
            spike_threshold = max(median_energy * 2.3, 0.01)
            silence_threshold = max(median_energy * 0.3, 0.003)

            spike_times = [round(float(t), 2) for t, e in zip(times, energies) if e >= spike_threshold]
            silence_segments = self._silence_segments(times, energies, silence_threshold)
            return spike_times, silence_segments
        except Exception as exc:
            raise VideoAnalyzerError(f"Audio analysis failed: {exc}") from exc
        finally:
            Path(wav_path).unlink(missing_ok=True)

    def _read_wav_mono(self, wav_path: str) -> Tuple[np.ndarray, int]:
        with contextlib.closing(wave.open(wav_path, "rb")) as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)

        data = np.frombuffer(raw, dtype=np.int16)
        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=1)
        normalized = data.astype(np.float32) / 32768.0
        return normalized, sample_rate

    def _window_rms(self, samples: np.ndarray, frame_size: int) -> np.ndarray:
        if frame_size <= 0:
            return np.array([], dtype=np.float32)
        chunks = max(1, len(samples) // frame_size)
        energies: List[float] = []
        for idx in range(chunks):
            start = idx * frame_size
            end = min((idx + 1) * frame_size, len(samples))
            window = samples[start:end]
            if window.size == 0:
                continue
            rms = float(np.sqrt(np.mean(np.square(window))))
            energies.append(rms)
        return np.array(energies, dtype=np.float32)

    def _silence_segments(
        self,
        times: np.ndarray,
        energies: np.ndarray,
        silence_threshold: float,
    ) -> List[Tuple[float, float]]:
        segments: List[Tuple[float, float]] = []
        start = None

        for t, e in zip(times, energies):
            if e <= silence_threshold and start is None:
                start = float(t)
            elif e > silence_threshold and start is not None:
                if float(t) - start >= 0.5:  # keep meaningful silence intervals
                    segments.append((round(start, 2), round(float(t), 2)))
                start = None

        if start is not None and len(times):
            end_time = float(times[-1] + 0.1)
            if end_time - start >= 0.5:
                segments.append((round(start, 2), round(end_time, 2)))

        return segments

    def _calculate_engagement_score(
        self,
        duration: float,
        scene_changes: List[float],
        spikes: List[float],
        silence_segments: List[Tuple[float, float]],
    ) -> Tuple[float, Dict[str, float]]:
        if duration <= 0:
            return 0.0, {"scene_density": 0.0, "audio_spike_density": 0.0, "silence_ratio": 1.0}

        scene_density = len(scene_changes) / max(duration, 1.0)
        spike_density = len(spikes) / max(duration, 1.0)
        silence_duration = sum(end - start for start, end in silence_segments)
        silence_ratio = min(1.0, silence_duration / duration)

        # Weighted heuristic normalized to 0..100.
        raw_score = (
            min(scene_density * 35.0, 35.0)
            + min(spike_density * 35.0, 35.0)
            + (1.0 - silence_ratio) * 30.0
        )
        engagement_score = round(max(0.0, min(100.0, raw_score)), 2)

        details = {
            "scene_density": round(scene_density, 4),
            "audio_spike_density": round(spike_density, 4),
            "silence_ratio": round(silence_ratio, 4),
        }
        return engagement_score, details
