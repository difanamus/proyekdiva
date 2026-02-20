"""Home screen for ClipForge Offline."""

from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class HomeScreen(MDScreen):
    """Landing screen with project description."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        container = MDBoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
        )
        container.add_widget(
            MDLabel(
                text="ClipForge Offline",
                style="Headline",
                halign="left",
                adaptive_height=True,
            )
        )
        container.add_widget(
            MDLabel(
                text=(
                    "Analyze local videos offline and estimate engagement with scene changes, "
                    "audio spikes, and silence signals."
                ),
                style="Body",
                halign="left",
            )
        )
        self.add_widget(container)
