"""Formatting helper utilities."""


def format_seconds(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string."""
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
