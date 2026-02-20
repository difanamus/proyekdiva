"""Settings screen."""

from kivy.metrics import dp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDSwitch


class SettingsScreen(MDScreen):
    """Simple settings panel for demo toggles."""

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.name = "settings"

        root = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        row.add_widget(MDLabel(text="Dark Theme", style="Body", adaptive_height=True))
        self.theme_switch = MDSwitch(active=True)
        self.theme_switch.bind(active=self._toggle_theme)
        row.add_widget(self.theme_switch)

        root.add_widget(row)
        root.add_widget(
            MDLabel(
                text="More settings can be added for export presets and scoring sensitivity.",
                style="Body",
            )
        )
        self.add_widget(root)

    def _toggle_theme(self, _instance, value: bool):
        self.app.theme_cls.theme_style = "Dark" if value else "Light"
