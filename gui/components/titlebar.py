"""
===============================================================================
RemoteDesk Pro
File: gui/components/titlebar.py

Custom title bar for the main application window.
Provides window controls (minimize, maximize, close) and the application title.
Designed to work with CustomTkinter and theme-aware.
===============================================================================
"""

from __future__ import annotations

from typing import Optional, Callable

import customtkinter

from core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PADDING,
    CORNER_RADIUS,
    ICON_SIZE,
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()

class TitleBar(customtkinter.CTkFrame):
    """
    Custom title bar for the main application window.
    
    Features:
    - Application logo/icon on the left
    - Application title in the center
    - Standard window controls (minimize, maximize, close) on the right
    - Smooth window dragging support
    - Theme-aware styling
    - Double-click to maximize support
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str = "RemoteDesk Pro",
        icon_path: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            height=40,
            fg_color=theme_manager.get_color("titlebar_bg", "#1E1E1E"),
            corner_radius=0,
            **kwargs,
        )
        self._master = master
        self._title = title
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_maximized = False
        
        # Create UI elements
        self._create_widgets(icon_path)
        
        # Bind events for window dragging
        self.bind("<ButtonPress-1>", self._on_drag_press)
        self.bind("<B1-Motion>", self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_release)
        self.bind("<Double-Button-1>", self._on_double_click)
        
        # Register theme callback
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_widgets(self, icon_path: Optional[str]) -> None:
        """Create the title bar's child widgets."""
        # Set minimum height
        self.configure(height=40)
        
        # Left side: Icon
        self._icon_label = None
        if icon_path:
            icon = load_image(icon_path, size=(ICON_SIZE, ICON_SIZE))
            if icon:
                self._icon_label = customtkinter.CTkLabel(
                    self,
                    image=icon,
                    text="",
                    anchor="w",
                )
                self._icon_label.pack(side="left", padx=(PADDING, 0))
        
        # Center: Title Label
        self._title_label = customtkinter.CTkLabel(
            self,
            text=self._title,
            font=customtkinter.CTkFont(
                family="Inter",
                size=11,
                weight="normal",
            ),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
            anchor="w",
        )
        if self._icon_label:
            self._title_label.pack(side="left", padx=(PADDING, 0), fill="x", expand=True)
        else:
            self._title_label.pack(fill="x", expand=True, padx=PADDING)
        
        # Right side: Window Controls
        self._create_window_controls()

    def _create_window_controls(self) -> None:
        """Create minimize, maximize, and close buttons."""
        self._controls_frame = customtkinter.CTkFrame(
            self,
            fg_color="transparent",
        )
        self._controls_frame.pack(side="right", padx=PADDING)
        
        # Minimize button
        self._minimize_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="—",  # Unicode minus sign
            command=self._minimize_window,
            width=30,
            height=30,
            corner_radius=5,
            fg_color=theme_manager.get_color("titlebar_minimize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._minimize_btn.pack(side="left", padx=2)
        
        # Maximize/Restore button
        self._maximize_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="□",  # Unicode square
            command=self._toggle_maximize,
            width=30,
            height=30,
            corner_radius=5,
            fg_color=theme_manager.get_color("titlebar_maximize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            font=customtkinter.CTkFont(size=14, weight="normal"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._maximize_btn.pack(side="left", padx=2)
        
        # Close button
        self._close_btn = customtkinter.CTkButton(
            self._controls_frame,
            text="✕",  # Unicode multiplication sign (X)
            command=self._close_window,
            width=30,
            height=30,
            corner_radius=5,
            fg_color=theme_manager.get_color("titlebar_close_bg", "#F44336"),
            hover_color=theme_manager.get_color("titlebar_close_hover", "#D32F2F"),
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._close_btn.pack(side="left", padx=2)

    def _on_theme_change(self, theme_name: str) -> None:
        """Update title bar colors when theme changes."""
        self.configure(
            fg_color=theme_manager.get_color("titlebar_bg", "#1E1E1E"),
        )
        self._title_label.configure(
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._minimize_btn.configure(
            fg_color=theme_manager.get_color("titlebar_minimize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._maximize_btn.configure(
            fg_color=theme_manager.get_color("titlebar_maximize_bg", "#444444"),
            hover_color=theme_manager.get_color("titlebar_control_hover", "#555555"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )
        self._close_btn.configure(
            fg_color=theme_manager.get_color("titlebar_close_bg", "#F44336"),
            hover_color=theme_manager.get_color("titlebar_close_hover", "#D32F2F"),
            text_color=theme_manager.get_color("titlebar_text", "#FFFFFF"),
        )

    # --------------------------------------------------------------------- #
    # Window Control Methods
    # --------------------------------------------------------------------- #
    def _minimize_window(self) -> None:
        """Minimize the application window."""
        self._master.iconify()

    def _toggle_maximize(self) -> None:
        """Toggle between maximized and normal window state."""
        if self._is_maximized:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self) -> None:
        """Maximize the application window."""
        self._master.state("zoomed")
        self._is_maximized = True
        self._update_maximize_button()

    def _restore_window(self) -> None:
        """Restore the window to its previous size and position."""
        self._master.state("normal")
        self._is_maximized = False
        self._update_maximize_button()

    def _update_maximize_button(self) -> None:
        """Update the maximize button text/icon."""
        if self._is_maximized:
            # Show restore icon (up arrow)
            self._maximize_btn.configure(text="❋")
        else:
            # Show maximize icon (square)
            self._maximize_btn.configure(text="□")

    def _close_window(self) -> None:
        """Close the application window."""
        self._master.destroy()

    # --------------------------------------------------------------------- #
    # Window Dragging Methods
    # --------------------------------------------------------------------- #
    def _on_drag_press(self, event) -> None:
        """Record initial mouse position when clicking on title bar."""
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_motion(self, event) -> None:
        """Move the window while dragging."""
        if self._is_maximized:
            return
        
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        
        x = self._master.winfo_x() + dx
        y = self._master.winfo_y() + dy
        
        self._master.geometry(f"+{x}+{y}")
        
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_drag_release(self, event) -> None:
        """Handle mouse release after dragging."""
        pass

    # --------------------------------------------------------------------- #
    # Double-click to maximize
    # --------------------------------------------------------------------- #
    def _on_double_click(self, event) -> None:
        """Toggle maximize on double-click."""
        self._toggle_maximize()

    # --------------------------------------------------------------------- #
    # Title Management
    # --------------------------------------------------------------------- #
    def set_title(self, title: str) -> None:
        """Update the title bar's title text."""
        self._title = title
        self._title_label.configure(text=title)

    def get_title(self) -> str:
        """Get the current title text."""
        return self._title

    # --------------------------------------------------------------------- #
    # Cleanup
    # --------------------------------------------------------------------- #
    def destroy(self) -> None:
        """Clean up resources."""
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


# Convenience function
def create_titlebar(
    master: customtkinter.CTk,
    title: str = "RemoteDesk Pro",
    icon_path: Optional[str] = None,
) -> TitleBar:
    """
    Factory function to create a title bar.
    
    Args:
        master: The parent window (CTk instance)
        title: The title text to display
        icon_path: Optional path to an icon image file
    
    Returns:
        A configured TitleBar instance
    """
    return TitleBar(master, title=title, icon_path=icon_path)


if __name__ == "__main__":
    # Demo for visual testing
    demo = customtkinter.CTk()
    demo.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    demo.title("Title Bar Demo")
    
    # Disable default title bar
    demo.configure(fg_color=theme_manager.get_color("background", "#0D0D0D"))
    
    # Create custom title bar
    titlebar = TitleBar(demo, title="RemoteDesk Pro Demo")
    titlebar.pack(fill="x", side="top")
    
    # Content area
    content = customtkinter.CTkFrame(demo, fg_color=theme_manager.get_color("surface", "#1A1A1A"))
    content.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)
    
    label = customtkinter.CTkLabel(
        content,
        text="Drag the title bar to move the window.\nDouble-click to maximize.\nClick the buttons to test window controls.",
        font=customtkinter.CTkFont(size=14),
        text_color=theme_manager.get_color("text_primary", "#FFFFFF"),
    )
    label.pack(expand=True)
    
    demo.mainloop()