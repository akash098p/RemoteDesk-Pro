"""
===============================================================================
RemoteDesk Pro
File: gui/pages/about.py
About page showing application information and credits.
===============================================================================
"""

from __future__ import annotations

import customtkinter
from core.config_manager import get_config_manager

config_manager = get_config_manager()

class AboutPage(customtkinter.CTkFrame):
    """Page displaying application information."""
    
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        
        # Create UI
        self._create_widgets()
        
    def _create_widgets(self) -> None:
        # Header
        title_label = customtkinter.CTkLabel(
            self, text="About RemoteDesk Pro", 
            font=customtkinter.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Application info
        info_text = f"""
RemoteDesk Pro v{config_manager.get_config('settings').get('app_version', '1.0.0')}
A modern remote collaboration platform inspired by AnyDesk and TeamViewer.
        
Developer: Akash Pramanik
GitHub: https://github.com/akash098p/RemoteDesk-Pro
        
License: MIT
"""
        
        info_label = customtkinter.CTkLabel(
            self, 
            text=info_text,
            font=customtkinter.CTkFont(family="Inter", size=14),
            text_color=theme_manager.get_color("text_secondary", "#A0A0A0")
        )
        info_label.pack(padx=20, pady=(0, 20))
        
        # Back button
        back_btn = customtkinter.CTkButton(
            self,
            text="Back",
            command=self._back_to_dashboard
        )
        back_btn.pack(pady=20)
        
    def _back_to_dashboard(self) -> None:
        if self.parent._navigation_manager:
            self.parent._navigation_manager.show_page("dashboard")