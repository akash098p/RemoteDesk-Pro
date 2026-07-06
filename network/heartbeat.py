"""
===============================================================================
RemoteDesk Pro
File: network/heartbeat.py
Implements heartbeat mechanism for connection monitoring.
Uses ping/pong messages to test connection liveness.
===============================================================================
"""

from __future__ import annotations

import time
import threading
from typing import Optional, Callable

from core.logger import logger
from network.protocol import MessageFactory, RemoteDeskMessage
from network.packet_system import serialize_message, deserialize_message


class Heartbeat:
    """
    Manages heartbeat mechanism for detecting connection liveness.
    Sends periodic ping messages and expects pong responses.
    """
    
    def __init__(
        self,
        interval: float = 30.0,  # seconds
        timeout: float = 60.0,   # seconds
        on_timeout: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize heartbeat manager.
        
        Args:
            interval: Time between ping messages (seconds)
            timeout: Time to wait for pong before considering connection dead (seconds)
            on_timeout: Callback when heartbeat times out
        """
        self._interval = interval
        self._timeout = timeout
        self._on_timeout = on_timeout
        
        self._last_pong_time: float = 0.0
        self._last_ping_time: float = 0.0
        self._ping_id: Optional[str] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def start(self, send_callback: Callable[[RemoteDeskMessage], bool]) -> None:
        """
        Start the heartbeat mechanism.
        
        Args:
            send_callback: Function to send a RemoteDeskMessage
        """
        with self._lock:
            if self._running:
                logger.warning("Heartbeat is already running.")
                return
            
            self._running = True
            self._send_callback = send_callback
            self._last_pong_time = time.time()
            self._thread = threading.Thread(
                target=self._heartbeat_loop,
                name="HeartbeatThread",
                daemon=True
            )
            self._thread.start()
            logger.debug("Heartbeat started.")
    
    def stop(self) -> None:
        """Stop the heartbeat mechanism."""
        with self._lock:
            self._running = False
            if self._thread and self._thread.is_alive():
                # Thread will exit when _running becomes False
                pass
            self._thread = None
        logger.debug("Heartbeat stopped.")
    
    def _heartbeat_loop(self) -> None:
        """Main heartbeat loop running in separate thread."""
        while self._running:
            try:
                current_time = time.time()
                
                # Check if we've timed out waiting for pong
                if (current_time - self._last_pong_time) > self._timeout:
                    logger.warning("Heartbeat timeout - no pong received.")
                    if self._on_timeout:
                        self._on_timeout()
                    # Continue trying - don't automatically stop
                
                # Send ping if interval has elapsed
                if (current_time - self._last_ping_time) >= self._interval:
                    self._send_ping()
                
                # Sleep for a short period before checking again
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    def _send_ping(self) -> None:
        """Send a ping message and record the time."""
        try:
            self._ping_id = f"ping-{int(time.time() * 1000)}"
            ping_msg = MessageFactory.create_ping()
            # We could store the ping_id in the message metadata for tracking
            # but for simplicity, we'll just track the time
            success = self._send_callback(ping_msg)
            if success:
                self._last_ping_time = time.time()
                logger.debug(f"Sent ping {self._ping_id}")
            else:
                logger.error("Failed to send ping message.")
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
    
    def handle_pong(self, pong_msg: RemoteDeskMessage) -> None:
        """Handle incoming pong message."""
        try:
            self._last_pong_time = time.time()
            ping_id = pong_msg.payload.get("ping_id")
            response_time = pong_msg.payload.get("response_time", 0)
            logger.debug(f"Received pong for {ping_id} (response time: {response_time:.3f}s)")
        except Exception as e:
            logger.error(f"Error handling pong message: {e}")
    
    def is_alive(self) -> bool:
        """
        Check if connection is considered alive based on heartbeat.
        
        Returns:
            True if connection appears alive, False otherwise
        """
        with self._lock:
            return (time.time() - self._last_pong_time) < self._timeout
    
    def get_stats(self) -> dict:
        """
        Get heartbeat statistics.
        
        Returns:
            Dictionary with heartbeat stats
        """
        with self._lock:
            return {
                "interval": self._interval,
                "timeout": self._timeout,
                "last_ping_time": self._last_ping_time,
                "last_pong_time": self._last_pong_time,
                "time_since_last_pong": time.time() - self._last_pong_time,
                "is_alive": self.is_alive(),
                "running": self._running
            }


# Convenience function for creating a heartbeat instance
def create_heartbeat(
    interval: float = 30.0,
    timeout: float = 60.0,
    on_timeout: Optional[Callable[[], None]] = None,
) -> Heartbeat:
    """
    Create a Heartbeat instance.
    
    Args:
        interval: Time between ping messages (seconds)
        timeout: Time to wait for pong before considering connection dead (seconds)
        on_timeout: Callback when heartbeat times out
        
    Returns:
        Configured Heartbeat instance
    """
    return Heartbeat(interval=interval, timeout=timeout, on_timeout=on_timeout)