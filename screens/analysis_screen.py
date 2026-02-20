"""Video analysis screen with offline processing."""

from __future__ import annotations

from threading import Thread

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivymd.uix.screen import MDScreen

from services.video_analyzer import VideoAnalyzer, VideoAnalyzerError
from utils.formatters import format_seconds


class AnalysisScreen(MDScreen):
    """Screen for selecting a local file and running analysis."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "analysis"
        self.analyzer = VideoAnalyzer()

        root = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        self.file_chooser = FileChooserListView(filters=["*.mp4", "*.mov", "*.mkv", "*.avi"])
        root.add_widget(self.file_chooser)

        controls = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        run_button = MDButton(
            MDButtonText(text="Analyze Selected Video"),
            on_release=self._start_analysis,
        )
        controls.add_widget(run_button)

        self.loader = MDCircularProgressIndicator(size_hint=(None, None), size=(dp(32), dp(32)), active=False)
        controls.add_widget(self.loader)
        root.add_widget(controls)

        self.result_label = MDLabel(text="Results will appear here.", style="Body", halign="left")
        root.add_widget(self.result_label)

        self.add_widget(root)

    def _start_analysis(self, *_args):
        selection = self.file_chooser.selection
        if not selection:
            toast("Please choose a video file first.")
            return

        self.loader.active = True
        self.result_label.text = "Analyzing..."
        video_path = selection[0]

        worker = Thread(target=self._analyze_worker, args=(video_path,), daemon=True)
        worker.start()

    def _analyze_worker(self, video_path: str) -> None:
        try:
            result = self.analyzer.analyze(video_path)
            Clock.schedule_once(lambda *_: self._show_result(result))
        except VideoAnalyzerError as exc:
            Clock.schedule_once(lambda *_: self._show_error(str(exc)))

    def _show_result(self, result):
        self.loader.active = False
        summary = [
            f"File: {result.file_path}",
            f"Duration: {format_seconds(result.duration)}",
            f"FPS: {result.fps:.2f}",
            f"Scene changes: {len(result.scene_changes)}",
            f"Audio spikes: {len(result.audio_spikes)}",
            f"Silence segments: {len(result.silence_segments)}",
            f"Engagement score: {result.engagement_score}/100",
            (
                "Metrics -> "
                f"scene_density={result.details['scene_density']}, "
                f"spike_density={result.details['audio_spike_density']}, "
                f"silence_ratio={result.details['silence_ratio']}"
            ),
        ]
        self.result_label.text = "\n".join(summary)

    def _show_error(self, message: str):
        self.loader.active = False
        self.result_label.text = f"Error: {message}"
        toast("Video analysis failed. Check logs for details.")
