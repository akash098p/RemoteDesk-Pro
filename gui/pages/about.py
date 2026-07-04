"""
===============================================================================
RemoteDesk Pro
File: gui/pages/about.py

About page for RemoteDesk Pro.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from core.constants import (
    APP_AUTHOR,
    APP_COPYRIGHT,
    APP_DESCRIPTION,
    APP_LICENSE,
    APP_NAME,
    APP_REPOSITORY,
    APP_VERSION,
)
from gui.components.cards import InfoCard
from gui.components.widgets import PageHeader


class AboutPage(ctk.CTkFrame):
    """Displays application information."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = PageHeader(
            self,
            title="About",
            subtitle="Application information",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        content = (
            f"Application : {APP_NAME}\n"
            f"Version     : {APP_VERSION}\n"
            f"Author      : {APP_AUTHOR}\n"
            f"License     : {APP_LICENSE}\n\n"
            f"{APP_DESCRIPTION}\n\n"
            f"Repository:\n{APP_REPOSITORY}\n\n"
            f"{APP_COPYRIGHT}"
        )

        card = InfoCard(
            self,
            title="RemoteDesk Pro",
            content=content,
        )
        card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(0, 20),
        )

        footer = ctk.CTkLabel(
            self,
            text="Thank you for using RemoteDesk Pro.",
            font=("Inter", 12),
        )
        footer.grid(
            row=2,
            column=0,
            pady=(0, 20),
        )
