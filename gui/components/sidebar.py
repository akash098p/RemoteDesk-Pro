"""
===============================================================================
RemoteDesk Pro
File: gui/components/sidebar.py

Reusable collapsible sidebar component.
===============================================================================
"""
from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from gui.components.buttons import SidebarButton


class Sidebar(ctk.CTkFrame):
    """Collapsible navigation sidebar."""

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None] | None = None,
        expanded_width: int = 250,
        collapsed_width: int = 70,
        **kwargs,
    ) -> None:
        super().__init__(master, corner_radius=0, **kwargs)

        self._expanded_width = expanded_width
        self._collapsed_width = collapsed_width
        self._expanded = True
        self._callback = on_navigate

        self.configure(width=self._expanded_width)

        self.grid_rowconfigure(99, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text="RemoteDesk Pro",
            font=("Inter", 18, "bold"),
            anchor="w",
        )
        self.title.grid(row=0, column=0, sticky="ew", padx=12, pady=(14, 20))

        self._buttons: dict[str, SidebarButton] = {}
        self._button_text: dict[str, str] = {}

        items = [
            ("dashboard", "Dashboard"),
            ("connection", "Connection"),
            ("chat", "Chat"),
            ("files", "Files"),
            ("screen", "Screen"),
            ("audio", "Audio"),
            ("clipboard", "Clipboard"),
            ("settings", "Settings"),
            ("logs", "Logs"),
            ("about", "About"),
        ]

        for row, (key, text) in enumerate(items, start=1):
            btn = SidebarButton(
                self,
                text=text,
                command=lambda k=key: self.navigate(k),
            )
            btn.grid(row=row, column=0, sticky="ew", padx=8, pady=3)
            self._buttons[key] = btn
            self._button_text[key] = text

        self.active_page: str | None = None

    def navigate(self, page: str) -> None:
        """Navigate to a page."""
        self.set_active(page)
        if self._callback:
            self._callback(page)

    def set_active(self, page: str) -> None:
        """Highlight the active page."""
        self.active_page = page
        for key, button in self._buttons.items():
            if key == page:
                button.configure(fg_color="#2563EB", text_color="white")
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=("black", "white"),
                )

    def toggle(self) -> None:
        """Toggle expanded/collapsed mode."""
        self._expanded = not self._expanded

        self.configure(
            width=self._expanded_width
            if self._expanded
            else self._collapsed_width
        )

        self.title.configure(
            text="RemoteDesk Pro" if self._expanded else "RDP"
        )

        for key, button in self._buttons.items():
            button.configure(
                text=self._button_text[key] if self._expanded else ""
            )

    @property
    def expanded(self) -> bool:
        """Return True if the sidebar is expanded."""
        return self._expanded
