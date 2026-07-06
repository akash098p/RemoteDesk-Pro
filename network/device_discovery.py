"""
===============================================================================
RemoteDesk Pro
File: network/device_discovery.py
Implements device discovery for finding remote peers on the network.
Supports both local network discovery and centralized discovery via server.
===============================================================================
"""

from __future__ import annotations

import socket
import threading
import time
from typing import Optional, Callable, Dict, List

from core.constants import DEFAULT_HOST, DEFAULT_PORT
from core.logger import logger


class DeviceDiscovery:
    """
    Handles discovery of remote devices on the local network.
    Uses UDP broadcast for local discovery.
    """
    
    def __init__(
        self,
        port: int = 5001,  # Different port for discovery
        broadcast_address: str = "255.255.255.255",
        on_device_found: Optional[Callable[[dict], None]] = None,
        on_device_lost: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize device discovery.
        
        Args:
            port: UDP port for discovery
            broadcast_address: Broadcast address to send discovery packets
            on_device_found: Callback when a device is discovered (device_info dict)
            on_device_lost: Callback when a device is no longer reachable (client_id)
        """
        self._port = port
        self._broadcast_address = broadcast_address
        self._on_device_found = on_device_found
        self._on_device_lost = on_device_lost
        
        self._running = False
        self._discovery_thread: Optional[threading.Thread] = None
        self._socket: Optional[socket.socket] = None
        self._discovered_devices: Dict[str, dict] = {}
        self._lock = threading.Lock()
    
    def start(self) -> bool:
        """
        Start the discovery service.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._socket.bind(("", self._port))
            self._socket.settimeout(1.0)
            
            self._running = True
            self._discovery_thread = threading.Thread(
                target=self._listen_loop,
                name="DeviceDiscoveryThread",
                daemon=True
            )
            self._discovery_thread.start()
            
            logger.info(f"Device discovery started on port {self._port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start device discovery: {e}")
            return False
    
    def stop(self) -> None:
        """Stop the discovery service."""
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
        logger.info("Device discovery stopped")
    
    def discover(self, timeout: float = 5.0) -> List[dict]:
        """
        Broadcast a discovery request and collect responses.
        
        Args:
            timeout: Time to wait for responses (seconds)
            
        Returns:
            List of discovered device information dictionaries
        """
        discovered = []
        start_time = time.time()
        
        try:
            # Send discovery packet
            discovery_message = b"DISCOVER_REQUEST"
            self._socket.sendto(discovery_message, (self._broadcast_address, self._port))
            
            # Wait for responses
            while (time.time() - start_time) < timeout:
                try:
                    data, addr = self._socket.recvfrom(1024)
                    if data == b"DISCOVER_RESPONSE":
                        device_info = {
                            "host": addr[0],
                            "port": addr[1],
                            "id": f"{addr[0]}:{addr[1]}",
                            "last_seen": time.time()
                        }
                        discovered.append(device_info)
                except socket.timeout:
                    continue
                    
        except Exception as e:
            logger.error(f"Discovery error: {e}")
        
        return discovered
    
    def _listen_loop(self) -> None:
        """Listen for discovery requests and respond."""
        while self._running:
            try:
                data, addr = self._socket.recvfrom(1024)
                if data == b"DISCOVER_REQUEST":
                    # Respond with our presence
                    response = b"DISCOVER_RESPONSE"
                    self._socket.sendto(response, addr)
                    logger.debug(f"Responded to discovery request from {addr}")
            except:
                pass
    
    def get_discovered_devices(self) -> Dict[str, dict]:
        """Get all currently discovered devices."""
        with self._lock:
            return self._discovered_devices.copy()