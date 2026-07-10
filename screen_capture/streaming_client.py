"""
===============================================================================
RemoteDesk Pro
File: screen_capture/streaming_client.py
Receives and displays shared screen content
===============================================================================
"""

from __future__ import annotations

import threading
import time
from typing import Optional, Callable

import customtkinter
from PIL import Image
import io

from core.logger import logger


class StreamingClient:
    """
    Receives and displays shared screen content.
    Handles frame buffering and UI updates.
    """

    def __init__(
        self,
        display_widget: Optional[customtkinter.CTkLabel] = None,
        on_frame_received: Optional[Callable[[Image.Image], None]] = None,
    ) -> None:
        """
        Initialize streaming client.

        Args:
            display_widget: CTkLabel widget to display frames
            on_frame_received: Callback for processed frames
        """
        self._display_widget = display_widget
        self._on_frame_received = on_frame_received

        self._running = False
        self._frame_buffer: Optional[bytes] = None
        self._lock = threading.Lock()
        self._frame_count = 0
        self._fps_counter = 0
        self._last_fps_time = time.time()
        self._current_fps = 0

        # Display update thread
        self._display_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the streaming client."""
        if self._running:
            return

        self._running = True
        self._display_thread = threading.Thread(
            target=self._display_loop,
            name="StreamDisplayThread",
            daemon=True
        )
        self._display_thread.start()

        logger.info("Streaming client started")

    def stop(self) -> None:
        """Stop the streaming client."""
        self._running = False
        if self._display_thread and self._display_thread.is_alive():
            self._display_thread.join(timeout=2.0)
        logger.info("Streaming client stopped")

    def receive_frame(self, frame_bytes: bytes) -> None:
        """
        Receive a new frame from the network.

        Args:
            frame_bytes: JPEG-encoded frame bytes
        """
        try:
            with self._lock:
                self._frame_buffer = frame_bytes
                self._frame_count += 1

                # Calculate FPS
                current_time = time.time()
                self._fps_counter += 1
                if current_time - self._last_fps_time >= 1.0:
                    self._current_fps = self._fps_counter
                    self._fps_counter = 0
                    self._last_fps_time = current_time

        except Exception as e:
            logger.error(f"Frame receive error: {e}")

    def _display_loop(self) -> None:
        """Continuously update display with latest frame."""
        while self._running:
            try:
                frame = None
                with self._lock:
                    if self._frame_buffer:
                        frame = self._frame_buffer
                        self._frame_buffer = None

                if frame and self._display_widget:
                    self._update_display(frame)

                time.sleep(0.016)  # ~60 FPS display update

            except Exception as e:
                logger.error(f"Display loop error: {e}")

    def _update_display(self, frame_bytes: bytes) -> None:
        """
        Decode and display frame in the UI.

        Args:
            frame_bytes: JPEG frame bytes
        """
        try:
            # Decode JPEG
            img = Image.open(io.BytesIO(frame_bytes))

            # Resize to fit display widget if needed
            if self._display_widget:
                widget_width = self._display_widget.winfo_width()
                widget_height = self._display_widget.winfo_height()

                if widget_width > 1 and widget_height > 1:
                    img.thumbnail((widget_width, widget_height), Image.LANCZOS)

            # Convert to CTkImage
            ctk_image = customtkinter.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )

            # Update widget on the main thread
            if self._display_widget:
                def update_widget() -> None:
                    try:
                        self._display_widget.configure(image=ctk_image)
                        self._display_widget._current_image = ctk_image
                    except Exception:
                        self._display_widget.configure(image=ctk_image)
                        self._display_widget._current_image = ctk_image

                try:
                    self._display_widget.after(0, update_widget)
                except Exception:
                    self._display_widget.configure(image=ctk_image)
                    self._display_widget._current_image = ctk_image

            # Callback if provided
            if self._on_frame_received:
                self._on_frame_received(img)

        except Exception as e:
            logger.error(f"Display update error: {e}")

    def get_fps(self) -> int:
        """Get current display FPS."""
        return self._current_fps

    def get_stats(self) -> dict:
        """Get client statistics."""
        return {
            "frames_received": self._frame_count,
            "current_fps": self._current_fps,
            "running": self._running,
            "buffer_size": len(self._frame_buffer) if self._frame_buffer else 0
        }

    def destroy(self) -> None:
        """Clean up resources."""
        self.stop()