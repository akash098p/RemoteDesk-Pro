"""
===============================================================================
RemoteDesk Pro
File: gui/pages/clipboard.py

Clipboard page for viewing and managing local clipboard content.
Provides read/copy workflows and a placeholder for remote sync status.
===============================================================================
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

import customtkinter
from core.theme_manager import get_theme_manager
from core.config_manager import get_config_manager
from core.utils import load_image

try:
    import pyperclip
except ImportError:  # pragma: no cover
    pyperclip = None

theme_manager = get_theme_manager()
config_manager = get_config_manager()


class ClipboardPage(customtkinter.CTkFrame):
    """Page for local clipboard management and remote clipboard sync status."""

    def __init__(self, parent: "customtkinter.CTk") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self._clipboard_available = pyperclip is not None

        self._create_widgets()
        self._refresh_clipboard_contents()

    def _create_widgets(self) -> None:
        """Create the clipboard page layout."""
        title_label = customtkinter.CTkLabel(
            self,
            text="Clipboard",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            anchor="w",
        )
        title_label.pack(fill="x", padx=20, pady=(20, 10))

        subtitle = customtkinter.CTkLabel(
            self,
            text="View and sync clipboard content across connected devices.",
            font=customtkinter.CTkFont(size=12),
            text_color=theme_manager.get_color("text_secondary", "#A0A0A0"),
            anchor="w",
        )
        subtitle.pack(fill="x", padx=20, pady=(0, 15))

        control_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        control_frame.pack(fill="x", padx=20, pady=(0, 10))

        load_btn = customtkinter.CTkButton(
            control_frame,
            text="Refresh from System",
            command=self._refresh_clipboard_contents,
            width=170,
        )
        load_btn.pack(side="left", padx=(0, 8), pady=5)

        copy_btn = customtkinter.CTkButton(
            control_frame,
            text="Copy to System",
            command=self._copy_to_system,
            width=170,
        )
        copy_btn.pack(side="left", padx=(0, 8), pady=5)

        clear_btn = customtkinter.CTkButton(
            control_frame,
            text="Clear Clipboard",
            command=self._clear_clipboard,
            width=170,
        )
        clear_btn.pack(side="left", padx=(0, 8), pady=5)

        self.status_label = customtkinter.CTkLabel(
            self,
            text="Remote sync is not configured yet.",
            font=customtkinter.CTkFont(size=11),
            text_color=theme_manager.get_color("text_secondary", "#A0A0A0"),
            anchor="w",
        )
        self.status_label.pack(fill="x", padx=20, pady=(10, 10))

        self.clipboard_text = customtkinter.CTkTextbox(
            self,
            wrap="word",
            height=12,
            font=("Inter", 13),
            fg_color=theme_manager.get_color("surface", "#1A1A1A"),
            text_color=theme_manager.get_color("text_primary", "#FFFFFF"),
        )
        self.clipboard_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not self._clipboard_available:
            warning_label = customtkinter.CTkLabel(
                self,
                text="Install pyperclip to enable system clipboard access.",
                font=customtkinter.CTkFont(size=12),
                text_color="#FFB347",
                anchor="w",
            )
            warning_label.pack(fill="x", padx=20, pady=(0, 10))

    def _refresh_clipboard_contents(self) -> None:
        """Read the current system clipboard content and display it."""
        if self._clipboard_available:
            try:
                content = pyperclip.paste() or ""
            except Exception:
                content = "Unable to read system clipboard content."
        else:
            content = "System clipboard integration unavailable. Install pyperclip."

        self.clipboard_text.delete("1.0", tk.END)
        self.clipboard_text.insert(tk.END, content)

    def _copy_to_system(self) -> None:
        """Copy the current text box contents to the system clipboard."""
        text = self.clipboard_text.get("1.0", tk.END).strip()
        if not self._clipboard_available:
            self.status_label.configure(text="pyperclip is required to copy to system clipboard.")
            return

        try:
            pyperclip.copy(text)
            self.status_label.configure(text="Copied current content to system clipboard.")
        except Exception:
            self.status_label.configure(text="Failed to copy content to system clipboard.")

    def _clear_clipboard(self) -> None:
        """Clear the displayed clipboard content and update the system clipboard if available."""
        self.clipboard_text.delete("1.0", tk.END)
        if self._clipboard_available:
            try:
                pyperclip.copy("")
                self.status_label.configure(text="Clipboard cleared.")
            except Exception:
                self.status_label.configure(text="Failed to clear system clipboard.")
        else:
            self.status_label.configure(text="Cleared local text view.")
