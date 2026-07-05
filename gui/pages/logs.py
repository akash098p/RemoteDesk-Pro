"""
===============================================================================
RemoteDesk Pro
File: gui/pages/logs.py

Application log viewer page.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from core.constants import APPLICATION_LOG_FILE
from gui.components.buttons import PrimaryButton, SecondaryButton
from gui.components.cards import PageCard
from gui.components.widgets import PageHeader


class LogsPage(ctk.CTkFrame):
    """Application log viewer."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = PageHeader(
            self,
            title="Logs",
            subtitle="View application log output",
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        card = PageCard(self)
        card.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(card, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        PrimaryButton(
            toolbar,
            text="Refresh",
            command=self.refresh_logs,
            width=110,
        ).pack(side="left", padx=(0, 8))

        SecondaryButton(
            toolbar,
            text="Clear View",
            command=self.clear_view,
            width=110,
        ).pack(side="left")

        self.path_label = ctk.CTkLabel(
            toolbar,
            text=str(APPLICATION_LOG_FILE),
            anchor="e",
            font=("Inter", 11),
        )
        self.path_label.pack(side="right")

        self.textbox = ctk.CTkTextbox(
            card,
            wrap="word",
            font=("Consolas", 12),
        )
        self.textbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(0, 16),
        )

        self.refresh_logs()

    def refresh_logs(self) -> None:
        """Load the application log into the viewer."""
        self.textbox.delete("1.0", "end")

        if not APPLICATION_LOG_FILE.exists():
            self.textbox.insert(
                "end",
                "Log file not found.\nStart the application to generate logs.",
            )
            return

        try:
            content = APPLICATION_LOG_FILE.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError as exc:
            content = f"Unable to read log file:\n\n{exc}"

        self.textbox.insert("1.0", content)

    def clear_view(self) -> None:
        """Clear only the viewer contents."""
        self.textbox.delete("1.0", "end")
"""
===============================================================================
RemoteDesk Pro
File: gui/pages/logs.py
Logs page displaying application, connection, and transfer logs.
===============================================================================
"""

from __future__ import annotations

import customtkinter
import tkinter.scrolledtext as scrolledtext
from core.config_manager import get_config_manager

config_manager = get_config_manager()

class LogsPage(customtkinter.CTkFrame):
    """Page displaying system and application logs."""
    
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        
        # Create UI
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        # Header
        title_label = customtkinter.CTkLabel(
            self, text="Logs", font=customtkinter.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Log display area
        self.log_area = scrolledtext.ScrolledText(
            self,
            wrap=tkinter.WORD,
            font=customtkinter.CTkFont(family="Inter", size=12)
        )
        self.log_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Filter section
        filter_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        filter_label = customtkinter.CTkLabel(
            filter_frame, text="Filter by level:",
            font=customtkinter.CTkFont(size=14)
        )
        filter_label.pack(side="left", padx=(0, 10))
        
        self.filter_var = customtkinter.StringVar(value="INFO")
        filter_menu = customtkinter.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        filter_menu.pack(side="left")
        
        # Clear button
        clear_btn = customtkinter.CTkButton(
            self,
            text="Clear Logs",
            command=self._clear_logs
        )
        clear_btn.pack(pady=10)
        
    def _clear_logs(self) -> None:
        self.log_area.delete("1.0", "end")
        
    def _update_logs(self, new_logs: str) -> None:
        """Placeholder to update logs from logging system"""
        self.log_area.insert("end", new_logs + "\n")
        self.log_area.see("end")