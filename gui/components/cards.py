"""
===============================================================================
RemoteDesk Pro
File: gui/components/cards.py

Reusable card widgets.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk


class BaseCard(ctk.CTkFrame):
    """Generic card container."""

    def __init__(
        self,
        master,
        width: int | None = None,
        height: int | None = None,
        corner_radius: int = 12,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=1,
            **kwargs,
        )


class PageCard(BaseCard):
    """Card for grouping page content."""
    pass


class StatusCard(BaseCard):
    """Dashboard status card."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "--",
        subtitle: str = "",
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            anchor="w",
            font=("Inter", 13, "bold"),
        )
        self.title_label.pack(fill="x", padx=16, pady=(14, 4))

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            anchor="w",
            font=("Inter", 28, "bold"),
        )
        self.value_label.pack(fill="x", padx=16)

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            anchor="w",
            font=("Inter", 11),
        )
        self.subtitle_label.pack(fill="x", padx=16, pady=(4, 14))

    def update_value(self, value: str) -> None:
        self.value_label.configure(text=value)

    def update_subtitle(self, text: str) -> None:
        self.subtitle_label.configure(text=text)


class InfoCard(BaseCard):
    """Title/content information card."""

    def __init__(self, master, title: str, content: str, **kwargs) -> None:
        super().__init__(master, **kwargs)

        ctk.CTkLabel(
            self,
            text=title,
            anchor="w",
            font=("Inter", 15, "bold"),
        ).pack(fill="x", padx=16, pady=(14, 6))

        self.content = ctk.CTkLabel(
            self,
            text=content,
            justify="left",
            anchor="nw",
            wraplength=500,
            font=("Inter", 12),
        )
        self.content.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def set_text(self, text: str) -> None:
        self.content.configure(text=text)
