"""
===============================================================================
RemoteDesk Pro
File: gui/pages/settings.py

Application settings page.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from gui.components.buttons import PrimaryButton
from gui.components.cards import PageCard
from gui.components.widgets import LabeledEntry, PageHeader


class SettingsPage(ctk.CTkFrame):
    """Application settings page."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = PageHeader(
            self,
            title="Settings",
            subtitle="Manage application preferences",
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        card = PageCard(self)
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)

        self.username = LabeledEntry(
            card,
            label="Display Name",
            placeholder="Enter your display name",
        )
        self.username.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))

        self.device = LabeledEntry(
            card,
            label="Device Name",
            placeholder="Enter device name",
        )
        self.device.grid(row=1, column=0, sticky="ew", padx=20, pady=12)

        self.theme = ctk.CTkOptionMenu(
            card,
            values=["dark", "light", "dracula", "nord", "amoled"],
        )
        self.theme.grid(row=2, column=0, sticky="ew", padx=20, pady=12)

        self.save_button = PrimaryButton(
            card,
            text="Save Settings",
            command=self.save_settings,
        )
        self.save_button.grid(row=3, column=0, sticky="e", padx=20, pady=20)

        self.status = ctk.CTkLabel(
            card,
            text="",
            anchor="w",
            font=("Inter", 11),
        )
        self.status.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

    def save_settings(self) -> None:
        """Placeholder save hook for integration with ConfigManager."""
        self.status.configure(text="Settings saved successfully.")

    def load_settings(
        self,
        display_name: str = "",
        device_name: str = "",
        theme: str = "dark",
    ) -> None:
        """Populate the form."""
        self.username.set(display_name)
        self.device.set(device_name)
        self.theme.set(theme)
