"""Entry point for local run/testing."""

from kivymd.app import MDApp

from screens.analysis_screen import AnalysisScreen


class DivaApp(MDApp):
    def build(self):
        return AnalysisScreen()


if __name__ == "__main__":
    DivaApp().run()
