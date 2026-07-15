"""
===============================================================================
RemoteDesk Pro
File: settings.py
Updates the Settings page to include frame rate and quality controls.
Adds frame rate selection drop-down and quality slider.
===============================================================================
"""

from typing import Optional
import customtkinter
from core.constants import FONT_SIZE_LABEL, FONT_SIZE_BODY
from core.theme_manager import get_theme_manager
from core.config_manager import get_config_manager

theme_manager = get_theme_manager()
config_manager = get_config_manager()

class SettingsPage(customtkinter.CTkFrame):
    """
    Settings page with options for theme, font size, notification preferences,
    window settings, and now frame rate & quality controls for screen capture.
    """
    
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.theme_manager = theme_manager
        self.config_manager = config_manager
        
        # Load current settings and theme
        self._settings = self.config_manager.get_config("settings")
        self.theme_var = customtkinter.StringVar(value=self.theme_manager.current_theme_name)
        self._theme_callback_registered = False
        
        # Create UI
        self._create_widgets()
        self.theme_manager.register_theme_change_callback(self._handle_theme_refresh)
        self._theme_callback_registered = True
            
    def _on_theme_change(self, new_theme: Optional[str] = None) -> None:
        if new_theme is None:
            new_theme = self.theme_var.get()
        self.theme_manager.set_theme(new_theme)
        self.config_manager.set_value("config", "theme", new_theme)
    
    def _on_font_change(self, new_font_size: str) -> None:
        size = int(new_font_size)
        self.config_manager.set_value("settings", "font_size", size)
    
    def _on_quality_change(self, new_quality: str) -> None:
        quality = int(new_quality)
        self.config_manager.set_value("settings", "quality", quality)
    
    def _on_fps_change(self, new_fps: str) -> None:
        fps = int(new_fps)
        self.config_manager.set_value("settings", "fps", fps)
    
    def _back_to_dashboard(self) -> None:
        if self.parent._navigation_manager:
            self.parent._navigation_manager.show_page("dashboard")

    def _create_widgets(self) -> None:
        text_secondary = self.theme_manager.get_color("text_secondary", "#AEB8C5")
        surface = self.theme_manager.get_color("surface", "#1A2940")
        border = self.theme_manager.get_color("border", "#31435F")
        # Header
        title_label = customtkinter.CTkLabel(
            self, text="Settings", 
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=self.theme_manager.get_color("text_primary", "#FFFFFF"),
        )
        title_label.pack(pady=20)
        
        # Theme Section
        theme_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)
        
        theme_label = customtkinter.CTkLabel(
            theme_frame, text="Theme:",
            font=customtkinter.CTkFont(size=14),
            text_color=text_secondary,
        )
        theme_label.pack(side="left", padx=(0, 10))
        
        self.theme_dropdown = customtkinter.CTkOptionMenu(
            theme_frame, 
            variable=self.theme_var,
            values=list(theme_manager.available_themes),
            command=lambda new_theme: self._on_theme_change(new_theme)
        )
        self.theme_dropdown.pack(side="left")
        
        # Font Size Section
        font_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        font_frame.pack(fill="x", pady=10)
        
        font_label = customtkinter.CTkLabel(
            font_frame, text="Font Size:",
            font=customtkinter.CTkFont(size=14),
            text_color=text_secondary,
        )
        font_label.pack(side="left", padx=(0, 10))
        
        self.font_var = customtkinter.StringVar(value=str(self._settings.get("font_size", 14)))
        self.font_spinbox = customtkinter.CTkOptionMenu(
            font_frame,
            variable=self.font_var,
            values=[str(size) for size in range(10, 25)],
            command=self._on_font_change,
        )
        self.font_spinbox.pack(side="left")
        
        # Quality & Frame Rate Section
        quality_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        quality_frame.pack(fill="x", pady=10)
        
        quality_label = customtkinter.CTkLabel(
            quality_frame, text="Capture Quality:",
            font=customtkinter.CTkFont(size=14),
            text_color=text_secondary,
        )
        quality_label.pack(side="left", padx=(0, 10))
        
        self.quality_var = customtkinter.IntVar(value=self._settings.get("quality", 75))
        self.quality_slider = customtkinter.CTkSlider(
            quality_frame,
            variable=self.quality_var,
            from_=1,
            to=100,
            number_of_steps=100,
            command=lambda e: self.config_manager.set_value("settings", "quality", self.quality_var.get())
        )
        self.quality_slider.pack(side="left", fill="x", expand=True)
        
        # Frame Rate Section
        fps_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        fps_frame.pack(fill="x", pady=10)
        
        fps_label = customtkinter.CTkLabel(
            fps_frame, text="Capture FPS:",
            font=customtkinter.CTkFont(size=14),
            text_color=text_secondary,
        )
        fps_label.pack(side="left", padx=(0, 10))
        
        fps_options = ["15", "24", "30", "60"]
        self.fps_var = customtkinter.IntVar(value=self._settings.get("fps", 30))
        self.fps_spinbox = customtkinter.CTkOptionMenu(
            fps_frame,
            variable=self.fps_var,
            values=[str(fps) for fps in [15, 24, 30, 60]],
            command=lambda e: self.config_manager.set_value("settings", "fps", self.fps_var.get())
        )
        self.fps_spinbox.pack(side="left")
        
        # Back button
        back_btn = customtkinter.CTkButton(
            self, text="Back", command=self._back_to_dashboard
        )
        back_btn.pack(pady=20)

    def _handle_theme_refresh(self, theme_name: str) -> None:
        for child in self.winfo_children():
            child.destroy()
        self._create_widgets()

    def destroy(self) -> None:
        if self._theme_callback_registered:
            self.theme_manager.unregister_theme_change_callback(self._handle_theme_refresh)
        super().destroy()
