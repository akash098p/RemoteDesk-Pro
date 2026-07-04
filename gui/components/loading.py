"""
===============================================================================
RemoteDesk Pro
File: gui/components/loading.py

Reusable loading components.
===============================================================================
"""

from __future__ import annotations

import customtkinter as ctk


class LoadingSpinner(ctk.CTkFrame):
    """Indeterminate loading widget."""

    def __init__(
        self,
        master,
        text: str = "Loading...",
        width: int = 220,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            width=width,
        )
        self.progress.grid(row=0, column=0, padx=10, pady=(10, 8))

        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=("Inter", 12),
        )
        self.label.grid(row=1, column=0, padx=10, pady=(0, 10))

        self._running = False

    def start(self) -> None:
        """Start the loading animation."""
        if not self._running:
            self.progress.start()
            self._running = True

    def stop(self) -> None:
        """Stop the loading animation."""
        if self._running:
            self.progress.stop()
            self._running = False

    def set_text(self, text: str) -> None:
        """Update the loading message."""
        self.label.configure(text=text)


class LoadingOverlay(ctk.CTkFrame):
    """Fullscreen loading overlay."""

    def __init__(
        self,
        master,
        message: str = "Please wait...",
        **kwargs,
    ) -> None:
        super().__init__(master, corner_radius=0, **kwargs)

        self.place_forget()

        self.spinner = LoadingSpinner(self, text=message)
        self.spinner.place(relx=0.5, rely=0.5, anchor="center")

    def show(self, message: str | None = None) -> None:
        """Display the overlay."""
        if message:
            self.spinner.set_text(message)
        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.spinner.start()

    def hide(self) -> None:
        """Hide the overlay."""
        self.spinner.stop()
        self.place_forget()
