"""
===============================================================================
RemoteDesk Pro
File: gui/pages/dashboard.py

Professional dashboard page.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from core.constants import APP_NAME, APP_VERSION
from gui.components.cards import InfoCard, StatusCard
from gui.components.widgets import PageHeader


class DashboardPage(ctk.CTkFrame):
    """Main dashboard page."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header = PageHeader(
            self,
            title="Dashboard",
            subtitle="Welcome to RemoteDesk Pro",
        )
        self.header.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        self.cpu_card = StatusCard(
            self,
            title="CPU Usage",
            value="0%",
            subtitle="Live system monitor",
        )
        self.cpu_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(20, 10),
            pady=10,
        )

        self.ram_card = StatusCard(
            self,
            title="RAM Usage",
            value="0%",
            subtitle="Live memory monitor",
        )
        self.ram_card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(10, 20),
            pady=10,
        )

        self.info_card = InfoCard(
            self,
            title="Application",
            content=(
                f"{APP_NAME}\n"
                f"Version: {APP_VERSION}\n\n"
                "Phase 2 desktop foundation initialized.\n"
                "Networking and remote collaboration modules "
                "will be integrated in later phases."
            ),
        )
        self.info_card.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=20,
            pady=(10, 20),
        )

    def update_cpu(self, value: str) -> None:
        """Update CPU usage display."""
        self.cpu_card.update_value(value)

    def update_ram(self, value: str) -> None:
        """Update RAM usage display."""
        self.ram_card.update_value(value)
