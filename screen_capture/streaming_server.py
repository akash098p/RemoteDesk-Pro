"""
===============================================================================
RemoteDesk Pro
File: screen_capture/streaming_server.py
Handles streaming screen capture to connected clients.
Manages frame distribution and compression settings.
===============================================================================
"""

from __future__ import annotations

import time
import threading
import gzip
from typing import Optional, Dict, Callable

from screen_capture.capture import ScreenCapture
from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import logger


class StreamingServer:
    """
    Manages screen streaming to connected clients.
    Handles frame capture, compression, and distribution.
    """
    
    def __init__(
        self,
        fps: int = DEFAULT_FPS,
        quality: int = DEFAULT_QUALITY,
        on_client_join: Optional[Callable[[str], None]] = None,
        on_client_leave: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize streaming server.
        
        Args:
            fps: Target capture frame rate
            quality: JPEG quality for encoding
            on_client_join: Callback when client joins (client_id)
            on_client_leave: Callback when client leaves (client_id)
        """
        self._fps = fps
        self._quality = quality
        self._on_client_join = on_client_join
        self._on_client_leave = on_client_leave
        
        self._capture: Optional[ScreenCapture] = None
        self._clients: Dict[str, dict] = {}  # client_id -> metadata
        self._running = False
        self._lock = threading.Lock()
        self._stream_sender_thread: Optional[threading.Thread] = None
        
    def start(self) -> bool:
        """
        Start the streaming server.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self._running:
                logger.warning("Streaming server is already running")
                return True
            
            self._running = True
            self._capture = ScreenCapture(
                fps=self._fps,
                quality=self._quality,
                on_frame=self._on_frame_captured
            )
            
            if self._capture.start():
                self._stream_sender_thread = threading.Thread(
                    target=self._stream_sender_loop,
                    name="StreamSenderThread",
                    daemon=True
                )
                self._stream_sender_thread.start()
                
                logger.info(f"Streaming server started (fps={self._fps}, quality={self._quality})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to start streaming server: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the streaming server."""
        self._running = False
        if self._capture:
            self._capture.stop()
        logger.info("Streaming server stopped")
    
    def add_client(self, client_id: str, send_callback: Callable) -> None:
        """
        Register a client for receiving stream frames.
        
        Args:
            client_id: Unique client identifier
            send_callback: Function to send frame bytes to client
        """
        with self._lock:
            self._clients[client_id] = {
                "send_callback": send_callback,
                "last_frame_time": time.time(),
                "frame_count": 0
            }
            logger.info(f"Client {client_id} joined stream")
            
            if self._on_client_join:
                self._on_client_join(client_id)
    
    def remove_client(self, client_id: str) -> None:
        """
        Remove a client from the stream.
        
        Args:
            client_id: Client identifier to remove
        """
        with self._lock:
            if client_id in self._clients:
                del self._clients[client_id]
                logger.info(f"Client {client_id} left stream")
                
                if self._on_client_leave:
                    self._on_client_leave(client_id)
    
    def _on_frame_captured(self, frame_bytes: bytes) -> None:
        """
        Store the latest frame for distribution.
        
        Args:
            frame_bytes: Captured frame bytes
        """
        with self._lock:
            self._latest_frame = frame_bytes
            self._latest_frame_time = time.time()
            
            # Update frame counts
            for client_id in self._clients:
                self._clients[client_id]["last_frame_time"] = time.time()
                self._clients[client_id]["frame_count"] += 1
    
    def _stream_sender_loop(self) -> None:
        """Send frames to all connected clients."""
        while self._running:
            try:
                with self._lock:
                    if hasattr(self, '_latest_frame'):
                        for client_id, client_data in list(self._clients.items()):
                            try:
                                client_data["send_callback"](self._latest_frame)
                            except Exception as e:
                                logger.error(f"Error sending to {client_id}: {e}")
                                # Remove unresponsive client
                                del self._clients[client_id]
                                self._on_client_leave(client_id)
                
                time.sleep(0.01)  # Small sleep to prevent busy loop
                
            except Exception as e:
                logger.error(f"Stream sender error: {e}")
    
    def set_fps(self, fps: int) -> None:
        """Set the capture frame rate."""
        self._fps = fps
        if self._capture:
            self._capture.set_fps(fps)
    
    def set_quality(self, quality: int) -> None:
        """Set the capture quality."""
        self._quality = quality
        if self._capture:
            self._capture.set_quality(quality)
    
    def get_stats(self) -> dict:
        """Get streaming statistics."""
        stats = {
            "fps": self._fps,
            "quality": self._quality,
            "running": self._running,
            "client_count": len(self._clients),
        }
        
        if self._capture:
            stats.update(self._capture.get_stats())
        
        return stats
    
    def destroy(self) -> None:
        """Clean up resources."""
        self.stop()
        if self._capture:
            self._capture.destroy()


# Convenience function
def create_streaming_server(
    fps: int = DEFAULT_FPS,
    quality: int = DEFAULT_QUALITY,
) -> StreamingServer:
    """
    Create a StreamingServer instance.
    
    Args:
        fps: Target frame rate
        quality: Capture quality
        
    Returns:
        Configured StreamingServer instance
    """
    return StreamingServer(fps=fps, quality=quality)