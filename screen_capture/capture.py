"""
===============================================================================
RemoteDesk Pro
File: screen_capture/capture.py
Implements screen capture functionality using MSS.
Captures screen regions and prepares them for streaming.
===============================================================================
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Tuple, Callable

from PIL import Image
import mss
import mss.tools

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY, MAX_FPS, MIN_FPS
from core.logger import logger
from core.utils import run_in_thread


class ScreenCapture:
    """
    Handles screen capture using MSS library.
    Supports region selection, frame rate control, and quality adjustment.
    """
    
    def __init__(
        self,
        monitor: int = 1,  # Primary monitor by default
        fps: int = DEFAULT_FPS,
        quality: int = DEFAULT_QUALITY,
        on_frame: Optional[Callable[[bytes], None]] = None,
    ) -> None:
        """
        Initialize screen capture.
        
        Args:
            monitor: Monitor index to capture (1 for primary)
            fps: Target frames per second
            quality: JPEG quality (1-100)
            on_frame: Callback for processed frame (bytes)
        """
        self._monitor_index = monitor
        self._fps = fps
        self._quality = quality
        self._on_frame = on_frame
        
        self._sct = mss.mss()
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._monitor: Optional[dict] = None
        self._lock = threading.Lock()
        
        self._initialize_monitor()
        
    def _initialize_monitor(self) -> None:
        """Initialize the monitor configuration."""
        try:
            with self._lock:
                if self._monitor_index == 0:
                    # Capture all monitors
                    self._monitor = self._sct.monitors[0]  # All monitors
                else:
                    # Capture specific monitor
                    if self._monitor_index < len(self._sct.monitors):
                        self._monitor = self._sct.monitors[self._monitor_index]
                    else:
                        logger.warning(f"Monitor {self._monitor_index} not found, using primary")
                        self._monitor = self._sct.monitors[1]  # Primary monitor
        except Exception as e:
            logger.error(f"Monitor initialization error: {e}")
            self._monitor = self._sct.monitors[1] if len(self._sct.monitors) > 1 else self._sct.monitors[0]
    
    def start(self) -> bool:
        """
        Start the screen capture loop.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self._running:
                logger.warning("Screen capture is already running")
                return True
            
            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                name="ScreenCaptureThread",
                daemon=True
            )
            self._capture_thread.start()
            
            logger.info(f"Screen capture started (monitor={self._monitor_index}, fps={self._fps})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start screen capture: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the screen capture loop."""
        self._running = False
        logger.info("Screen capture stopped")
    
    def _capture_loop(self) -> None:
        """Main capture loop running in separate thread."""
        frame_interval = 1.0 / self._fps
        
        while self._running:
            try:
                start_time = time.time()
                
                # Capture frame
                frame = self._capture_frame()
                
                # Send frame via callback
                if frame and self._on_frame:
                    self._on_frame(frame)
                
                # Maintain frame rate
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
    
    def _capture_frame(self) -> Optional[bytes]:
        """
        Capture a single frame from the screen.
        
        Returns:
            JPEG-encoded frame bytes or None on error
        """
        try:
            with self._lock:
                if not self._monitor:
                    self._initialize_monitor()
                
                # Capture screen region
                screenshot = self._sct.grab(self._monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGR")
                
                # Compress to JPEG
                import io
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=self._quality)
                frame_bytes = buffer.getvalue()
                
                return frame_bytes
                
        except Exception as e:
            logger.error(f"Frame capture error: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """
        Capture a specific region of the screen.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Region width
            height: Region height
            
        Returns:
            JPEG-encoded frame bytes or None on error
        """
        try:
            region = {"top": y, "left": x, "width": width, "height": height}
            screenshot = self._sct.grab(region)
            
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGR")
            
            import io
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=self._quality)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Region capture error: {e}")
            return None
    
    def set_fps(self, fps: int) -> None:
        """Set the target frames per second."""
        self._fps = max(MIN_FPS, min(MAX_FPS, fps))
        logger.debug(f"Updated FPS to {self._fps}")
    
    def set_quality(self, quality: int) -> None:
        """Set the JPEG compression quality."""
        self._quality = max(1, min(100, quality))
        logger.debug(f"Updated quality to {self._quality}")
    
    def get_stats(self) -> dict:
        """Get current capture statistics."""
        return {
            "monitor_index": self._monitor_index,
            "fps": self._fps,
            "quality": self._quality,
            "running": self._running,
            "monitor": self._monitor
        }
    
    def destroy(self) -> None:
        """Clean up resources."""
        self.stop()
        try:
            self._sct.close()
        except:
            pass


# Convenience function
def create_screen_capture(
    fps: int = DEFAULT_FPS,
    quality: int = DEFAULT_QUALITY,
    on_frame: Optional[Callable[[bytes], None]] = None,
) -> ScreenCapture:
    """
    Create a ScreenCapture instance.
    
    Args:
        fps: Target frames per second
        quality: JPEG quality (1-100)
        on_frame: Callback for processed frames
        
    Returns:
        Configured ScreenCapture instance
    """
    return ScreenCapture(fps=fps, quality=quality, on_frame=on_frame)