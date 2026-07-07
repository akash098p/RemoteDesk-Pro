"""
===============================================================================
RemoteDesk Pro
File: gui/components/buttons.py

Defines various reusable button widgets for the application, ensuring
consistent styling and theme integration.
===============================================================================
"""
from __future__ import annotations

from typing import Callable, Optional, Tuple, Union

import customtkinter

from core.constants import (
    BUTTON_HEIGHT, BUTTON_WIDTH, CORNER_RADIUS, ICON_SIZE, PADDING,
    FONT_SIZE_BODY
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()

class BaseButton(customtkinter.CTkButton):
    """
    Base class for all custom buttons, providing common styling and theme integration.
    """
    def __init__(
        self,
        master: Any,
        text: str = "",
        command: Optional[Callable[..., Any]] = None,
        width: int = BUTTON_WIDTH,
        height: int = BUTTON_HEIGHT,
        corner_radius: int = CORNER_RADIUS,
        font_size: int = FONT_SIZE_BODY,
        icon: Optional[Union[str, customtkinter.CTkImage]] = None,
        icon_size: int = ICON_SIZE,
        **kwargs: Any,
    ) -> None:
        
        self._master = master
        self._icon_name = icon if isinstance(icon, str) else None
        self._icon_image = icon if isinstance(icon, customtkinter.CTkImage) else None
        self._icon_size = icon_size

        unsupported = {"icon_size", "hover_text", "padx"}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in unsupported}

        super().__init__(
            master=master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            font=theme_manager.get_font("Inter", font_size, "medium"),
            **filtered_kwargs,
        )
        self._apply_theme_colors()
        theme_manager.register_theme_change_callback(self._on_theme_change)
        self._load_and_set_icon()

    def _apply_theme_colors(self) -> None:
        """
        Applies theme-specific colors to the button.
        To be overridden by subclasses for specific button types.
        """
        pass # Base class does not apply specific colors

    def _on_theme_change(self, theme_name: str) -> None:
        """
        Callback for when the theme changes. Re-applies theme colors.
        """
        self._apply_theme_colors()
        # Reload icon as its colors might change with theme
        self._load_and_set_icon()

    def _load_and_set_icon(self) -> None:
        """
        Loads the icon image if an icon_name is provided and sets it to the button.
        """
        if self._icon_name:
            self._icon_image = load_image(self._icon_name, size=(self._icon_size, self._icon_size))
            if self._icon_image:
                self.configure(image=self._icon_image, compound="left")
            else:
                self.configure(image=None, compound="none") # Clear image if loading failed
        elif self._icon_image: # If a CTkImage was passed directly
            self.configure(image=self._icon_image, compound="left")
        else:
            self.configure(image=None, compound="none")


    def set_icon(self, icon: Optional[Union[str, customtkinter.CTkImage]]) -> None:
        """
        Sets or updates the icon of the button.
        """
        self._icon_name = icon if isinstance(icon, str) else None
        self._icon_image = icon if isinstance(icon, customtkinter.CTkImage) else None
        self._load_and_set_icon()

    def destroy(self) -> None:
        """
        Destroys the widget and unregisters theme change callback.
        """
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class PrimaryButton(BaseButton):
    """
    A prominent button for primary actions (e.g., "Connect", "Save").
    """
    def _apply_theme_colors(self) -> None:
        self.configure(
            fg_color=theme_manager.get_color("primary"),
            hover_color=theme_manager.get_color("primary_hover", "primary"),
            text_color=theme_manager.get_color("text_on_primary", "text_primary"),
        )


class SecondaryButton(BaseButton):
    """
    A secondary button for less prominent actions (e.g., "Cancel", "Browse").
    """
    def _apply_theme_colors(self) -> None:
        self.configure(
            fg_color=theme_manager.get_color("secondary"),
            hover_color=theme_manager.get_color("secondary_hover", "surface"),
            text_color=theme_manager.get_color("text_primary"),
            border_color=theme_manager.get_color("border"),
            border_width=1,
        )


class DangerButton(BaseButton):
    """
    A button for destructive actions (e.g., "Delete", "Disconnect").
    """
    def _apply_theme_colors(self) -> None:
        self.configure(
            fg_color=theme_manager.get_color("error"),
            hover_color=theme_manager.get_color("error_hover", "error"),
            text_color=theme_manager.get_color("text_on_error", "text_primary"),
        )


class SidebarButton(BaseButton):
    """
    A button specifically designed for the collapsible sidebar navigation.
    """
    def __init__(
        self,
        master: Any,
        text: str,
        command: Optional[Callable[..., Any]] = None,
        icon: Optional[Union[str, customtkinter.CTkImage]] = None,
        is_active: bool = False,
        width: int = BUTTON_WIDTH,
        height: int = BUTTON_HEIGHT,
        corner_radius: int = CORNER_RADIUS,
        font_size: int = FONT_SIZE_BODY,
        **kwargs: Any,
    ) -> None:
        self._is_active = is_active
        super().__init__(
            master=master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            font_size=font_size,
            anchor="w", # Align text and icon to the left
            padx=PADDING,
            icon=icon,
            **kwargs,
        )

    def _apply_theme_colors(self) -> None:
        if self._is_active:
            self.configure(
                fg_color=theme_manager.get_color("sidebar_button_active_bg", "primary"),
                hover_color=theme_manager.get_color("sidebar_button_active_hover_bg", "primary_hover"),
                text_color=theme_manager.get_color("sidebar_button_active_text", "text_on_primary"),
            )
        else:
            self.configure(
                fg_color=theme_manager.get_color("sidebar_button_bg", "transparent"),
                hover_color=theme_manager.get_color("sidebar_button_hover_bg", "surface_hover"),
                text_color=theme_manager.get_color("sidebar_button_text", "text_primary"),
            )

    def set_active(self, active: bool) -> None:
        """
        Sets the active state of the sidebar button.
        """
        if self._is_active != active:
            self._is_active = active
            self._apply_theme_colors()
            logger.debug(f"Sidebar button '{self.cget('text')}' set to active: {active}")

    def _set_nav_key(self, key: str) -> None:
        """Set the internal navigation key for sidebar state tracking."""
        self._nav_key = key


class IconButton(BaseButton):
    """
    A button that displays only an icon, typically for toolbar or compact actions.
    """
    def __init__(
        self,
        master: Any,
        command: Optional[Callable[..., Any]] = None,
        icon: Optional[Union[str, customtkinter.CTkImage]] = None,
        width: int = ICON_SIZE + PADDING,
        height: int = ICON_SIZE + PADDING,
        corner_radius: int = CORNER_RADIUS,
        tooltip_text: str = "", # Future: Add tooltip functionality
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master=master,
            text="", # Icon buttons typically have no text
            command=command,
            width=width,
            height=height,
            corner_radius=corner_radius,
            icon=icon,
            **kwargs,
        )
        self._tooltip_text = tooltip_text
        self.configure(compound="center") # Center the icon
    
    def _apply_theme_colors(self) -> None:
        self.configure(
            fg_color=theme_manager.get_color("icon_button_bg", "transparent"),
            hover_color=theme_manager.get_color("icon_button_hover_bg", "surface_hover"),
            text_color=theme_manager.get_color("icon_button_text", "text_primary"),
            image_property="text_color",
        )


class CloseButton(IconButton):
    """
    A red icon button for closing actions.
    """
    def __init__(
        self,
        master: Any,
        command: Optional[Callable[..., Any]] = None,
        width: int = ICON_SIZE + PADDING,
        height: int = ICON_SIZE + PADDING,
        corner_radius: int = CORNER_RADIUS,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master=master,
            command=command,
            icon="close.svg",
            width=width,
            height=height,
            corner_radius=corner_radius,
            **kwargs,
        )

    def _apply_theme_colors(self) -> None:
        self.configure(
            fg_color=theme_manager.get_color("close_button_bg", "transparent"),
            hover_color=theme_manager.get_color("close_button_hover_bg", "error"),
            text_color=theme_manager.get_color("close_button_text", "text_primary"),
            image_property="text_color",
        )
