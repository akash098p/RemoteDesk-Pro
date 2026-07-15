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
import tkinter.messagebox as messagebox
from typing import TYPE_CHECKING

import customtkinter

from core.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_PORT,
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
from network.connection_manager import ConnectionManager

if TYPE_CHECKING:
    from gui.pages.dashboard import DashboardPage
    from gui.pages.settings import SettingsPage
    from gui.pages.logs import LogsPage
    from gui.pages.about import AboutPage
    from gui.pages.connection import ConnectionPage
    from gui.pages.chat import ChatPage
    from gui.pages.clipboard import ClipboardPage
    from gui.pages.screen import ScreenPage


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
        self.connection_manager = ConnectionManager(DEFAULT_PORT)
        self._chat_page: "ChatPage" | None = None
        self._screen_page: "ScreenPage" | None = None
        self.username = self.config_manager.get_value("config", "username", "Local")
        self._is_running = False
        self._theme_manager.register_theme_change_callback(self._on_theme_change)

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
            corner_radius=0,
        )
        self.content_frame._app = self
        self.content_frame._theme_manager = self._theme_manager
        self.content_frame._connection_manager = self.connection_manager
        self.content_frame.pack(fill="both", expand=True, padx=(10, 10), pady=(10, 8))

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
        from gui.pages.screen import ScreenPage
        from gui.pages.chat import ChatPage
        from gui.pages.clipboard import ClipboardPage

        # Create navigation manager
        self._navigation_manager = NavigationManager(self.content_frame, self.sidebar)
        self.content_frame._navigation_manager = self._navigation_manager

        # Register pages
        self._navigation_manager.register_page("dashboard", DashboardPage(self.content_frame))
        self._navigation_manager.register_page(
            "connection",
            ConnectionPage(self.content_frame, on_connect=self._connect_to_device),
        )
        self._screen_page = ScreenPage(self.content_frame)
        self._navigation_manager.register_page("screen", self._screen_page)
        self._chat_page = ChatPage(self.content_frame)
        self._navigation_manager.register_page("chat", self._chat_page)
        self._navigation_manager.register_page("clipboard", ClipboardPage(self.content_frame))
        self._navigation_manager.register_page("settings", SettingsPage(self.content_frame))
        self._navigation_manager.register_page("logs", LogsPage(self.content_frame))
        self._navigation_manager.register_page("about", AboutPage(self.content_frame))

        if self._chat_page is not None:
            self._chat_page.set_send_callback(self.send_chat_message)

        self._register_connection_callbacks()
        self.connection_manager.start_server(port=DEFAULT_PORT)

        # Show dashboard
        self._navigation_manager.show_page("dashboard")

    def _register_connection_callbacks(self) -> None:
        """Route connection events into the active GUI pages."""
        self.connection_manager.register_callback(
            "status",
            lambda status, ok=True: self.after(
                0, lambda: self.status_bar.set_connection_status(status, is_connected=ok)
            ),
        )
        self.connection_manager.register_callback(
            "screen_frame",
            lambda payload: self.after(
                0, lambda: self._screen_page and self._screen_page.handle_remote_frame(payload)
            ),
        )
        self.connection_manager.register_callback(
            "audio_frame",
            lambda payload: self.after(
                0, lambda: self._screen_page and self._screen_page.handle_remote_audio(payload)
            ),
        )
        self.connection_manager.register_callback(
            "chat_message",
            lambda payload, peer_id=None: self.after(
                0, lambda: self._chat_page and self._chat_page.receive_network_message(payload)
            ),
        )
        self.connection_manager.register_callback(
            "peer_disconnected",
            lambda peer: self.after(
                0,
                lambda: NotificationManager.get_instance().show_info(
                    f"{peer.device_name} disconnected.",
                    title="Connection",
                ),
            ),
        )
        self.connection_manager.register_callback(
            "control_request",
            lambda payload, peer_id=None: self.after(0, lambda: self._handle_control_request(payload, peer_id)),
        )

    def _handle_control_request(self, payload: dict, peer_id: str | None) -> None:
        """Prompt before granting remote mouse/keyboard access."""
        requested_by = payload.get("requested_by", "Remote user")
        NotificationManager.get_instance().show_info(
            f"{requested_by} requested control access.",
            title="Remote Control",
        )
        if peer_id is None:
            return

        granted = messagebox.askyesno(
            "Remote Control Request",
            f"Allow {requested_by} to control this device?\n\n"
            "They will be able to use mouse and keyboard input until you disconnect.",
        )
        self.connection_manager.respond_to_control_request(peer_id, granted, requested_by=requested_by)

    def _connect_to_device(self, host: str, port: int) -> bool:
        """Connect to a remote host from the connection page."""
        connected = self.connection_manager.connect_to_host(host, port)
        if connected and self._navigation_manager:
            self._navigation_manager.show_page("screen")
        return connected

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

    def _on_theme_change(self, theme_name: str) -> None:
        if hasattr(self, "content_frame"):
            self.content_frame.configure(
                fg_color=self._theme_manager.get_color("background", "#0D0D0D")
            )

    def send_chat_message(self, content: str) -> None:
        """Send a chat message through the app controller.

        Falls back to local display if chat networking is not available yet.
        """
        if self._chat_page is None:
            return

        try:
            if self.connection_manager.has_active_session():
                self.connection_manager.send_chat_message(
                    content=content,
                    sender=self.username,
                    sender_id=self.connection_manager.client_id,
                )
                self._chat_page.receive_network_message(
                    {
                        "sender": self.username,
                        "sender_id": self.connection_manager.client_id,
                        "content": content,
                        "message_type": "text",
                        "metadata": {},
                    }
                )
                return
        except Exception:
            pass

        # Local fallback display
        if self._chat_page is not None:
            self._chat_page.receive_network_message(
                {
                    "sender": self.username,
                    "sender_id": self.connection_manager.client_id,
                    "content": content,
                    "message_type": "text",
                    "metadata": {},
                }
            )

    def run(self) -> None:
        """Start the application main loop."""
        self._is_running = True
        self.mainloop()
        self._is_running = False
        self.connection_manager.disconnect_all()
        self._theme_manager.unregister_theme_change_callback(self._on_theme_change)


def create_main_window(config_manager) -> MainWindow:
    """Factory function to create the main application window."""
    return MainWindow(config_manager)
