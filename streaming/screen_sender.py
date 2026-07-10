"""
===============================================================================
RemoteDesk Pro
File: streaming\screen_sender.py
Handles capturing and sending screen content
===============================================================================
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Callable

import mss
from PIL import Image
import io
import logging
from core.logger import logger

logger = logging.getLogger(__name__)

class ScreenSender:
    """
    Captures and sends screen content to connected clients.
    Uses MSS for cross-platform screen capture.
    """

    def __init__(
        self,
        fps: int = 30,
        quality: int = 50,
        on_frame: Optional[Callable[[bytes], None]] = None,
    ) -> None:
        """
        Initialize screen sender.

        Args:
            fps: Frames per second to capture
            quality: JPEG quality (1-100)
            on_frame: Callback function for captured frames
        """
        self._fps = fps
        self._quality = quality
        self._on_frame = on_frame
        self._running = False
        self._monitor: Optional[dict] = None
        self._capture_thread: Optional[threading.Thread] = None

    def start(self, monitor_index: int = 0) -> bool:
        """
        Start capturing and sending screen frames.

        Args:
            monitor_index: Monitor index (0 = primary)

        Returns:
            True if started successfully
        """
        if self._running:
            logger.warning("Screen sender is already running")
            return True

        try:
            # Initialize monitor
            mss_instance = mss.mss()
            if monitor_index == 0:
                self._monitor = mss_instance.monitors[0]
            elif 1 <= monitor_index < len(mss_instance.monitors):
                self._monitor = mss_instance.monitors[monitor_index]
            else:
                self._monitor = mss_instance.monitors[0]

            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                name="ScreenSenderThread",
                daemon=True
            )
            self._capture_thread.start()
            logger.info(f"Screen sender started at {self._fps} FPS")
            return True
        except Exception as e:
            logger.error(f"Failed to start screen sender: {e}")
            return False

    def stop(self) -> None:
        """Stop capturing screen frames"""
        self._running = False
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
        logger.info("Screen sender stopped")

    def _capture_loop(self) -> None:
        """Main capture loop"""
        mss_instance = mss.mss()
        
        try:
            while self._running:
                start_time = time.time()

                # Capture screen
                screenshot = mss_instance.grab(self._monitor)
                
                # Convert to PIL Image
                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.rgb,
                    raw="BGR"
                )

                # Compress to JPEG
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=self._quality)
                frame_bytes = img_bytes.getvalue()

                # Send frame via callback
                if self._on_frame:
                    try:
                        self._on_frame(frame_bytes)
                    except Exception as e:
                        logger.error(f"Error in on_frame callback: {e}")

                # Maintain target FPS
                elapsed = time.time() - start_time
                sleep_time = max(0.0, 1.0 / self._fps - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Error in capture loop: {e}")
            self._running = False

    def set_fps(self, fps: int) -> None:
        """Set capture frame rate"""
        self._fps = max(1, min(60, fps))

    def set_quality(self, quality: int) -> None:
        """Set JPEG quality"""
        self._quality = max(1, min(100, quality))

    def is_running(self) -> bool:
        """Check if sender is running"""
        return self._running

    def get_stats(self) -> dict:
        """Get capture statistics"""
        return {
            "fps": self._fps,
            "quality": self._quality,
            "running": self._running,
            "monitor": self._monitor
        }