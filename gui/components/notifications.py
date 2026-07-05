"""
===============================================================================
RemoteDesk Pro
File: gui/components/notifications.py
Display non-intrusive notification pop-ups (toasts) on the screen.
Supports stacking, auto-dismissal, and theme integration.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Optional, List, Callable, Any

import customtkinter

from core.constants import (
    NOTIFICATION_DURATION,
    CORNER_RADIUS,
    PADDING,
    FONT_SIZE_BODY,
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()

class NotificationPopup(customtkinter.CTkToplevel):
    """
    A single notification popup/toast.
    
    Features:
    - Semi-transparent background
    - Optional icon and title
    - Auto-dismissal after duration
    - Close button for manual dismissal
    - Theme-aware styling
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str = "",
        message: str = "",
        duration: int = NOTIFICATION_DURATION,
        position: str = "top-right",
        icon_name: Optional[str] = None,
        callback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        
        self._title = title
        self._message = message
        self._duration = duration
        self._position = position
        self._icon_name = icon_name
        self._callback = callback
        self._is_dismissing = False
        
        # Configure window properties
        self.overrideredirect(True)  # Remove OS decorations
        self.attributes("-topmost", True)  # Keep on top
        self.transient(master)  # Attach to parent
        self.configure(fg_color=theme_manager.get_color("notification_bg", "#2D2D2D"))
        
        # Create UI
        self._create_widgets()
        
        # Position and show
        self._position_window()
        self._schedule_dismissal()
        
        # Theme callback
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_widgets(self) -> None:
        """Create notification content widgets."""
        # Main container with padding
        container = customtkinter.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=CORNER_RADIUS,
        )
        container.pack(padx=PADDING, pady=PADDING)
        
        # Header with icon and title
        if self._title or self._icon_name:
            header = customtkinter.CTkFrame(container, fg_color="transparent")
            header.pack(fill="x", pady=(0, PADDING // 2))
            
            # Icon
            if self._icon_name:
                icon = load_image(self._icon_name, size=(18, 18))
                if icon:
                    icon_label = customtkinter.CTkLabel(header, image=icon, text="")
                    icon_label.pack(side="left", padx=(0, PADDING // 2))
            
            # Title
            if self._title:
                title_label = customtkinter.CTkLabel(
                    header,
                    text=self._title,
                    font=customtkinter.CTkFont(family="Inter", size=12, weight="bold"),
                    text_color=theme_manager.get_color("notification_title", "#FFFFFF"),
                )
                title_label.pack(side="left" if self._icon_name else "top", anchor="w")
        
        # Message
        if self._message:
            msg_label = customtkinter.CTkLabel(
                container,
                text=self._message,
                font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
                text_color=theme_manager.get_color("notification_message", "#CCCCCC"),
                wraplength=280,
                justify="left",
            )
            msg_label.pack(fill="x", pady=(0, PADDING // 2))
        
        # Close button
        close_btn = customtkinter.CTkButton(
            container,
            text="✕",
            command=self.dismiss,
            width=20,
            height=20,
            fg_color=theme_manager.get_color("notification_close_bg", "#FF5555"),
            hover_color=theme_manager.get_color("notification_close_hover", "#FF3333"),
            font=customtkinter.CTkFont(size=12),
            text_color="#FFFFFF",
            corner_radius=10,
        )
        close_btn.place(relx=0.95, rely=0.05, anchor="ne")

    def _position_window(self) -> None:
        """Position the notification based on the specified corner."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Default size
        width, height = 320, 100
        
        # Calculate position
        margin = PADDING * 2
        if self._position == "top-left":
            x, y = margin, margin
        elif self._position == "top-center":
            x, y = (screen_width - width) // 2, margin
        elif self._position == "top-right":
            x, y = screen_width - width - margin, margin
        elif self._position == "bottom-left":
            x, y = margin, screen_height - height - margin
        elif self._position == "bottom-center":
            x, y = (screen_width - width) // 2, screen_height - height - margin
        elif self._position == "bottom-right":
            x, y = screen_width - width - margin, screen_height - height - margin
        else:
            x, y = screen_width - width - margin, margin
        
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _schedule_dismissal(self) -> None:
        """Schedule automatic dismissal after the specified duration."""
        if self._duration > 0:
            self.after(self._duration, self.dismiss)

    def dismiss(self) -> None:
        """Dismiss the notification with animation."""
        if self._is_dismissing:
            return
        self._is_dismissing = True
        
        # Fade out effect
        steps = 10
        delay = 20
        alpha = 1.0
        
        def fade_step(step: int) -> None:
            nonlocal alpha
            if step >= steps:
                self.destroy()
                if self._callback:
                    self._callback()
            else:
                alpha -= 1 / steps
                self.attributes("-alpha", max(0.0, alpha))
                self.after(delay, lambda: fade_step(step + 1))
        
        fade_step(0)

    def _on_theme_change(self, theme_name: str) -> None:
        """Update styling when theme changes."""
        self.configure(fg_color=theme_manager.get_color("notification_bg", "#2D2D2D"))

    def destroy(self) -> None:
        """Clean up resources."""
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class NotificationManager:
    """
    Central manager for displaying stacked notifications.
    
    Features:
    - Limits maximum number of concurrent notifications
    - Automatic positioning of stacked notifications
    - Theme integration
    - Easy API for showing different notification types
    """

    _instance: Optional["NotificationManager"] = None

    def __new__(cls) -> "NotificationManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
            
        self._master: Optional[customtkinter.CTk] = None
        self._notifications: List[NotificationPopup] = []
        self._max_notifications = 5
        self._default_duration = NOTIFICATION_DURATION
        self._default_position = "top-right"
        
        theme_manager.register_theme_change_callback(self._on_theme_change)
        self._initialized = True

    def initialize(self, master: customtkinter.CTk) -> None:
        """Initialize with the main application window."""
        self._master = master

    def show(
        self,
        title: str = "",
        message: str = "",
        duration: Optional[int] = None,
        position: Optional[str] = None,
        icon_name: Optional[str] = None,
        callback: Optional[Callable] = None,
    ) -> NotificationPopup:
        """Display a notification."""
        if self._master is None:
            return None
            
        # Enforce max notifications
        if len(self._notifications) >= self._max_notifications:
            oldest = self._notifications.pop(0)
            oldest.dismiss()
        
        # Create and show notification
        notification = NotificationPopup(
            master=self._master,
            title=title,
            message=message,
            duration=duration or self._default_duration,
            position=position or self._default_position,
            icon_name=icon_name,
            callback=callback,
        )
        self._notifications.append(notification)
        
        # Remove from list when dismissed
        def on_dismiss():
            if notification in self._notifications:
                self._notifications.remove(notification)
        
        notification._callback = on_dismiss
        
        return notification

    def show_info(self, message: str, title: str = "Info") -> NotificationPopup:
        """Show an informational notification."""
        return self.show(title=title, message=message)

    def show_success(self, message: str, title: str = "Success") -> NotificationPopup:
        """Show a success notification."""
        return self.show(title=title, message=message, icon_name="check-circle.svg")

    def show_warning(self, message: str, title: str = "Warning") -> NotificationPopup:
        """Show a warning notification."""
        return self.show(title=title, message=message, icon_name="alert-triangle.svg")

    def show_error(self, message: str, title: str = "Error") -> NotificationPopup:
        """Show an error notification."""
        return self.show(title=title, message=message, icon_name="x-circle.svg")

    def clear_all(self) -> None:
        """Dismiss all active notifications."""
        for notification in self._notifications[:]:
            notification.dismiss()
        self._notifications.clear()

    def _on_theme_change(self, theme_name: str) -> None:
        """Handle theme change events."""
        pass  # Styling is updated in each notification

    @classmethod
    def get_instance(cls) -> "NotificationManager":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Convenience functions
def show_notification(
    title: str = "",
    message: str = "",
    duration: Optional[int] = None,
    position: Optional[str] = None,
    icon_name: Optional[str] = None,
) -> NotificationPopup:
    """Show a notification using the global manager."""
    return NotificationManager.get_instance().show(
        title=title,
        message=message,
        duration=duration,
        position=position,
        icon_name=icon_name,
    )


if __name__ == "__main__":
    # Demo
    demo = customtkinter.CTk()
    demo.geometry("400x300")
    demo.title("Notification Demo")
    
    def test_notifications():
        nm = NotificationManager.get_instance()
        nm.initialize(demo)
        nm.show_info("This is an info message", "Information")
        demo.after(500, lambda: nm.show_success("Operation completed!", "Success"))
        demo.after(1500, lambda: nm.show_warning("Please check your input", "Warning"))
        demo.after(2500, lambda: nm.show_error("An error occurred", "Error"))
    
    btn = customtkinter.CTkButton(demo, text="Show Notifications", command=test_notifications)
    btn.pack(pady=50)
    
    demo.mainloop()