"""
=================================================================================
RemoteDesk Pro
File: gui/pages/dashboard.py
Modern dashboard with system stats, quick actions and premium glass UI
=================================================================================
"""

from __future__ import annotations

from typing import Callable
import os

import customtkinter as ctk
from PIL import Image
import time

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger
from core.utils import get_cpu_usage, get_ram_usage

logger = get_logger()

# Get the assets directory path
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons')


def load_icon(icon_name: str, size: tuple = (24, 24)) -> Image.Image:
    """Load an icon from the assets directory."""
    icon_path = os.path.join(ASSETS_DIR, icon_name)
    if os.path.exists(icon_path):
        return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
    return None  # Return None if icon not found


class DashboardPage(ctk.CTkFrame):
    """
    Premium dashboard page – system stats, quick actions and status overview.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._last_update = time.time()
        self._cpu_usage = 0
        self._ram_usage = 0
        # Get theme manager from parent
        self._theme_manager = parent._theme_manager if hasattr(parent, '_theme_manager') else None
        self._initialize_ui()
        # Start system status updates
        self.after(0, self._update_system_status)

    def _initialize_ui(self):
        """Create the premium dashboard layout"""
        # Main background with glass effect
        self._set_appearance_mode("dark")
        self._set_appearance_mode("system")

        # Title section
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(0, 5))

        title_label = ctk.CTkLabel(
            title_frame,
            text="RemoteDesk Pro",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        title_label.pack(padx=20, pady=(0, 5))

        # Stats container (using pack instead of grid)
        stats_container = ctk.CTkFrame(self, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=10)

        # CPU Card
        cpu_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        cpu_frame.pack(side="left", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            cpu_frame,
            text="CPU Usage",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CCCCCC"
        ).pack(pady=(10, 5))

        self.cpu_value = ctk.CTkLabel(
            cpu_frame,
            text="0%",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#00C0FF"
        )
        self.cpu_value.pack()

        # RAM Card
        ram_frame = ctk.CTkFrame(stats_container, fg_color="transparent")
        ram_frame.pack(side="left", fill="x", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            ram_frame,
            text="RAM Usage",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#A0A0A0", "#FFFFFF")
        ).pack(pady=(10, 5))

        self.ram_value = ctk.CTkLabel(
            ram_frame,
            text="0%",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#4CAF50"
        )
        self.ram_value.pack()

        # Quick Actions Section
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(20, 10))

        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#A0A0A0"
        ).pack(anchor="w", pady=(10, 5))

        # Quick action buttons with glass effect and icons
        actions = [
            ("monitor.png", "Start Sharing", self._start_sharing),
            ("plug-zap.png", "Remote Control", self._start_remote_control),
            ("folder.png", "File Transfer", self._open_files),
            ("settings.png", "Settings", self._open_settings),
            ("info.png", "About", self._show_about)
        ]

        # Container for buttons (inside actions_frame)
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=5)

        for icon_file, text, command in actions:
            # Load and create the icon image
            icon_image = load_icon(icon_file, size=(20, 20))
            if icon_image:
                ctk_icon = ctk.CTkImage(light_image=icon_image, dark_image=icon_image, size=(20, 20))
                btn = ctk.CTkButton(
                    buttons_frame,
                    image=ctk_icon,
                    text=text,
                    compound="left",
                    width=150,
                    height=45,
                    corner_radius=12,
                    fg_color=("#4A90E2", "#2E3A47"),
                )
            else:
                # Fallback to text-only button if icon not found
                btn = ctk.CTkButton(
                    buttons_frame,
                    text=text,
                    width=150,
                    height=45,
                    corner_radius=12,
                    fg_color=("#4A90E2", "#2E3A47"),
                )
            btn.pack(side="left", padx=10, pady=5)
            # Store command reference
            if not hasattr(self, f"_btn_{text.strip()}"):
                setattr(self, f"_btn_{text.strip()}", [])

    def _start_sharing(self):
        """Start screen sharing session"""
        # Would normally call connection manager to start sharing
        logger.info("Starting screen sharing")
        # Placeholder – integrate with actual connection manager

    def _start_remote_control(self):
        """Initiate remote control session"""
        logger.info("Starting remote control")
        # Would open remote control UI

    def _open_files(self):
        """Open file transfer page"""
        if self.master._navigation_manager:
            self.master._navigation_manager.show_page("files")

    def _open_settings(self):
        """Open settings page"""
        if self.master._navigation_manager:
            self.master._navigation_manager.show_page("settings")

    def _show_about(self):
        """Open about page"""
        if self.master._navigation_manager:
            self.master._navigation_manager.show_page("about")

    def _update_system_status(self):
        """Periodically update CPU and RAM usage stats"""
        cpu = get_cpu_usage()
        ram = get_ram_usage()
        self.cpu_value.configure(text=f"{cpu:.1f}%")
        self.ram_value.configure(text=f"{ram[0]:.1f}%")

        # Schedule next update
        self.after(1000, self._update_system_status)

    def _create_widgets(self):
        """Initial UI setup – split into logical sections"""
        # Title area already created in __init__
        # Stats grid already created
        # Quick actions already added

        # Footer/status line
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=(0, 20))

        status_label = ctk.CTkLabel(
            self,
            text="Ready to share your screen",
            font=ctk.CTkFont(size=14),
            text_color="#A0A0A0"
        )
        status_label.pack(side="left", padx=20)

        # Add a small status icon label
        status_icon = ctk.CTkLabel(
            self,
            text="💻",
            font=ctk.CTkFont(size=16)
        )
        status_icon.pack(side="right", padx=(20, 0))