"""
===============================================================================
RemoteDesk Pro
File: gui/components/glass.py
Premium glassmorphism UI components
===============================================================================
"""

from __future__ import annotations

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable

class GlassFrame(ctk.CTkFrame):
    """
    A frame with glassmorphism effect - semi-transparent background
    with subtle border and rounded corners
    """
    
    def __init__(
        self,
        master,
        corner_radius: int = 16,
        border_width: int = 1,
        glass_opacity: float = 0.1,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=corner_radius,
            border_width=border_width,
            **kwargs
        )
        self._glass_opacity = glass_opacity


class GlassCard(ctk.CTkFrame):
    """
    Premium card component with glassmorphism styling
    """
    
    def __init__(
        self,
        master,
        title: str = "",
        subtitle: str = "",
        width: int = 300,
        height: int = 200,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=20,
            border_width=1,
            border_color=("gray70", "gray30"),
            fg_color=("gray95", "gray15"),
            **kwargs
        )
        
        self._title = title
        self._subtitle = subtitle
        self._title_label: Optional[ctk.CTkLabel] = None
        self._subtitle_label: Optional[ctk.CTkLabel] = None
        
        if title:
            self._title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=18, weight="bold")
            )
            self._title_label.pack(padx=20, pady=(15, 5), anchor="w")
        
        if subtitle:
            self._subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=14, weight="normal"),
                text_color=("gray20", "gray70")
            )
            self._subtitle_label.pack(padx=20, pady=(0, 10), anchor="w")
    
    def add_content(self, widget, pady: int = 10):
        """Add content widget to card"""
        widget.pack(padx=20, pady=pady, fill="both", expand=True)


class GlassButton(ctk.CTkButton):
    """
    Premium button with glassmorphism hover effects
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 12)
        kwargs.setdefault("border_width", 0)
        kwargs.setdefault("font", ctk.CTkFont(size=14, weight="bold"))
        kwargs.setdefault("height", 40)
        
        super().__init__(master, **kwargs)
        
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
    
    def _on_hover_enter(self, event):
        """Handle mouse enter"""
        if self.cget("state") != "disabled":
            self.configure(border_width=1)
    
    def _on_hover_leave(self, event):
        """Handle mouse leave"""
        if self.cget("state") != "disabled":
            self.configure(border_width=0)


class GlassLabel(ctk.CTkLabel):
    """
    Premium label with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 8)
        super().__init__(master, **kwargs)


class GlassSlider(ctk.CTkSlider):
    """
    Premium slider with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("button_corner_radius", 10)
        kwargs.setdefault("button_color", ("gray70", "gray30"))
        kwargs.setdefault("progress_color", ("gray60", "gray40"))
        super().__init__(master, **kwargs)


class GlassEntry(ctk.CTkEntry):
    """
    Premium entry field with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", ("gray70", "gray30"))
        super().__init__(master, **kwargs)


class GlassComboBox(ctk.CTkComboBox):
    """
    Premium combo box with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("width", 200)
        super().__init__(master, **kwargs)


class GlassProgressBar(ctk.CTkProgressBar):
    """
    Premium progress bar with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("height", 8)
        kwargs.setdefault("corner_radius", 6)
        super().__init__(master, **kwargs)


class GlassSwitch(ctk.CTkSwitch):
    """
    Premium switch with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 16)
        super().__init__(master, **kwargs)


class GlassSegmentedButton(ctk.CTkSegmentedButton):
    """
    Premium segmented button with glassmorphism styling
    """
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)


class GlassFrame(ctk.CTkFrame):
    """
    A frame with glassmorphism effect - semi-transparent background
    with subtle border and rounded corners
    """
    
    def __init__(
        self,
        master,
        corner_radius: int = 16,
        border_width: int = 1,
        glass_opacity: float = 0.1,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=corner_radius,
            border_width=border_width,
            **kwargs
        )
        self._glass_opacity = glass_opacity