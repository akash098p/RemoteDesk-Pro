"""
===============================================================================
RemoteDesk Pro
File: gui/components/sidebar.py
Defines a collapsible navigation sidebar with smooth animations and theme integration.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Callable, List, Optional

import customtkinter

from core.constants import (
    SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH, SIDEBAR_ANIMATION_SPEED
)
from core.theme_manager import get_theme_manager
from gui.components.buttons import SidebarButton

theme_manager = get_theme_manager()

class Sidebar(customtkinter.CTkFrame):
    """
    Collapsible navigation sidebar for RemoteDesk Pro.
    
    Features:
    - Contains primary navigation buttons (Dashboard, Connection, Settings, etc.)
    - Smooth collapse/expand animation
    - Icon + text display in expanded state
    - Icon-only in collapsed state
    - Active page highlighting
    - Theme integration via ThemeManager
    """
    
    def __init__(
        self,
        master: customtkinter.CTk,
        navigate_callback: Callable[[str], None],
        **kwargs: object,
    ) -> None:
        """
        Initialize sidebar with navigation callback.
        
        Args:
            master: Parent widget (MainWindow)
            navigate_callback: Function to call when item clicked (takes page_key)
            **kwargs: Additional widget configuration
        """
        super().__init__(master, width=SIDEBAR_WIDTH, corner_radius=10, fg_color="#2B2B2B")
        self._navigate_callback = navigate_callback
        self._is_expanded: bool = True  # Starts expanded
        self._animation_start_time: Optional[float] = None
        self._is_toggling: bool = False
        self._current_height: int = 0
        
        # Create navigation container
        self._nav_frame = customtkinter.CTkFrame(
            self, fg_color="transparent"
        ).pack(fill="y", padx=5, pady=10)
        
        # Create toggle button for collapse (handle externally via toolbar)
        self._is_toggling = False
        self._create_navigation_items()
        
        # Configure initial hover state
        self._update_hover_state()
        
        # Bind events for hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_configure)
        
        logger.debug(f"Sidebar initialized (expanded: {self._is_expanded})")

    def _create_navigation_items(self) -> None:
        """Create and configure all navigation buttons."""
        # Define navigation items with icons and labels
        nav_items = [
            {
                "key": "dashboard",
                "icon": "dashboard.svg",
                "text": "Dashboard",
                "hover_text": "Main Overview",
                "icon_size": 24
            },
            {
                "key": "connection", 
                "icon": "plug-zap.svg",
                "text": "Connection",
                "hover_text": "Network Status",
                "icon_size": 24
            },
            {
                "key": "settings", 
                "icon": "settings.svg",
                "text": "Settings",
                "hover_text": "Preferences",
                "icon_size": 24
            },
            {
                "key": "logs", 
                "icon": "file-text.svg",
                "text": "Logs",
                "hover_text": "Diagnostics",
                "icon_size": 24
            },
            {
                "key": "about", 
                "icon": "info.svg",
                "text": "About",
                "hover_text": "Application Info",
                "icon_size": 24
            }
        ]
        
        # Create and store navigation buttons
        self._buttons: List[SidebarButton] = []
        for item in nav_items:
            button = SidebarButton(
                master=self._nav_frame,
                text=item["text"],
                icon=item["icon"],
                width=SIDEBAR_WIDTH - 20,  # Compensate for padding
                height=50,
                corner_radius=4,
                font_size=12,
                hover_text=item["hover_text"],
                icon_size=item["icon_size"]
            )
            button._set_nav_key(item["key"])  # Set internal navigation key
            button.pack(fill="x", pady=2)
            self._buttons.append(button)
            
            # Bind click event
            button.configure(command=lambda key=item["key"]: self._on_navigate(key))
            
            # Store icon name for active state management
            setattr(button, "_nav_icon", item["icon"])

    def _on_navigate(self, key: str) -> None:
        """Handle navigation button click events."""
        logger.debug(f"Sidebar navigation triggered for key: {key}")
        if self._navigate_callback:
            self._navigate_callback(key)
        
        # Update active states
        self._update_active_state(key)
        
    def _update_active_state(self, active_key: str) -> None:
        """Highlight the active navigation button."""
        for button in self._buttons:
            button.set_active(button._nav_key == active_key)
            button.pack_forget()  # Force re-pack to update layout
            button.pack(fill="x", pady=2)
        self._update_hover_state()

    def _update_active_state(self, active_key: str) -> None:
        """Highlight the active navigation button."""
        for button in self._buttons:
            is_active = button._nav_key == active_key
            button.set_active(is_active)
            button.pack_forget()
            button.pack(fill="x", pady=2)

    def set_active_page(self, page_key: str) -> None:
        """Set active page from external navigation system."""
        self._update_active_state(page_key)
        
    def _on_enter(self, event) -> None:
        """Handle mouse enter event."""
        if self._is_toggling:
            return
        self._update_hover_state(hover=True)
        
    def _on_leave(self, event) -> None:
        """Handle mouse leave event."""
        if self._is_toggling:
            return
        self._update_hover_state(hover=False)
        
    def _update_hover_state(self, hover: bool = False) -> None:
        """Update visual state based on hover."""
        for button in self._buttons:
            if hover:
                # Highlight on hover (only works when expanded)
                if self._is_expanded:
                    button.configure(fg_color=getattr(theme_manager.get_color, "sidebar_button_hover_bg", "#3A3A3A"))
                    button._hover_state = True
            else:
                if hover is False and not self._is_expanded:
                    continue
                button.configure(fg_color=theme_manager.get_color("sidebar_button_bg", "#2B2B2B"))
                button._hover_state = False

    def _on_configure(self, event) -> None:
        """Handle widget resize events."""
        if event.widget == self and not self._is_toggling:
            self._current_height = event.height
            logger.debug(f"Sidebar resize detected: {self._current_height}")

    def toggle(self) -> None:
        """
        Toggle between expanded and collapsed states with animation.
        Starts animation sequence using master.after() for smooth timing.
        """
        if self._is_toggling or not self._is_expanded:
            return  # Prevent multiple toggles
            
        self._is_toggling = True
        self._animation_start_time = time.time()
        self._animate_toggle()

    def _animate_toggle(self) -> None:
        """Perform smooth width animation between expanded and collapsed states."""
        current_time = time.time()
        elapsed = current_time - self._animation_start_time
        progress = min(elapsed / (SIDEBAR_ANIMATION_SPEED / 1000), 1.0)
        
        # Determine target width
        target_width = self._get_target_width()
        current_width = self.winfo_width()
        
        # Calculate new width based on animation progress
        if self._is_expanded:
            new_width = self._interpolate_width(current_width, target_width, progress)
        else:
            new_width = self._interpolate_width(current_width, target_width, progress)
        
        # Apply new width
        self._set_expanded_state(progress > 0.9)
        self.configure(width=new_width)
        
        # Check if animation is complete
        if progress < 1.0:
            # Continue animation via after()
            self.after(10, self._animate_toggle)
        else:
            # Animation complete - finalize state
            self._finalize_toggle()

    def _get_target_width(self) -> int:
        """Return target width based on current expanded state."""
        return SIDEBAR_COLLAPSED_WIDTH if self._is_expanded else SIDEBAR_WIDTH

    def _interpolate_width(self, current: int, target: int, progress: float) -> int:
        """Interpolate between current and target width based on progress."""
        delta = target - current
        return current + int(delta * progress)

    def _set_expanded_state(self, is_expanded: bool) -> None:
        """Set internal state and update layout."""
        self._is_expanded = is_expanded
        self._update_visibility()
        
    def _update_visibility(self) -> None:
        """Update visibility of text labels in collapsed state."""
        for button in self._buttons:
            text_widget = getattr(button, '_text_widget', None)
            if text_widget:
                text_widget.pack_forget() if self._is_expanded else text_widget.pack(side="left", expand=True)
            else:
                # Find text widget in button's children
                for child in button.winfo_children():
                    if isinstance(child, customtkinter.CTkLabel) and child.cget("text"):
                        text_widget = child
                        text_widget.pack_forget() if self._is_expanded else text_widget.pack(side="left", expand=True)

    def _finalize_toggle(self) -> None:
        """Complete toggle animation and reset state."""
        self._is_toggling = False
        # Ensure layout is updated
        self.pack_propagate()
        logger.debug(f"Sidebar animation complete. Expanded: {self._is_expanded}")

    def _update_hover_state(self) -> None:
        """Update visual states after layout changes."""
        if self._is_expanded:
            for button in self._buttons:
                button.pack_forget()
                button.pack(fill="x", pady=2)
                button._hover_state = False
        else:
            pass  # Collapsed state handles visibility internally

    def _on_configure(self, event) -> None:
        """Handle widget resize events to maintain layout integrity."""
        if event.widget == self and not self._is_toggling:
            self._current_height = event.height
            self._current_width = event.width