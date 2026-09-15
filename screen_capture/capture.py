"""
===============================================================================
RemoteDesk Pro
File: screen_capture/capture.py
Real-time desktop screen capture used by the streaming server.
===============================================================================
"""

from __future__ import annotations

import io
import threading
import time
from typing import Any, Callable, Optional

import mss
from PIL import Image

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger

logger = get_logger()


class ScreenCapture:
    """Capture the desktop and deliver encoded frames to a callback."""

    def __init__(
        self,
        fps: int = DEFAULT_FPS,
        quality: int = DEFAULT_QUALITY,
        on_frame: Optional[Callable[[bytes], None]] = None,
        connection_manager: Optional[Any] = None,
        monitor_index: int = 0,
    ) -> None:
        self._fps = max(1, min(60, int(fps)))
        self._quality = max(1, min(100, int(quality)))
        self._on_frame = on_frame
        self._connection_manager = connection_manager
        self._monitor_index = monitor_index
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._monitor: Optional[dict] = None
        self._lock = threading.Lock()
        self._frames_captured = 0
        self._last_error: Optional[str] = None
        self._monitor_width = 0
        self._monitor_height = 0

    # ------------------------------------------------------------------ state
    def is_running(self) -> bool:
        """Return True while the capture thread is active."""
        return self._running

    def get_stats(self) -> dict:
        """Return runtime statistics for this capture instance."""
        return {
            "running": self._running,
            "fps": self._fps,
            "quality": self._quality,
            "monitor_index": self._monitor_index,
            "frames_captured": self._frames_captured,
            "last_error": self._last_error,
        }

    # ------------------------------------------------------------- lifecycle
    def start(self) -> bool:
        """Start capturing frames on a background thread."""
        with self._lock:
            if self._running:
                return True

            try:
                self._monitor = self._resolve_monitor(self._monitor_index)
            except Exception as exc:
                self._last_error = f"Unable to open screen capture device: {exc}"
                logger.error(self._last_error)
                return False

            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                name="ScreenCaptureThread",
                daemon=True,
            )
            self._capture_thread.start()
            logger.info(f"Screen capture started at {self._fps} FPS (quality {self._quality})")
            return True

    def stop(self) -> None:
        """Stop capturing and wait briefly for the capture thread to finish."""
        self._running = False
        thread = self._capture_thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self._capture_thread = None
        logger.info("Screen capture stopped")

    def destroy(self) -> None:
        """Stop capture and release resources."""
        self.stop()
        self._monitor = None
        self._on_frame = None

    # -------------------------------------------------------------- controls
    def set_fps(self, fps: int) -> None:
        """Change the capture frame rate (clamped to a sane range)."""
        self._fps = max(1, min(60, int(fps)))

    def set_quality(self, quality: int) -> None:
        """Change the encoding quality (clamped to a sane range)."""
        self._quality = max(1, min(100, int(quality)))

    def set_monitor(self, monitor_index: int) -> bool:
        """Select which monitor to capture. Index 0 captures everything."""
        try:
            monitor = self._resolve_monitor(monitor_index)
        except Exception as exc:
            self._last_error = f"Unable to select monitor {monitor_index}: {exc}"
            logger.error(self._last_error)
            return False

        self._monitor = monitor
        self._monitor_index = monitor_index
        return True

    # ------------------------------------------------------------- utilities
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """Capture and encode a single screen region."""
        try:
            with mss.mss() as capture_device:
                screenshot = capture_device.grab(
                    {"top": y, "left": x, "width": width, "height": height}
                )
                return self._encode(self._to_image(screenshot))
        except Exception as exc:
            self._last_error = f"Region capture failed: {exc}"
            logger.error(self._last_error)
            return None

    def _resolve_monitor(self, monitor_index: int) -> dict:
        """Return the mss monitor description for the requested index."""
        with mss.mss() as capture_device:
            monitors = capture_device.monitors
            if monitor_index < 0 or monitor_index >= len(monitors):
                raise ValueError(
                    f"Monitor index {monitor_index} is out of range "
                    f"(available: 0-{len(monitors) - 1})"
                )
            return dict(monitors[monitor_index])

    @staticmethod
    def _to_image(screenshot: Any) -> Image.Image:
        """Convert an mss screenshot into a PIL RGB image."""
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "BGRX")

    def _encode(self, image: Image.Image) -> bytes:
        """Encode a PIL image as JPEG bytes."""
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=self._quality)
        return buffer.getvalue()

    def _deliver(self, frame_data: bytes) -> None:
        """Forward a captured frame to the connection manager and the callback."""
        if self._connection_manager is not None:
            try:
                self._connection_manager.send_screen_frame(
                    frame_data,
                    metadata={"width": self._monitor_width, "height": self._monitor_height},
                )
            except Exception as exc:
                logger.error(f"Failed to send captured frame: {exc}")

        if self._on_frame is not None:
            try:
                self._on_frame(frame_data)
            except Exception as exc:
                logger.error(f"Screen capture callback failed: {exc}")

    def _capture_loop(self) -> None:
        """Capture frames until stopped, maintaining the target frame rate."""
        monitor = self._monitor
        if monitor is None:
            self._running = False
            return

        self._monitor_width = int(monitor.get("width", 0))
        self._monitor_height = int(monitor.get("height", 0))

        try:
            with mss.mss() as capture_device:
                while self._running:
                    start_time = time.time()
                    try:
                        screenshot = capture_device.grab(monitor)
                    except Exception as exc:
                        self._last_error = f"Screen capture failed: {exc}"
                        logger.error(self._last_error)
                        break

                    try:
                        self._deliver(self._encode(self._to_image(screenshot)))
                        self._frames_captured += 1
                    except Exception as exc:
                        logger.error(f"Frame encoding failed: {exc}")

                    delay = (1.0 / self._fps) - (time.time() - start_time)
                    if delay > 0:
                        time.sleep(delay)
        finally:
            self._running = False


def create_screen_capture(
    fps: int = DEFAULT_FPS,
    quality: int = DEFAULT_QUALITY,
    on_frame: Optional[Callable[[bytes], None]] = None,
    connection_manager: Optional[Any] = None,
    monitor_index: int = 0,
) -> ScreenCapture:
    """Create a configured :class:`ScreenCapture` instance."""
    return ScreenCapture(
        fps=fps,
        quality=quality,
        on_frame=on_frame,
        connection_manager=connection_manager,
        monitor_index=monitor_index,
    )
