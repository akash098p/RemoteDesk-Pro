"""
===============================================================================
RemoteDesk Pro
File: gui/components/statusbar.py

Professional status bar component.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):
    """Application status bar."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, height=28, corner_radius=0, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            font=("Inter", 11),
        )
        self.status_label.grid(
            row=0,
            column=0,
            padx=(10, 5),
            pady=4,
            sticky="w",
        )

        self.info_label = ctk.CTkLabel(
            self,
            text="",
            anchor="center",
            font=("Inter", 11),
        )
        self.info_label.grid(
            row=0,
            column=1,
            padx=5,
            pady=4,
            sticky="ew",
        )

        self.version_label = ctk.CTkLabel(
            self,
            text="RemoteDesk Pro",
            anchor="e",
            font=("Inter", 11),
        )
        self.version_label.grid(
            row=0,
            column=2,
            padx=(5, 10),
            pady=4,
            sticky="e",
        )

    def set_status(self, text: str) -> None:
        """Update the main status message."""
        self.status_label.configure(text=text)

    def set_info(self, text: str) -> None:
        """Update the center information area."""
        self.info_label.configure(text=text)

    def set_version(self, version: str) -> None:
        """Update the version display."""
        self.version_label.configure(text=version)

    def clear_info(self) -> None:
        """Clear the center information."""
        self.info_label.configure(text="")

    def reset(self) -> None:
        """Reset the status bar to its default state."""
        self.status_label.configure(text="Ready")
        self.info_label.configure(text="")
