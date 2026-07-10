"""
===============================================================================
RemoteDesk Pro
File: streaming\screen_receiver.py
Handles receiving and displaying shared screen content
===============================================================================
"""

from __future__ import annotations

import threading
import time
from typing import Optional, Callable, Dict, Any

import customtkinter
from PIL import Image
import io
import logging
from core.logger import logger

logger = logging.getLogger(__name__)

class ScreenReceiver:
    """
    Receives and displays shared screen content.
    Manages frame buffering, FPS calculation, and UI updates.
    """

    def __init__(
        self,
        display_widget: Optional[customtkinter.CTkLabel] = None,
        on_frame_received: Optional[Callable[[Image.Image], None]] = None,
    ) -> None:
        """
        Initialize screen receiver.

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
        self._frame_queue: list = []

    def start(self) -> None:
        """Start the receiver"""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(
            target=self._receive_loop,
            name="ScreenReceiverThread",
            daemon=True
        )
        self._thread.start()
        logger.info("Screen receiver started")

    def stop(self) -> None:
        """Stop the receiver"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Screen receiver stopped")

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

    def _receive_loop(self) -> None:
        """Thread loop to receive frames"""
        while self._running:
            try:
                # In a real implementation, this would receive frames from network
                # For now, simulate receiving frames when they're available
                time.sleep(0.016)  # ~60 FPS
            except Exception as e:
                logger.error(f"Receive loop error: {e}")

    def _update_display(self, frame_bytes: bytes) -> None:
        """
        Update the display with the received frame.

        Args:
            frame_bytes: JPEG frame bytes
        """
        try:
            # Decode JPEG
            img = Image.open(io.BytesIO(frame_bytes))
            
            # Resize if necessary
            if self._display_widget:
                widget_w = self._display_widget.winfo_width()
                widget_h = self._display_widget.winfo_height()
                if widget_w > 1 and widget_h > 1:
                    img.thumbnail((widget_w, widget_h), Image.LANCZOS)
            
            # Create CTkImage
            ctk_image = customtkinter.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )
            
            # Update widget on main thread
            if self._display_widget:
                def update_widget():
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

    def get_current_fps(self) -> int:
        """Get current display FPS"""
        return self._current_fps

    def get_stats(self) -> Dict[str, Any]:
        """Get receiver statistics"""
        with self._lock:
            return {
                "frames_received": self._frame_count,
                "current_fps": self._current_fps,
                "running": self._running,
                "buffer_size": len(self._frame_buffer) if self._frame_buffer else 0
            }

    def destroy(self) -> None:
        """Clean up resources"""
        self.stop()