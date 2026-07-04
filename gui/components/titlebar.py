"""
===============================================================================
RemoteDesk Pro
File: gui/components/titlebar.py

Custom application title bar for RemoteDesk Pro.
===============================================================================
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class TitleBar(ctk.CTkFrame):
    """Reusable custom title bar."""

    def __init__(
        self,
        master,
        title: str = "RemoteDesk Pro",
        on_minimize: Callable[[], None] | None = None,
        on_maximize: Callable[[], None] | None = None,
        on_close: Callable[[], None] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master, height=42, corner_radius=0, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        self._drag_x = 0
        self._drag_y = 0

        self.logo = ctk.CTkLabel(
            self,
            text="🖥",
            width=32,
            font=("Inter", 18),
        )
        self.logo.grid(row=0, column=0, padx=(10, 4), pady=5)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            anchor="w",
            font=("Inter", 14, "bold"),
        )
        self.title_label.grid(
            row=0,
            column=1,
            sticky="w",
            pady=5,
        )

        self.minimize_btn = ctk.CTkButton(
            self,
            text="—",
            width=36,
            height=28,
            command=on_minimize,
        )
        self.minimize_btn.grid(row=0, column=2, padx=(0, 4), pady=6)

        self.maximize_btn = ctk.CTkButton(
            self,
            text="□",
            width=36,
            height=28,
            command=on_maximize,
        )
        self.maximize_btn.grid(row=0, column=3, padx=(0, 4), pady=6)

        self.close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=36,
            height=28,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=on_close,
        )
        self.close_btn.grid(row=0, column=4, padx=(0, 8), pady=6)

        for widget in (self, self.title_label, self.logo):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._move_window)

    def set_title(self, text: str) -> None:
        """Update the displayed title."""
        self.title_label.configure(text=text)

    def _start_move(self, event) -> None:
        self._drag_x = event.x_root
        self._drag_y = event.y_root

    def _move_window(self, event) -> None:
        window = self.winfo_toplevel()
        dx = event.x_root - self._drag_x
        dy = event.y_root - self._drag_y
        x = window.winfo_x() + dx
        y = window.winfo_y() + dy
        window.geometry(f"+{x}+{y}")
        self._drag_x = event.x_root
        self._drag_y = event.y_root
