"""
===============================================================================
RemoteDesk Pro
File: gui/components/notifications.py

Toast notification system for RemoteDesk Pro.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk


class ToastNotification(ctk.CTkFrame):
    """Single toast notification."""

    COLORS = {
        "info": "#2563EB",
        "success": "#16A34A",
        "warning": "#D97706",
        "error": "#DC2626",
    }

    def __init__(self, master, message: str, level: str = "info",
                 duration: int = 3000, **kwargs) -> None:
        super().__init__(master, corner_radius=10, **kwargs)

        color = self.COLORS.get(level, self.COLORS["info"])

        self.configure(border_width=1, border_color=color)

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=message,
            justify="left",
            anchor="w",
            wraplength=260,
            font=("Inter", 12),
        )
        self.label.grid(row=0, column=0, padx=12, pady=10, sticky="ew")

        self.close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=26,
            height=26,
            fg_color="transparent",
            hover_color=color,
            command=self.destroy,
        )
        self.close_btn.grid(row=0, column=1, padx=(0, 8), pady=8)

        self.after(duration, self.destroy)


class NotificationManager(ctk.CTkFrame):
    """Stacked toast notification manager."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self.place(relx=1.0, y=16, x=-16, anchor="ne")
        self._items: list[ToastNotification] = []

    def show(self, message: str,
             level: str = "info",
             duration: int = 3000) -> None:
        """Display a toast notification."""
        toast = ToastNotification(
            self,
            message=message,
            level=level,
            duration=duration,
        )
        self._items.append(toast)
        self._relayout()

        original_destroy = toast.destroy

        def _destroy() -> None:
            if toast in self._items:
                self._items.remove(toast)
                self._relayout()
            original_destroy()

        toast.destroy = _destroy  # type: ignore[method-assign]

    def _relayout(self) -> None:
        for widget in self.winfo_children():
            widget.pack_forget()
        for toast in self._items:
            toast.pack(fill="x", pady=4)
