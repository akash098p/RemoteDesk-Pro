"""
===============================================================================
RemoteDesk Pro
File: gui/main_window.py

Main application window.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from core.constants import (
    APP_NAME,
    APP_VERSION,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    SIDEBAR_COLLAPSED_WIDTH,
    SIDEBAR_WIDTH,
    STATUSBAR_HEIGHT,
    TOOLBAR_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from gui.components.notifications import NotificationManager
from gui.components.sidebar import Sidebar
from gui.components.statusbar import StatusBar
from gui.components.titlebar import TitleBar


class MainWindow(ctk.CTk):
    """Main application shell."""

    def __init__(self) -> None:
        super().__init__()

        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.titlebar = TitleBar(
            self,
            title=f"{APP_NAME} {APP_VERSION}",
            on_minimize=self.iconify,
            on_maximize=self._toggle_zoom,
            on_close=self.destroy,
            height=TOOLBAR_HEIGHT,
        )
        self.titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_page,
            expanded_width=SIDEBAR_WIDTH,
            collapsed_width=SIDEBAR_COLLAPSED_WIDTH,
        )
        self.sidebar.grid(row=1, column=0, rowspan=2, sticky="nsw")

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages: dict[str, ctk.CTkFrame] = {}

        self.statusbar = StatusBar(self, height=STATUSBAR_HEIGHT)
        self.statusbar.set_version(f"v{APP_VERSION}")
        self.statusbar.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.notifications = NotificationManager(self)

        self._create_placeholder_pages()
        self.show_page("dashboard")

    def _create_placeholder_pages(self) -> None:
        names = [
            "dashboard", "connection", "chat", "files",
            "screen", "audio", "clipboard",
            "settings", "logs", "about",
        ]
        for name in names:
            frame = ctk.CTkFrame(self.content)
            frame.grid(row=0, column=0, sticky="nsew")
            ctk.CTkLabel(
                frame,
                text=name.title(),
                font=("Inter", 28, "bold"),
            ).pack(expand=True)
            self.pages[name] = frame

    def show_page(self, name: str) -> None:
        page = self.pages.get(name)
        if page:
            page.tkraise()
            self.sidebar.set_active(name)
            self.statusbar.set_status(f"{name.title()} page")
            self.notifications.show(f"Opened {name.title()}", "info", 1500)

    def toggle_sidebar(self) -> None:
        self.sidebar.toggle()

    def _toggle_zoom(self) -> None:
        try:
            self.state("zoomed" if self.state() != "zoomed" else "normal")
        except Exception:
            pass


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
