"""
===============================================================================
RemoteDesk Pro
File: network/connection_manager.py
Implements connection management for SocketServer and SocketClient.
Manages connection lifecycle and provides status updates.
===============================================================================
"""

from __future__ import annotations

import time
import socket
import threading
from typing import Callable, Optional, Dict, Any, Tuple

from network.socket_server import SocketServer
from network.socket_client import SocketClient
from network.protocol import RemoteDeskMessage, MessageType
from core.logger import get_logger

logger = get_logger()


class ConnectionManager:
    """
    Manages network connections between clients and servers.
    Coordinates connection state and provides status updates.
    """
    
    def __init__(
        self,
        server_port: int = 5000,
        client_id: Optional[str] = None,
        server_callback: Optional[Callable] = None,
        client_callback: Optional[Callable] = None,
    ) -> None:
        """
        Initialize connection manager.
        
        Args:
            server_port: Port for the server component
            client_id: Identifier for the client connection
            server_callback: Callback for server events
            client_callback: Callback for client events
        """
        self._server_port = server_port
        self._client_id = client_id or f"client_{int(time.time())}"
        self._server_callback = server_callback
        self._client_callback = client_callback
        
        self._server: Optional[SocketServer] = None
        self._client: Optional[SocketClient] = None
        
        self._initialized = False
    
    def initialize(self, is_server: bool = True, **kwargs) -> bool:
        """
        Initialize the connection manager with server or client mode.
        
        Args:
            is_server: True for server mode, False for client mode
            **kwargs: Additional arguments for initialization
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if is_server:
                self._server = SocketServer(
                    host=kwargs.get("host", "127.0.0.1"),
                    port=kwargs.get("port", self._server_port),
                    max_clients=kwargs.get("max_clients", 10),
                    on_client_connect=self._on_server_client_connect,
                    on_client_disconnect=self._on_server_client_disconnect,
                    on_message_received=self._on_server_message,
                )
                
                if self._server.start():
                    logger.info("Server initialized successfully")
                    self._initialized = True
                    return True
            else:
                self._client = SocketClient(
                    host=kwargs.get("host", "127.0.0.1"),
                    port=kwargs.get("port", self._server_port),
                    on_connect=self._on_client_connect,
                    on_disconnect=self._on_client_disconnect,
                    on_message_received=self._on_client_message,
                )
                
                if self._client.connect():
                    logger.info(f"Client initialized successfully: {self._client_id}")
                    self._initialized = True
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """
        Start the appropriate network component.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if self._server:
                self._server.start()
                return True
            elif self._client:
                self._client.connect()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to start connection: {e}")
            return False
    
    def stop(self) -> None:
        """Stop all network operations."""
        try:
            if self._server:
                self._server.stop()
            if self._client:
                self._client.disconnect()
                
            self._initialized = False
            logger.info("All connections stopped")
            
        except Exception as e:
            logger.error(f"Error stopping connections: {e}")
    
    def send_message(self, message: RemoteDeskMessage | dict, client_id: Optional[str] = None) -> bool:
        """
        Send a message through the appropriate connection.
        
        Args:
            message: Message object or dictionary to send
            client_id: Specific client identifier when server mode requires a target
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self._initialized:
            return False

        try:
            if self._server:
                if client_id:
                    return self._server.send_to_client(client_id, message)
                return self._server.broadcast_message(message)
            elif self._client:
                return self._client.send_message(message)
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def get_connection_status(self) -> str:
        """
        Get current connection status.
        
        Returns:
            Status string ("disconnected", "connecting", "connected", or "error")
        """
        try:
            if self._server:
                return "connected"
            elif self._client:
                if self._client.is_connected():
                    return "connected"
                elif not self._client.connect():
                    return "error"
                return "connecting"
            return "disconnected"
        except Exception as e:
            logger.error(f"Error getting connection status: {e}")
            return "error"
    
    def get_connected_clients(self) -> list[str]:
        """
        Get list of connected clients (server mode only).
        
        Returns:
            List of connected client identifiers
        """
        try:
            if self._server:
                return self._server.get_client_ids()
            return []
        except Exception as e:
            logger.error(f"Failed to get connected clients: {e}")
            return []
    
    def get_client_id(self) -> str:
        """Get the client identifier."""
        return self._client_id
    
    def _on_server_client_connect(self, client_id: str, client_socket) -> None:
        """
        Handle new client connection on the server side.
        
        Args:
            client_id: Unique identifier for the client
            client_socket: Client's socket connection
        """
        logger.info(f"Client connected: {client_id}")
        if self._server_callback:
            self._server_callback("connection", {"client_id": client_id, "status": "connected"})
    
    def _on_server_client_disconnect(self, client_id: str) -> None:
        """
        Handle client disconnection on the server side.
        
        Args:
            client_id: Client identifier
        """
        logger.info(f"Client disconnected: {client_id}")
        if self._server_callback:
            self._server_callback("disconnection", {"client_id": client_id, "status": "disconnected"})
    
    def _on_server_message(self, client_id: str, message: dict) -> None:
        """
        Handle incoming message on the server side.
        
        Args:
            client_id: Client identifier
            message: Received message dictionary
        """
        logger.debug(f"Received message from {client_id}: {message}")
        if self._server_callback:
            self._server_callback("message", message)
    
    def _on_client_connect(self, client_id: str, client_socket) -> None:
        """
        Handle client connection event.
        
        Args:
            client_id: Client identifier
            client_socket: Client's socket connection
        """
        logger.info(f"Client connected: {client_id}")
        if self._client_callback:
            self._client_callback("connection", {"client_id": client_id, "status": "connected"})
    
    def _on_client_disconnect(self, client_id: str) -> None:
        """
        Handle client disconnection event.
        
        Args:
            client_id: Client identifier
        """
        logger.info(f"Client disconnected: {client_id}")
        if self._client_callback:
            self._client_callback("disconnection", {"client_id": client_id, "status": "disconnected"})
    
    def _on_client_message(self, message: RemoteDeskMessage) -> None:
        """
        Handle incoming message on the client side.
        
        Args:
            message: Received message object
        """
        logger.debug(f"Received message from server: {message}")
        if self._client_callback:
            self._client_callback("message", message)
    
    def destroy(self) -> None:
        """Clean up and release resources."""
        self.stop()
        logger.debug("ConnectionManager destroyed")


# Convenience function
def create_connection_manager(
    server_port: int = 5000,
    client_id: Optional[str] = None,
    server_callback: Optional[Callable] = None,
    client_callback: Optional[Callable] = None,
) -> ConnectionManager:
    """
    Factory function to create a ConnectionManager instance.
    
    Args:
        server_port: Port for the server
        client_id: Identifier for the client
        server_callback: Callback for server events
        client_callback: Callback for client events
        
    Returns:
        Configured ConnectionManager instance
    """
    return ConnectionManager(
        server_port=server_port,
        client_id=client_id,
        server_callback=server_callback,
        client_callback=client_callback,
    )