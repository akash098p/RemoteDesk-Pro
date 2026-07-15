"""
===============================================================================
RemoteDesk Pro
File: gui/components/statusbar.py
Defines the status bar component at the bottom of the MainWindow.
===============================================================================
"""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter

from core.constants import STATUS_BAR_HEIGHT, PADDING, CORNER_RADIUS
from core.theme_manager import get_theme_manager
from core.utils import get_cpu_usage, get_ram_usage, get_app_version, load_image

theme_manager = get_theme_manager()


class StatusBar(customtkinter.CTkFrame):
    """Theme-aware bottom status bar."""

    def __init__(
        self,
        master: customtkinter.CTk,
        toggle_theme_callback: Optional[Callable[[], None]] = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            master,
            height=STATUS_BAR_HEIGHT,
            fg_color=theme_manager.get_color("statusbar_bg", "#333333"),
            corner_radius=0,
            border_width=1,
            border_color=theme_manager.get_color("border", "#333333"),
            **kwargs,
        )
        self.pack(side="bottom", fill="x")

        self._toggle_theme_callback = toggle_theme_callback
        self._notification_count: int = 0
        self._update_job: Optional[str] = None

        self._create_widgets()
        self._start_periodic_updates()
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_widgets(self) -> None:
        left_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", fill="y", padx=PADDING)

        self.cpu_label = customtkinter.CTkLabel(
            left_frame,
            text="CPU: --%",
            font=customtkinter.CTkFont(family="Inter", size=11),
            text_color=theme_manager.get_color("statusbar_text", "#FFFFFF"),
        )
        self.cpu_label.pack(side="left", padx=PADDING / 2)

        self.ram_label = customtkinter.CTkLabel(
            left_frame,
            text="RAM: --%",
            font=customtkinter.CTkFont(family="Inter", size=11),
            text_color=theme_manager.get_color("statusbar_text", "#FFFFFF"),
        )
        self.ram_label.pack(side="left", padx=PADDING / 2)

        self.connection_label = customtkinter.CTkLabel(
            self,
            text="Status: Idle",
            font=customtkinter.CTkFont(family="Inter", size=11, weight="bold"),
            text_color=theme_manager.get_color("statusbar_secondary_text", "#FFFFFF"),
        )
        self.connection_label.pack(side="top", fill="both", expand=True)

        right_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", fill="y", padx=PADDING)

        self.notification_frame = customtkinter.CTkFrame(
            right_frame,
            fg_color=theme_manager.get_color("notification_badge", "#FF0000"),
            corner_radius=CORNER_RADIUS,
        )
        self.notification_frame.pack(side="left", padx=PADDING / 2)
        self.notification_frame.pack_forget()

        self.notification_label = customtkinter.CTkLabel(
            self.notification_frame,
            text="0",
            font=customtkinter.CTkFont(family="Inter", size=10, weight="bold"),
            text_color=theme_manager.get_color("notification_text", "#FFFFFF"),
        )
        self.notification_label.pack(padx=PADDING / 2, pady=2)

        theme_icon = load_image("moon-star.svg", size=(18, 18))
        self.theme_button = customtkinter.CTkButton(
            right_frame,
            image=theme_icon,
            text="",
            command=self._toggle_theme,
            width=34,
            height=28,
            fg_color="transparent",
            hover_color=theme_manager.get_color("icon_button_hover_bg", "#3A3A3A"),
            corner_radius=10,
        )
        self.theme_button.pack(side="left", padx=PADDING / 2)

        self.version_label = customtkinter.CTkLabel(
            right_frame,
            text=f"v{get_app_version()}",
            font=customtkinter.CTkFont(family="Inter", size=10),
            text_color=theme_manager.get_color("statusbar_secondary_text", "#888888"),
        )
        self.version_label.pack(side="left", padx=PADDING)

    def _start_periodic_updates(self) -> None:
        self._update_system_status()

    def _update_system_status(self) -> None:
        cpu_percent = get_cpu_usage()
        self.cpu_label.configure(text=f"CPU: {cpu_percent:.1f}%")

        ram = get_ram_usage()
        self.ram_label.configure(text=f"RAM: {ram[0]:.1f}%")
        self._update_job = self.after(1000, self._update_system_status)

    def set_connection_status(self, status: str, is_connected: bool = True) -> None:
        color = theme_manager.get_color("success") if is_connected else theme_manager.get_color("danger", "error")
        self.connection_label.configure(text=f"Status: {status}", text_color=color)

    def update_notification_count(self, count: int) -> None:
        self._notification_count = count
        if count > 0:
            self.notification_frame.pack(side="left", padx=PADDING / 2)
            self.notification_label.configure(text=str(count) if count <= 99 else "99+")
        else:
            self.notification_frame.pack_forget()

    def increment_notification(self) -> None:
        self.update_notification_count(self._notification_count + 1)

    def clear_notifications(self) -> None:
        self.update_notification_count(0)

    def _toggle_theme(self) -> None:
        if self._toggle_theme_callback:
            self._toggle_theme_callback()
        else:
            current_mode = customtkinter.get_appearance_mode()
            new_mode = "light" if current_mode == "dark" else "dark"
            customtkinter.set_appearance_mode(new_mode)

    def _on_theme_change(self, theme_name: str) -> None:
        self.configure(
            fg_color=theme_manager.get_color("statusbar_bg", "#333333"),
            border_color=theme_manager.get_color("border", "#333333"),
        )
        self.cpu_label.configure(text_color=theme_manager.get_color("statusbar_text", "#FFFFFF"))
        self.ram_label.configure(text_color=theme_manager.get_color("statusbar_text", "#FFFFFF"))
        self.connection_label.configure(text_color=theme_manager.get_color("statusbar_secondary_text", "#FFFFFF"))
        self.version_label.configure(text_color=theme_manager.get_color("statusbar_secondary_text", "#888888"))
        self.theme_button.configure(hover_color=theme_manager.get_color("icon_button_hover_bg", "#3A3A3A"))
        self.notification_frame.configure(fg_color=theme_manager.get_color("notification_badge", "#FF0000"))
        self.notification_label.configure(text_color=theme_manager.get_color("notification_text", "#FFFFFF"))

    def destroy(self) -> None:
        if self._update_job:
            self.after_cancel(self._update_job)
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


if __name__ == "__main__":
    app = customtkinter.CTk()
    app.geometry("800x600")
    status_bar = StatusBar(app)
    app.mainloop()
