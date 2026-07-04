"""
===============================================================================
RemoteDesk Pro
File: gui/components/widgets.py

Reusable widgets for RemoteDesk Pro.
===============================================================================
"""

from __future__ import annotations

import customtkinter as ctk


class PageHeader(ctk.CTkFrame):
    """Reusable page header."""

    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Inter", 24, "bold"),
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=("Inter", 12),
            anchor="w",
        )
        self.subtitle_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0),
        )

    def set_title(self, text: str) -> None:
        self.title_label.configure(text=text)

    def set_subtitle(self, text: str) -> None:
        self.subtitle_label.configure(text=text)


class LabeledEntry(ctk.CTkFrame):
    """Entry widget with label."""

    def __init__(
        self,
        master,
        label: str,
        placeholder: str = "",
        show: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=label,
            anchor="w",
            font=("Inter", 12, "bold"),
        )
        self.label.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 6),
        )

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            show=show,
        )
        self.entry.grid(
            row=1,
            column=0,
            sticky="ew",
        )

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def clear(self) -> None:
        self.entry.delete(0, "end")


class LabeledTextbox(ctk.CTkFrame):
    """Textbox widget with label."""

    def __init__(
        self,
        master,
        label: str,
        height: int = 150,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text=label,
            anchor="w",
            font=("Inter", 12, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 6),
        )

        self.textbox = ctk.CTkTextbox(
            self,
            height=height,
        )
        self.textbox.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

    def get(self) -> str:
        return self.textbox.get("1.0", "end").strip()

    def set(self, text: str) -> None:
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

    def clear(self) -> None:
        self.textbox.delete("1.0", "end")


class Separator(ctk.CTkFrame):
    """Simple horizontal separator."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            height=1,
            corner_radius=0,
            **kwargs,
        )
