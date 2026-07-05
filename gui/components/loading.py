"""
===============================================================================
RemoteDesk Pro
File: gui/components/loading.py

Reusable loading spinner and overlay components for visual feedback during
operations. These are non-blocking and theme-aware.
===============================================================================
"""

from __future__ import annotations

from typing import Optional, Callable, Any

import customtkinter

from core.constants import (
    CORNER_RADIUS,
    ICON_SIZE,
    ANIMATION_DURATION,
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()

class LoadingSpinner(customtkinter.CTkCanvas):
    """
    Animated loading spinner widget using a rotating arc on a canvas.
    Perfect for inline loading indicators (e.g., next to a button).
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        size: int = 20,
        thickness: int = 2,
        speed: int = 100,  # milliseconds per frame
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            width=size,
            height=size,
            highlightthickness=0,  # Remove border
            **kwargs,
        )
        self._size = size
        self._thickness = thickness
        self._speed = speed
        self._is_spinning = False
        self._angle = 0

        # Configure colors from theme
        self._color = theme_manager.get_color("primary", "#0084FF")
        
        # Draw initial arc (invisible rotation)
        self._arc = self.create_arc(
            self._thickness, self._thickness,
            self._size - self._thickness, self._size - self._thickness,
            start=0, extent=0,
            style="arc",
            outline=self._color,
            width=self._thickness,
        )

        # Register theme callback
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _on_theme_change(self, theme_name: str) -> None:
        """Update spinner color on theme change."""
        self._color = theme_manager.get_color("primary", "#0084FF")
        self.itemconfig(self._arc, outline=self._color)

    def start(self) -> None:
        """Start the spinner animation."""
        if not self._is_spinning:
            self._is_spinning = True
            self._animate()

    def stop(self) -> None:
        """Stop the spinner animation."""
        self._is_spinning = False

    def _animate(self) -> None:
        """Perform one frame of the spinner animation."""
        if not self._is_spinning:
            return
            
        self._angle = (self._angle + 10) % 360
        self.itemconfig(self._arc, extent=self._angle % 360)
        
        # Continue animation
        self.after(self._speed, self._animate)

    def destroy(self) -> None:
        """Clean up resources."""
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class LoadingOverlay(customtkinter.CTkFrame):
    """
    Full-window overlay that shows a centered loading spinner with optional
    text and blocks interaction with the underlying widgets (modal).
    Usage:
        overlay = LoadingOverlay(main_window)
        overlay.show()
        # ... long operation ...
        overlay.hide()
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        text: str = "Loading...",
        show_spinner: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            master,
            fg_color=f"{theme_manager.get_color('background', '#0D0D0D')}AA",  # Semi-transparent
            corner_radius=0,
            **kwargs,
        )
        self._text = text
        self._is_visible = False
        self._text_id = None
        self._spinner = None

        # Create UI
        self._create_ui()

        # Register theme callback
        theme_manager.register_theme_change_callback(self._on_theme_change)

    def _create_ui(self) -> None:
        """Create the visual elements of the overlay."""
        # Center frame
        center_frame = customtkinter.CTkFrame(
            self,
            fg_color=theme_manager.get_color("surface", "#1A1A1A"),
            corner_radius=CORNER_RADIUS + 4,
        )
        center_frame.place(
            relx=0.5, rely=0.5,
            anchor="center",
            relwidth=0.3,
            relheight=0.2,
        )

        # Spinner
        self._spinner = LoadingSpinner(
            center_frame,
            size=32,
            thickness=3,
        )
        self._spinner.pack(pady=(20, 10))

        # Loading text
        self._text_label = customtkinter.CTkLabel(
            center_frame,
            text=self._text,
            font=customtkinter.CTkFont(family="Inter", size=14),
            text_color=theme_manager.get_color("text_primary", "#FFFFFF"),
        )
        self._text_label.pack()

    def _on_theme_change(self, theme_name: str) -> None:
        """Update overlay colors on theme change."""
        self.configure(
            fg_color=f"{theme_manager.get_color('background', '#0D0D0D')}AA"
        )
        self._text_label.configure(
            text_color=theme_manager.get_color("text_primary", "#FFFFFF")
        )

    def show(self) -> None:
        """Display the overlay, blocking parent interaction."""
        if not self._is_visible:
            self._is_visible = True
            self.place(
                relx=0, rely=0,
                relwidth=1, relheight=1,
            )
            self.lift()
            self.grab_set()  # Make modal
            if self._spinner:
                self._spinner.start()

    def hide(self) -> None:
        """Hide the overlay and restore interaction."""
        if self._is_visible:
            self._is_visible = False
            if self._spinner:
                self._spinner.stop()
            self.grab_release()
            self.place_forget()

    def set_text(self, text: str) -> None:
        """Update loading text dynamically."""
        self._text = text
        if self._text_label:
            self._text_label.configure(text=text)

    def destroy(self) -> None:
        """Clean up resources."""
        if self._spinner:
            self._spinner.stop()
        theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()


class AsyncLoader:
    """
    Helper class that wraps long-running operations with a loading overlay.
    Usage example:
        async_loader = AsyncLoader(main_window, "Processing files...")
        def heavy_task():
            # Do work here
            time.sleep(5)
        async_loader.execute(heavy_task)
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        text: str = "Loading...",
        callback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        self._master = master
        self._text = text
        self._callback = callback
        self._overlay = LoadingOverlay(master, text=text, **kwargs)

    def execute(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """Execute function with loading overlay."""
        import threading
        
        def run_task():
            try:
                result = func(*args, **kwargs)
                if self._callback:
                    self._callback(result)
            finally:
                self._overlay.hide()

        self._overlay.show()
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()


# Convenience functions
def show_loading(master: customtkinter.CTk, text: str = "Loading...") -> LoadingOverlay:
    """Create and show a loading overlay."""
    overlay = LoadingOverlay(master, text=text)
    overlay.show()
    return overlay

def hide_loading(overlay: LoadingOverlay) -> None:
    """Hide a loading overlay."""
    overlay.hide()


if __name__ == "__main__":
    # Demo for visual testing
    demo = customtkinter.CTk()
    demo.title("Loading Components Demo")
    demo.geometry("600x400")

    # Inline spinner
    spinner = LoadingSpinner(demo, size=30)
    spinner.pack(pady=20)
    spinner.start()

    # Overlay demo
    def test_overlay():
        overlay = LoadingOverlay(demo, text="Please wait...")
        overlay.show()
        demo.after(3000, overlay.hide)

    btn = customtkinter.CTkButton(
        demo,
        text="Show Loading Overlay",
        command=test_overlay,
    )
    btn.pack(pady=20)

    demo.mainloop()