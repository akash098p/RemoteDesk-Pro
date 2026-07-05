"""
===============================================================================
RemoteDesk Pro
File: gui/pages/dashboard.py

Dashboard page showing overview information, system status, and quick actions.
===============================================================================
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import customtkinter

from core.constants import FONT_SIZE_HEADER, FONT_SIZE_BODY
from core.theme_manager import get_theme_manager
from core.utils import get_cpu_usage, get_ram_usage

if TYPE_CHECKING:
    from gui.main_window import MainWindow


class DashboardPage(customtkinter.CTkFrame):
    """
    Main dashboard page for RemoteDesk Pro.
    Displays system information, quick actions, and application status.
    """

    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self._theme_manager = get_theme_manager()

        # Create UI
        self._create_widgets()
        self._start_updates()

    def _create_widgets(self) -> None:
        """Create the dashboard layout."""
        # Main container with padding
        container = customtkinter.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = customtkinter.CTkLabel(
            container,
            text="Dashboard",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_HEADER, weight="bold"),
            text_color=self._theme_manager.get_color("text_primary", "#FFFFFF"),
            anchor="w",
        )
        title_label.pack(fill="x", pady=(0, 20))

        # System status cards row
        status_row = customtkinter.CTkFrame(container, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 20))

        # CPU Card
        self.cpu_card = customtkinter.CTkFrame(
            status_row,
            fg_color=self._theme_manager.get_color("card_bg", "#252525"),
            corner_radius=10,
        )
        self.cpu_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cpu_title = customtkinter.CTkLabel(
            self.cpu_card,
            text="CPU Usage",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=self._theme_manager.get_color("text_secondary", "#A0A0A0"),
        )
        cpu_title.pack(pady=(15, 5))

        self.cpu_value = customtkinter.CTkLabel(
            self.cpu_card,
            text="0%",
            font=customtkinter.CTkFont(family="Inter", size=36, weight="bold"),
            text_color=self._theme_manager.get_color("primary", "#0084FF"),
        )
        self.cpu_value.pack(pady=(5, 15))

        # RAM Card
        self.ram_card = customtkinter.CTkFrame(
            status_row,
            fg_color=self._theme_manager.get_color("card_bg", "#252525"),
            corner_radius=10,
        )
        self.ram_card.pack(side="left", fill="both", expand=True, padx=(10, 0))

        ram_title = customtkinter.CTkLabel(
            self.ram_card,
            text="RAM Usage",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=self._theme_manager.get_color("text_secondary", "#A0A0A0"),
        )
        ram_title.pack(pady=(15, 5))

        self.ram_value = customtkinter.CTkLabel(
            self.ram_card,
            text="0%",
            font=customtkinter.CTkFont(family="Inter", size=36, weight="bold"),
            text_color=self._theme_manager.get_color("primary", "#0084FF"),
        )
        self.ram_value.pack(pady=(5, 15))

        # Quick Actions Section
        actions_label = customtkinter.CTkLabel(
            container,
            text="Quick Actions",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_HEADER, weight="bold"),
            text_color=self._theme_manager.get_color("text_primary", "#FFFFFF"),
            anchor="w",
        )
        actions_label.pack(fill="x", pady=(20, 15))

        # Action buttons
        actions_frame = customtkinter.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 20))

        connect_btn = customtkinter.CTkButton(
            actions_frame,
            text="New Connection",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            width=150,
            height=40,
            command=self._on_connect,
        )
        connect_btn.pack(side="left", padx=(0, 10))

        settings_btn = customtkinter.CTkButton(
            actions_frame,
            text="Settings",
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            width=150,
            height=40,
            command=self._on_settings,
        )
        settings_btn.pack(side="left", padx=(10, 0))

    def _start_updates(self) -> None:
        """Start periodic system status updates."""
        self._update_system_status()

    def _update_system_status(self) -> None:
        """Update CPU and RAM usage displays."""
        cpu = get_cpu_usage()
        ram = get_ram_usage()

        self.cpu_value.configure(text=f"{cpu:.1f}%")
        self.ram_value.configure(text=f"{ram[0]:.1f}%")

        # Schedule next update
        self.after(1000, self._update_system_status)

    def _on_connect(self) -> None:
        """Handle connect button click."""
        if self.parent._navigation_manager:
            self.parent._navigation_manager.show_page("connection")

    def _on_settings(self) -> None:
        """Handle settings button click."""
        if self.parent._navigation_manager:
            self.parent._navigation_manager.show_page("settings")

    def destroy(self) -> None:
        """Clean up resources."""
        super().destroy()