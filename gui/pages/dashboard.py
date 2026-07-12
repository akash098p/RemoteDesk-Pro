"""
=================================================================================
RemoteDesk Pro
File: gui/pages/dashboard.py
Dashboard page with system stats, quick actions, and session overview.
=================================================================================
"""

from __future__ import annotations

import os
from typing import Optional

import customtkinter as ctk
from PIL import Image

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger
from core.utils import get_cpu_usage, get_ram_usage

logger = get_logger()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")


def load_icon(icon_name: str, size: tuple = (24, 24)) -> Optional[Image.Image]:
    """Load an icon from the assets directory."""
    icon_path = os.path.join(ASSETS_DIR, icon_name)
    if os.path.exists(icon_path):
        return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
    return None


class DashboardPage(ctk.CTkFrame):
    """Dashboard page for status, actions, and system overview."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._cpu_usage = 0.0
        self._ram_usage = 0.0
        self._action_icons: list[ctk.CTkImage] = []
        self._build_ui()
        self.after(0, self._update_system_status)

    @property
    def _connection_manager(self):
        return getattr(self.master, "_connection_manager", None)

    def _build_ui(self) -> None:
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=18, pady=(12, 10))

        hero = ctk.CTkFrame(self.scroll_frame, fg_color=("#F4F7FB", "#1D232B"), corner_radius=18)
        hero.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            hero,
            text="RemoteDesk Pro",
            font=ctk.CTkFont(size=32, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(22, 4))

        ctk.CTkLabel(
            hero,
            text="Share your screen, connect to devices, and keep remote sessions under control from one place.",
            font=ctk.CTkFont(size=13),
            text_color=("#5B6574", "#AEB8C5"),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 14))

        summary_row = ctk.CTkFrame(hero, fg_color="transparent")
        summary_row.pack(fill="x", padx=24, pady=(0, 20))
        for col in range(3):
            summary_row.grid_columnconfigure(col, weight=1)

        self.session_value = self._create_summary_card(summary_row, 0, "Session", "Waiting for connection")
        self.quality_value = self._create_summary_card(summary_row, 1, "Streaming", f"{DEFAULT_FPS} FPS / {DEFAULT_QUALITY}% quality")
        self.network_value = self._create_summary_card(summary_row, 2, "Network", "Local hosting available")

        stats_row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 12))
        for col in range(2):
            stats_row.grid_columnconfigure(col, weight=1)

        self.cpu_value = self._create_metric_card(stats_row, 0, "CPU Usage", "0.0%", "#11B8FF")
        self.ram_value = self._create_metric_card(stats_row, 1, "RAM Usage", "0.0%", "#58C15D")

        actions_card = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        actions_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            actions_card,
            text="Quick Actions",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(18, 4))

        ctk.CTkLabel(
            actions_card,
            text="Jump straight into sharing, control, files, and settings without hunting through the sidebar.",
            font=ctk.CTkFont(size=12),
            text_color=("#5B6574", "#AEB8C5"),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 14))

        actions_grid = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_grid.pack(fill="x", padx=18, pady=(0, 18))
        for col in range(3):
            actions_grid.grid_columnconfigure(col, weight=1)

        actions = [
            ("monitor.png", "Start Sharing", "Open the screen page and begin broadcasting your desktop.", self._start_sharing),
            ("plug-zap.png", "Remote Control", "Move into a live session and request or grant control.", self._start_remote_control),
            ("folder.png", "File Transfer", "Go to the file tools area for sharing documents and images.", self._open_files),
            ("settings.png", "Settings", "Adjust theme, FPS, quality, and app preferences.", self._open_settings),
            ("info.png", "About", "View project details, creator info, and support links.", self._show_about),
            ("chat.png", "Open Chat", "Check messages and keep the conversation nearby during sessions.", self._open_chat),
        ]

        for index, (icon_file, title, description, command) in enumerate(actions):
            row = index // 3
            col = index % 3
            self._create_action_card(actions_grid, row, col, icon_file, title, description, command)

        tips_card = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        tips_card.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            tips_card,
            text="Ready Checklist",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(18, 10))

        for text in [
            "Open Connection to confirm your LAN IP or create a public link before inviting another device.",
            "Use Screen after connecting to start video sharing and remote control features.",
            "Keep Chat open during a session if you want fast two-way messaging alongside screen sharing.",
        ]:
            ctk.CTkLabel(
                tips_card,
                text=f"- {text}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                justify="left",
                wraplength=920,
            ).pack(fill="x", padx=22, pady=4)

        self.footer_status = ctk.CTkLabel(
            tips_card,
            text="Ready to share your screen.",
            font=ctk.CTkFont(size=12),
            text_color=("#5B6574", "#AEB8C5"),
        )
        self.footer_status.pack(anchor="w", padx=22, pady=(10, 18))

    def _create_summary_card(self, parent, column: int, title: str, value: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color=("white", "#14191F"), corner_radius=14)
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#667085", "#93A0B0"),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="left",
            anchor="w",
        )
        value_label.pack(fill="x", padx=16, pady=(0, 14))
        return value_label

    def _create_metric_card(self, parent, column: int, title: str, value: str, accent: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=4)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#667085", "#93A0B0"),
        ).pack(anchor="w", padx=20, pady=(18, 10))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=accent,
        )
        value_label.pack(anchor="w", padx=20, pady=(0, 18))
        return value_label

    def _create_action_card(
        self,
        parent,
        row: int,
        column: int,
        icon_file: str,
        title: str,
        description: str,
        command,
    ) -> None:
        card = ctk.CTkFrame(parent, fg_color=("white", "#14191F"), corner_radius=16)
        card.grid(row=row, column=column, sticky="nsew", padx=6, pady=6)

        button_icon = None
        icon_image = load_icon(icon_file, size=(20, 20))
        if icon_image is not None:
            button_icon = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(20, 20))
            self._action_icons.append(button_icon)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(18, 6))

        ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=("#5B6574", "#AEB8C5"),
            justify="left",
            wraplength=240,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 14))

        ctk.CTkButton(
            card,
            text=title,
            image=button_icon,
            compound="left",
            height=40,
            corner_radius=12,
            command=command,
            fg_color=("#2F7DDA", "#243E5B"),
            hover_color=("#276BBB", "#2C5073"),
        ).pack(fill="x", padx=18, pady=(0, 18))

    def _start_sharing(self):
        logger.info("Starting screen sharing")
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("screen")

    def _start_remote_control(self):
        logger.info("Starting remote control")
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("screen")

    def _open_chat(self):
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("chat")

    def _open_files(self):
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("files")

    def _open_settings(self):
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("settings")

    def _show_about(self):
        if getattr(self.master, "_navigation_manager", None):
            self.master._navigation_manager.show_page("about")

    def _update_system_status(self):
        cpu = get_cpu_usage()
        ram = get_ram_usage()
        self._cpu_usage = cpu
        self._ram_usage = ram[0]
        self.cpu_value.configure(text=f"{cpu:.1f}%")
        self.ram_value.configure(text=f"{ram[0]:.1f}%")

        manager = self._connection_manager
        if manager is not None:
            self.session_value.configure(text=manager.get_session_summary())
            self.network_value.configure(text=f"Host on {manager.get_local_ip()}:{manager.server_port}")
            self.footer_status.configure(text=manager.get_session_summary())
        self.after(1000, self._update_system_status)
