"""Analysis screen compatible with KivyMD 1.x.

This module avoids importing ``MDButton``/``MDButtonText`` which only exist in
newer KivyMD builds and can raise ImportError on common 1.x installations.
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen


class AnalysisScreen(MDScreen):
    """Simple analysis screen with a version-compatible button."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        self.run_button = MDRaisedButton(
            text="Mulai Analisis",
            pos_hint={"center_x": 0.5},
            on_release=self.on_run_analysis,
        )
        root.add_widget(self.run_button)
        self.add_widget(root)

    def on_run_analysis(self, *_args):
        """Button callback placeholder."""
        # Isi logic analisis kamu di sini.
        return None
