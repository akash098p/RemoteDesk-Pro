"""
===============================================================================
RemoteDesk Pro
File: audio/audio_capture.py
Real-time audio capture for streaming
===============================================================================
"""

import threading
import time
import queue
import logging
from typing import Optional, Callable

import pyaudio

logger = logging.getLogger(__name__)

class AudioCapture:
    """
    Audio capture class for capturing screen content for remote sharing
    """
    
    def __init__(
        self,
        fps: int = 30,
        quality: int = 50,
        on_frame: Optional[Callable[[bytes], None]] = None,
        connection_manager: Optional[Any] = None
    ) -> None:
        self._fps = fps
        self._quality = quality
        self._on_frame = on_frame
        self._connection_manager = connection_manager
        self._running = False
        self._capture_thread: Optional[threading.Thread] = None
        self._monitor = None
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start screen capture"""
        if self._running:
            return True
            
        try:
            self._running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop,
                name="ScreenCaptureThread",
                daemon=True
            )
            self._capture_thread.start()
            logger.info(f"Screen capture started at {self._fps} FPS")
            return True
        except Exception as e:
            logger.error(f"Failed to start screen capture: {e}")
            return False

    def _capture_loop(self):
        """Main capture loop"""
        from mss import mss
        
        while self._running:
            try:
                # Capture screen
                with mss.mss() as sct:
                    screenshot = sct.grab(self._monitor)
                    
                    # Convert to PIL Image
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    
                    # Encode as JPEG
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=self._quality)
                    frame_bytes = buf.getvalue()
                    
                    # Send to connection manager
                    if self._connection_manager:
                        self._connection_manager.send_screen_frame(frame_bytes)
                    
                    # Call user callback
                    if self._on_frame:
                        self._on_frame(frame_bytes)
                        
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0.0, 1.0 / self._fps - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Capture loop error: {e}")
                self._running = False

    def stop(self):
        """Stop screen capture"""
        self._running = False
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
        logger.info("Screen capture stopped")

    def _capture_loop(self):
        """Main capture loop"""
        mss_instance = mss.mss()
        self._monitor = mss_instance.monitors[0]  # Use primary monitor
        
        while self._running:
            try:
                start_time = time.time()
                screenshot = mss_instance.grab(self._monitor)
                
                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "BGRX")
                
                # Encode as JPEG
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=self._quality)
                frame_data = buf.getvalue()
                
                # Send frame
                if self._connection_manager:
                    self._connection_manager.send_screen_frame(frame_data)
                    
                # Call user callback
                if self._on_frame:
                    self._on_frame(frame_bytes)
                    
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, 1.0 / self._fps - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Capture error: {e}")
                self._running = False

    def set_fps(self, fps: int) -> None:
        """Change capture FPS"""
        self._fps = max(1, min(60, fps))
        
    def set_quality(self, quality: int) -> None:
        """Set quality level"""
        self._quality = max(1, min(100, quality))
        
    def set_monitor(self, monitor_index: int) -> bool:
        """Set which monitor to capture"""
        try:
            mss_instance = mss.mss()
            if monitor_index == 0:
                self._monitor = mss_instance.monitors[0]
            elif 1 <= monitor_index < len(mss_instance.monitors):
                self._monitor = mss_instance.monitors[monitor_index]
            else:
                return False
            return True
        except:
            return False

    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """Capture specific screen region"""
        try:
            with mss.mss() as mss_instance:
                region = {"top": y, "left": x, "width": width, "height": height}
                screenshot = mss_instance.grab(region)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "BGRX")
                
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=self._quality)
                return buf.getvalue()
        except Exception as e:
            logger.error(f"Region capture error: {e}")
            return None