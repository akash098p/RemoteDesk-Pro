"""
===============================================================================
RemoteDesk Pro
File: network/connection_manager.py
Manages client-server connections and remote control capabilities
===============================================================================
"""

from __future__ import annotations

import socket
import threading
import time
import uuid
import base64
from typing import Optional, Dict, Any

from network.protocol import RemoteDeskMessage, MessageType, MessageFactory
from core.constants import DEFAULT_PORT
from core.logger import get_logger

logger = get_logger()

class ConnectionManager:
    def __init__(self, server_port: int = DEFAULT_PORT):
        """
        Initialize connection manager
        
        Args:
            server_port: Port for the server component
        """
        self.server_port = server_port
        self.client_id: Optional[str] = None
        self.is_server: bool = False
        self.is_controlling: bool = False
        self.controlled_client: Optional[str] = None
        self._server_socket: Optional[socket.socket] = None
        self._client_socket: Optional[socket.socket] = None
        self.clients: Dict[str, socket] = {}
        self._running: bool = False
        self._message_queue: list = []
        self._lock = threading.Lock()
        self.logger = logger
        self.logger.info(f"ConnectionManager initialized on port {server_port}")

    def start_server(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> bool:
        """Start the server component"""
        if not self._server_socket:
            try:
                self.server_port = port
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_socket.bind((host, port))
                self._server_socket.listen(5)
                self._server_socket.setblocking(False)
                self._running = True
                threading.Thread(target=self._server_accept, daemon=True).start()
                logger.info(f"Server started on {host}:{self.server_port}")
                return True
            except Exception as e:
                logger.error(f"Failed to start server: {e}")
                return False
        return True

    def stop_server(self) -> bool:
        """Stop the server component"""
        try:
            self._running = False
            if self._server_socket:
                self._server_socket.close()
                self._server_socket = None
            logger.info("Server stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
            return False

    def connect_to_client(self, host: str, port: int) -> bool:
        """Connect to a remote client"""
        try:
            self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._client_socket.settimeout(10)
            self._client_socket.connect((host, port))
            self._running = True
            threading.Thread(target=self._client_receive, daemon=True).start()
            self.client_id = str(uuid.uuid4())
            self.is_controlling = True
            logger.info(f"Connected to client at {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Connection to client failed: {e}")
            return False

    def send_message(self, message_type: MessageType, payload: dict) -> bool:
        """Send a message to connected client or server"""
        try:
            message = RemoteDeskMessage(message_type, payload)
            json_data = message.to_json()
            
            if self.is_controlling and self._client_socket:
                self._client_socket.send(json_data.encode())
            
            # Also send to any connected clients
            for client_id, client_socket in list(self.clients.items()):
                try:
                    client_socket.send(json_data.encode())
                except:
                    self._disconnect_client(client_id)
                    
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def send_screen_frame(self, frame_data: bytes, metadata: dict = None) -> bool:
        """Send a screen frame message"""
        return self.send_message(MessageType.SCREEN_FRAME, {
            "frame_data": base64.b64encode(frame_data).decode(),
            "metadata": metadata or {}
        })

    def send_mouse_event(self, x: int, y: int, button: str = "left", action: str = "move") -> bool:
        """Send a mouse event to remote device"""
        return self.send_message(MessageType.MOUSE_EVENT, {
            "x": x, "y": y, "button": button, "action": action
        })

    def send_keyboard_event(self, key: str, action: str = "press") -> bool:
        """Send a keyboard event to remote device"""
        return self.send_message(MessageType.KEYBOARD_EVENT, {
            "key": key, "action": action
        })

    def _server_accept(self):
        """Main server accept loop"""
        while self._running:
            try:
                if not self._server_socket:
                    break
                client_socket, addr = self._server_socket.accept()
                client_socket.setblocking(False)
                client_id = str(uuid.uuid4())
                self.clients[client_id] = client_socket
                threading.Thread(
                    target=self._handle_client,
                    args=(client_id,),
                    daemon=True
                ).start()
                logger.info(f"Client connected: {client_id} from {addr}")
            except Exception as e:
                logger.error(f"Server accept error: {e}")
                break

    def _handle_client(self, client_id: str):
        """Handle communication with a client"""
        client_socket = self.clients[client_id]
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                message = RemoteDeskMessage.from_json(data.decode())
                self.process_message(message)
            except Exception as e:
                logger.error(f"Client handler error: {e}")
                break
        self._disconnect_client(client_id)

    def _client_receive(self):
        """Receive messages from remote client"""
        while self._running:
            try:
                data = self._client_socket.recv(4096)
                if not data:
                    break
                message = RemoteDeskMessage.from_json(data.decode())
                self.process_message(message)
            except Exception as e:
                logger.error(f"Client receive error: {e}")
                break

    def process_message(self, message: RemoteDeskMessage):
        """Process incoming messages based on type"""
        logger.debug(f"Processing message: {message.type} with payload: {message.payload}")
        if message.type == MessageType.SCREEN_FRAME:
            self._handle_screen_frame(message.payload)
        elif message.type == MessageType.MOUSE_EVENT:
            self._handle_mouse_event(message.payload)
        elif message.type == MessageType.KEYBOARD_EVENT:
            self._handle_keyboard_event(message.payload)
        elif message.type == MessageType.CONTROL_REQUEST:
            self._handle_control_request(message.payload)

    def _handle_screen_frame(self, payload: dict):
        """Handle incoming screen frames"""
        # This would normally be sent to the screen sharing viewer
        pass

    def _handle_mouse_event(self, payload: dict):
        """Process mouse events from remote device"""
        logger.info(f"Mouse event received: {payload}")

    def _handle_keyboard_event(self, payload: dict):
        """Process keyboard events from remote device"""
        logger.info(f"Keyboard event received: {payload}")

    def _handle_control_request(self, payload: dict):
        """Handle control permission requests"""
        logger.info(f"Control request received: {payload}")

    def _disconnect_client(self, client_id: str):
        """Clean up disconnected client"""
        if client_id in self.clients:
            try:
                del self.clients[client_id]
            except:
                pass

    def get_connected_clients(self):
        """Return list of connected client IDs"""
        return list(self.clients.keys())

    def is_client_active(self) -> bool:
        """Check if we have an active connection"""
        return self._client_socket is not None and self.is_controlling

    def get_active_client(self):
        """Get the current controlled client ID"""
        return self.controlled_client

    def disconnect_all(self):
        """Disconnect all clients and stop server"""
        try:
            self._running = False
            if self._server_socket:
                self._server_socket.close()
            for client_socket in self.clients.values():
                client_socket.close()
            self.clients.clear()
            logger.info("All connections disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.disconnect_all()