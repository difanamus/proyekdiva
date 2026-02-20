"""Theme configuration for ClipForge Offline."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppTheme:
    """Simple theme constants shared by the application."""

    PRIMARY_PALETTE: str = "BlueGray"
    ACCENT_PALETTE: str = "Amber"
    THEME_STYLE: str = "Dark"
    APP_TITLE: str = "ClipForge Offline"


APP_THEME = AppTheme()
