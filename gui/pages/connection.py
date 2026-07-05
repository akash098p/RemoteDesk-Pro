"""
===============================================================================
RemoteDesk Pro
File: gui/pages/connection.py
Connection page for initiating and managing remote connections.
===============================================================================
"""

from __future__ import annotations

import customtkinter
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()

class ConnectionPage(customtkinter.CTkFrame):
    """Page for connection setup and status."""
    
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self._theme = theme_manager
        
        # Create UI
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        # Header
        title_label = customtkinter.CTkLabel(
            self, text="Connection", font=customtkinter.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Connection status
        status_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", pady=10)
        
        status_label = customtkinter.CTkLabel(
            status_frame, text="Status: Disconnected",
            font=customtkinter.CTkFont(size=14, weight="bold")
        )
        status_label.pack(side="left", padx=(0, 10))
        
        # Connection controls
        control_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", pady=10)
        
        # IP input
        ip_label = customtkinter.CTkLabel(
            control_frame, text="Remote IP/ID:",
            font=customtkinter.CTkFont(size=14)
        )
        ip_label.pack(side="left", padx=(0, 10))
        
        self.ip_entry = customtkinter.CTkEntry(control_frame)
        self.ip_entry.pack(side="left", fill="x", expand=True)
        
        # Connect button
        connect_btn = customtkinter.CTkButton(
            control_frame,
            text="Connect",
            command=self._on_connect
        )
        connect_btn.pack(side="left", padx=(10, 0))
        
        # Terminal section (placeholder)
        terminal_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        terminal_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.terminal = customtkinter.CTkTextbox(terminal_frame)
        self.terminal.pack(fill="both", expand=True)
        
    def _on_connect(self) -> None:
        """Placeholder for connection logic (Phase 3 will implement actual networking)"""
        self.terminal.insert("end", "Connection initiated...\n")
        # Would connect to the provided IP in Phase 3