"""
==============================================================================
RemoteDesk Pro
File: gui/components/cards.py

Reusable card-style container widgets for organizing UI content.
Includes StatusCard, SystemStatusCard, and other specialized cards.
==============================================================================
"""

from __future__ import annotations

from typing import Any, Optional

import customtkinter

from core.constants import (
    CORNER_RADIUS,
    PADDING,
    FONT_SIZE_BODY,
    FONT_SIZE_LABEL,
    FONT_SIZE_HEADER,
    ICON_SIZE,
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()


class Card(customtkinter.CTkFrame):
    """
    Generic card widget for grouping content with consistent styling.
    
    Features:
    - Optional header with title and icon
    - Flexible body area
    - Optional footer
    - Theme-aware colors
    - Rounded corners and subtle border
    """
    
    def __init__(
        self,
        master: customtkinter.CTk,
        title: Optional[str] = None,
        header_icon: Optional[str] = None,
        width: int = 340,
        height: int = 200,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a card widget.
        
        Args:
            master: Parent widget
            title: Optional card title
            header_icon: Optional icon filename (from assets/icons/)
            width: Card width in pixels
            height: Card height in pixels
            **kwargs: Additional CTkFrame options
        """
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=CORNER_RADIUS + 2,
            fg_color=theme_manager.get_color("card_bg", "#252525"),
            border_width=1,
            border_color=theme_manager.get_color("card_border", "#333333"),
            **kwargs,
        )
        
        self._title = title
        self._header_icon = header_icon
        
        # Create UI
        self._create_widgets()
        
        # Register theme callback
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_widgets(self) -> None:
        """Create the card's internal widgets."""
        # Header frame (if title provided)
        if self._title:
            self._header_frame = customtkinter.CTkFrame(
                self, fg_color="transparent"
            )
            self._header_frame.pack(fill="x", padx=PADDING, pady=(PADDING, 0))
            
            # Icon (if provided)
            if self._header_icon:
                icon = load_image(self._header_icon, size=(ICON_SIZE, ICON_SIZE))
                if icon:
                    icon_label = customtkinter.CTkLabel(
                        self._header_frame, image=icon, text=""
                    )
                    icon_label.pack(side="left", padx=(0, PADDING // 2))
            
            # Title label
            self._title_label = customtkinter.CTkLabel(
                self._header_frame,
                text=self._title,
                font=customtkinter.CTkFont(
                    family="Inter",
                    size=FONT_SIZE_LABEL,
                    weight="bold"
                ),
                text_color=theme_manager.get_color("card_title", "#FFFFFF"),
            )
            self._title_label.pack(side="left", anchor="w")
        
        # Body frame
        self._body_frame = customtkinter.CTkFrame(
            self, fg_color="transparent"
        )
        self._body_frame.pack(
            fill="both",
            expand=True,
            padx=PADDING,
            pady=PADDING
        )
        
        # Footer frame (created lazily)
        self._footer_frame: Optional[customtkinter.CTkFrame] = None

    def _on_theme_change(self, theme_name: str) -> None:
        """Update styling when theme changes."""
        self.configure(
            fg_color=theme_manager.get_color("card_bg", "#252525"),
            border_color=theme_manager.get_color("card_border", "#333333"),
        )
        if hasattr(self, "_title_label"):
            self._title_label.configure(
                text_color=theme_manager.get_color("card_title", "#FFFFFF")
            )

    def add_content(self, widget: customtkinter.CTkBaseClass) -> None:
        """Add a widget to the card's body area."""
        widget.pack(fill="both", expand=True)

    def add_footer(self, text: str = "", command: Optional[callable] = None) -> None:
        """Add a footer section with optional action."""
        if self._footer_frame is None:
            self._footer_frame = customtkinter.CTkFrame(
                self, fg_color="transparent"
            )
            self._footer_frame.pack(
                fill="x",
                padx=PADDING,
                pady=(0, PADDING)
            )
        
        footer_label = customtkinter.CTkLabel(
            self._footer_frame,
            text=text,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=theme_manager.get_color("card_footer_text", "#A0A0A0"),
            cursor="hand2" if command else "arrow",
        )
        footer_label.pack(side="left")
        
        if command:
            footer_label.bind("<Button-1>", lambda _: command())

    def destroy(self) -> None:
        """Clean up resources."""
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


# Backwards-compatibility alias expected by some pages
PageCard = Card


class StatusCard(Card):
    """
    Specialized card for displaying status information.
    Shows a title and value with optional icon.
    """
    
    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        value: str = "-",
        icon: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title=title, **kwargs)
        self._value_label = None
        self._icon = icon
        self._create_value_display(value)

    def _create_value_display(self, value: str) -> None:
        """Create the value display area."""
        # Value label
        self._value_label = customtkinter.CTkLabel(
            self._body_frame,
            text=value,
            font=customtkinter.CTkFont(
                family="Inter",
                size=FONT_SIZE_HEADER,
                weight="bold"
            ),
            text_color=theme_manager.get_color("primary", "#0084FF"),
        )
        self._value_label.pack(pady=(PADDING, 0))
        
        # Icon (if provided)
        if self._icon:
            icon = load_image(self._icon, size=(32, 32))
            if icon:
                icon_label = customtkinter.CTkLabel(
                    self._body_frame,
                    image=icon,
                    text=""
                )
                icon_label.pack(pady=(PADDING, 0))

    def set_value(self, value: str, color_key: Optional[str] = None) -> None:
        """Update the displayed value."""
        if self._value_label:
            self._value_label.configure(text=value)
            if color_key:
                self._value_label.configure(
                    text_color=theme_manager.get_color(color_key, "#0084FF")
                )

    def set_title(self, title: str) -> None:
        """Update the card title."""
        if hasattr(self, "_title_label"):
            self._title_label.configure(text=title)
        self._title = title


class SystemStatusCard(Card):
    """
    Card for displaying system status information like CPU/RAM usage.
    """
    
    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        initial_value: str = "0%",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title=title, **kwargs)
        self._value_label = None
        self._create_status_display(initial_value)

    def _create_status_display(self, initial_value: str) -> None:
        """Create the status display."""
        self._value_label = customtkinter.CTkLabel(
            self._body_frame,
            text=initial_value,
            font=customtkinter.CTkFont(
