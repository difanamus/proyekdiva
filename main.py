"""ClipForge Offline main application entrypoint."""

from __future__ import annotations

from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.screenmanager import MDScreenManager

from screens.analysis_screen import AnalysisScreen
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from theme import APP_THEME


class ClipForgeApp(MDApp):
    """Root app class with responsive desktop/mobile navigation."""

    def build(self):
        self.title = APP_THEME.APP_TITLE
        self.theme_cls.primary_palette = APP_THEME.PRIMARY_PALETTE
        self.theme_cls.accent_palette = APP_THEME.ACCENT_PALETTE
        self.theme_cls.theme_style = APP_THEME.THEME_STYLE

        self.root_layout = MDBoxLayout(orientation="vertical")
        self._render_layout(Window.width, Window.height)
        Window.bind(size=self._on_window_size)
        return self.root_layout

    def _on_window_size(self, _instance, size):
        self._render_layout(size[0], size[1])

    def _render_layout(self, width: int, height: int):
        self.root_layout.clear_widgets()
        is_desktop = width >= dp(800) or width > height
        if is_desktop:
            self.root_layout.add_widget(self._desktop_layout())
        else:
            self.root_layout.add_widget(self._mobile_layout())

    def _desktop_layout(self) -> MDBoxLayout:
        wrapper = MDBoxLayout(orientation="horizontal")

        manager = MDScreenManager()
        manager.add_widget(HomeScreen())
        manager.add_widget(AnalysisScreen())
        manager.add_widget(SettingsScreen(app=self))

        nav_rail = MDNavigationRail()
        nav_rail.add_widget(MDNavigationRailItem(icon="home", text="Home", on_release=lambda *_: self._goto(manager, "home")))
        nav_rail.add_widget(
            MDNavigationRailItem(icon="movie-open", text="Analyze", on_release=lambda *_: self._goto(manager, "analysis"))
        )
        nav_rail.add_widget(
            MDNavigationRailItem(icon="cog", text="Settings", on_release=lambda *_: self._goto(manager, "settings"))
        )

        wrapper.add_widget(nav_rail)
        wrapper.add_widget(manager)
        return wrapper

    def _mobile_layout(self) -> MDBottomNavigation:
        """Bottom navigation layout tailored for mobile-sized windows."""
        bottom = MDBottomNavigation()

        home = MDBottomNavigationItem(name="home", text="Home", icon="home")
        home.add_widget(HomeScreen())

        analysis = MDBottomNavigationItem(name="analysis", text="Analyze", icon="movie-open")
        analysis.add_widget(AnalysisScreen())

        settings = MDBottomNavigationItem(name="settings", text="Settings", icon="cog")
        settings.add_widget(SettingsScreen(app=self))

        bottom.add_widget(home)
        bottom.add_widget(analysis)
        bottom.add_widget(settings)
        return bottom

    @staticmethod
    def _goto(manager: MDScreenManager, screen_name: str):
        manager.current = screen_name


if __name__ == "__main__":
    ClipForgeApp().run()
