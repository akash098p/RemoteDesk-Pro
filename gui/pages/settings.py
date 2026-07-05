"""
===============================================================================
RemoteDesk Pro
File: gui/pages/settings.py
Settings page for theme, font size, notification preferences, and window settings.
===============================================================================
"""

from __future__ import annotations

import customtkinter
from core.config_manager import get_config_manager
from core.theme_manager import get_theme_manager
from core.utils import clamp

theme_manager = get_theme_manager()
config_manager = get_config_manager()

class SettingsPage(customtkinter.CTkFrame):
    """Settings page with options for theme, font size, and system preferences."""
    
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self._theme_manager = get_theme_manager()
        self._config = config_manager.get_config("settings")
        
        # Create UI
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        # Header
        title_label = customtkinter.CTkLabel(
            self, text="Settings", font=customtkinter.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Theme Section
        theme_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)
        
        theme_label = customtkinter.CTkLabel(
            theme_frame, text="Theme:",
            font=customtkinter.CTkFont(size=14)
        )
        theme_label.pack(side="left", padx=(0, 10))
        
        self.theme_var = customtkinter.StringVar(value=self._config.get("theme", "dark"))
        theme_menu = customtkinter.CTkOptionMenu(
            theme_frame, 
            variable=self.theme_var,
            values=["dark", "light", "nord", "dracula", "amoled"],
            command=self._on_theme_change
        )
        theme_menu.pack(side="left")
        
        # Font Size Section
        font_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        font_frame.pack(fill="x", pady=10)
        
        font_label = customtkinter.CTkLabel(
            font_frame, text="Font Size:",
            font=customtkinter.CTkFont(size=14)
        )
        font_label.pack(side="left", padx=(0, 10))
        
        self.font_var = customtkinter.IntVar(value=self._config.get("font_size", 14))
        font_spinbox = customtkinter.CTkSpinner(
            font_frame,
            from_=10,
            to=24,
            number_of_steps=14,
            command=self._on_font_change
        )
        font_spinbox.pack(side="left")
        
        # Notification Section
        notif_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        notif_frame.pack(fill="x", pady=10)
        
        notif_label = customtkinter.CTkLabel(
            notif_frame, text="Notification Duration (ms):",
            font=customtkinter.CTkFont(size=14)
        )
        notif_label.pack(side="left", padx=(0, 10))
        
        self.notif_var = customtkinter.IntVar(value=self._config.get("notif_duration", 3000))
        notif_spinbox = customtkinter.CTkSpinner(
            notif_frame,
            from_=1000,
            to=10000,
            number_of_steps=10,
            command=self._on_notif_change
        )
        notif_spinbox.pack(side="left")
        
        # Window Section
        win_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        win_frame.pack(fill="x", pady=10)
        
        win_label = customtkinter.CTkLabel(
            win_frame, text="Window Size:",
            font=customtkinter.CTkFont(size=14)
        )
        win_label.pack(side="left", padx=(0, 10))
        
        # Width
        self.win_width = self.parent.winfo_width()
        width_spinbox = customtkinter.CTkSpinner(
            win_frame,
            from_=800,
            to=1920,
            number_of_steps=100,
            command=lambda: self._update_window_size("width")
        )
        width_spinbox.pack(side="left")
        
        # Height
        self.win_height = self.parent.winfo_height()
        height_spinbox = customtkinter.CTkSpinner(
            win_frame,
            from_=600,
            to=1080,
            number_of_steps=100,
            command=lambda: self._update_window_size("height")
        )
        height_spinbox.pack(side="left")
        
        # Back Button
        back_btn = customtkinter.CTkButton(
            self,
            text="Back",
            command=self._back_to_dashboard
        )
        back_btn.pack(pady=20)
        
    def _on_theme_change(self, new_theme: str) -> None:
        self._theme_manager.set_theme(new_theme)
        self.config_manager.set_value("settings", "theme", new_theme)
        
    def _on_font_change(self, new_size: str) -> None:
        size = int(new_size)
        if 10 <= size <= 24:
            self.config_manager.set_value("settings", "font_size", size)
            # Update global font size (would require core.utils font registration)
        
    def _on_notif_change(self, new_duration: str) -> None:
        duration = int(new_duration)
        self.config_manager.set_value("settings", "notif_duration", clamp(duration, 500, 10000))
        
    def _update_window_size(self, dimension: str) -> None:
        size = self._get_current_spinbox_value(dimension)
        if dimension == "width":
            self.parent.geometry(f"{size}x{self.win_height}")
        else:
            self.parent.geometry(f"{self.win_width}x{size}")
        
        self.config_manager.set_value("settings", dimension, size)
        
    def _get_current_spinbox_value(self, dimension: str) -> int:
        # This would need to track spinbox values properly
        # Currently simplified for demo
        return 1000  # Placeholder
        
    def _back_to_dashboard(self) -> None:
        if self.parent._navigation_manager:
            self.parent._navigation_manager.show_page("dashboard")