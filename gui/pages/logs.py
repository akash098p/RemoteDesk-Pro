"""
==============================================================================
RemoteDesk Pro
File: gui/pages/logs.py

Application log viewer page.
==============================================================================
"""

from __future__ import annotations

import customtkinter as ctk
from typing import Optional
from tkinter import END

from core.constants import LOG_FILE
from core.logger import get_logger
from gui.components.buttons import PrimaryButton, SecondaryButton
from gui.components.cards import PageCard
from gui.components.widgets import PageHeader

logger = get_logger()


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
            text=str(LOG_FILE),
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

        # Initial load
        self.refresh_logs()

    def refresh_logs(self) -> None:
        """Load the application log into the viewer."""
        self.textbox.delete("1.0", END)

        try:
            if not LOG_FILE.exists():
                self.textbox.insert(END, "Log file not found.\nStart the application to generate logs.")
                return

            content = LOG_FILE.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            logger.error(f"Failed to read log file: {exc}")
            content = f"Unable to read log file:\n\n{exc}"

        self.textbox.insert("1.0", content)

    def clear_view(self) -> None:
        """Clear only the viewer contents."""
        self.textbox.delete("1.0", END)
