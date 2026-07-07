"""
===============================================================================
RemoteDesk Pro
File: gui/main_window.py

The main application window that contains all UI components and orchestrates
the application lifecycle. This is the central hub of the GUI.
===============================================================================
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import customtkinter

from core.constants import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from core.config_manager import get_config_manager
from core.theme_manager import get_theme_manager
from core.utils import ensure_directories
from gui.components.titlebar import TitleBar
from gui.components.sidebar import Sidebar
from gui.components.statusbar import StatusBar
from gui.components.notifications import NotificationManager

if TYPE_CHECKING:
    from gui.pages.dashboard import DashboardPage
    from gui.pages.settings import SettingsPage
    from gui.pages.logs import LogsPage
    from gui.pages.about import AboutPage
    from gui.pages.connection import ConnectionPage


class NavigationManager:
    """
    Manages navigation between different pages in the application.
    Handles page registration, switching, and sidebar synchronization.
    """

    def __init__(self, master: customtkinter.CTk, sidebar: Sidebar) -> None:
        self._master = master
        self._sidebar = sidebar
        self._pages: dict[str, customtkinter.CTkFrame] = {}
        self._current_page: str | None = None

    def register_page(self, key: str, page: customtkinter.CTkFrame) -> None:
        """Register a page with the navigation manager."""
        self._pages[key] = page
        page.pack_forget()  # Hide initially

    def show_page(self, key: str) -> None:
        """Switch to display the specified page."""
        if key not in self._pages:
            return

        # Hide current page
        if self._current_page and self._current_page in self._pages:
            self._pages[self._current_page].pack_forget()

        # Show new page
        self._pages[key].pack(fill="both", expand=True)
        self._current_page = key
        
        # Update sidebar active state
        self._sidebar.set_active_page(key)

    def get_current_page(self) -> str | None:
        """Get the key of the currently displayed page."""
        return self._current_page


class MainWindow(customtkinter.CTk):
    """
    Main application window for RemoteDesk Pro.
    
    Features:
    - Custom title bar
    - Collapsible sidebar navigation
    - Content area for pages
    - Status bar with system monitors
    - Theme-aware styling
    """

    def __init__(self, config_manager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self._theme_manager = get_theme_manager()
        self._navigation_manager: NavigationManager | None = None
        self._is_running = False

        # Initialize
        self._setup_window()
        self._setup_components()
        self._setup_navigation()

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        # Set initial theme
        theme = self.config_manager.get_value("config", "theme", "dark")
        if hasattr(customtkinter, "set_appearance_mode"):
            customtkinter.set_appearance_mode(theme)
        else:
            self.set_appearance_mode(theme)

        # Window dimensions
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resizable(True, True)

        # Title
        self.title(f"RemoteDesk Pro v{APP_VERSION}")

    def _setup_components(self) -> None:
        """Initialize UI components (titlebar, sidebar, content, statusbar)."""
        # Ensure directories exist
        ensure_directories()

        # Initialize notification system
        NotificationManager.get_instance().initialize(self)

        # Create title bar
        logo_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "images", "app_icon.png"
        )
        self.title_bar = TitleBar(self, title=APP_NAME, icon_path=logo_path)
        self.title_bar.pack(fill="x", side="top")

        # Create sidebar
        self.sidebar = Sidebar(
            self,
            navigate_callback=self._on_sidebar_click,
        )
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        # Create content frame
        self.content_frame = customtkinter.CTkFrame(
            self,
            fg_color=self._theme_manager.get_color("background", "#0D0D0D"),
        )
        self.content_frame.pack(fill="both", expand=True)

        # Create status bar
        self.status_bar = StatusBar(
            self,
            toggle_theme_callback=self._toggle_theme,
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _setup_navigation(self) -> None:
        """Set up the navigation manager and load initial pages."""
        from gui.pages.dashboard import DashboardPage
        from gui.pages.settings import SettingsPage
        from gui.pages.logs import LogsPage
        from gui.pages.about import AboutPage
        from gui.pages.connection import ConnectionPage

        # Create navigation manager
        self._navigation_manager = NavigationManager(self, self.sidebar)

        # Register pages
        self._navigation_manager.register_page("dashboard", DashboardPage(self))
        self._navigation_manager.register_page("settings", SettingsPage(self))
        self._navigation_manager.register_page("logs", LogsPage(self))
        self._navigation_manager.register_page("about", AboutPage(self))
        self._navigation_manager.register_page("connection", ConnectionPage(self))

        # Show dashboard
        self._navigation_manager.show_page("dashboard")

    def _on_sidebar_click(self, page_key: str) -> None:
        """Handle sidebar navigation clicks."""
        if self._navigation_manager:
            self._navigation_manager.show_page(page_key)

    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current = self._theme_manager.current_theme_name
        new_theme = "light" if current == "dark" else "dark"
        self._theme_manager.set_theme(new_theme)
        self.config_manager.set_value("config", "theme", new_theme)

    def run(self) -> None:
        """Start the application main loop."""
        self._is_running = True
        self.mainloop()
        self._is_running = False


def create_main_window(config_manager) -> MainWindow:
    """Factory function to create the main application window."""
    return MainWindow(config_manager)