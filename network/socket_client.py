"""
===============================================================================
RemoteDesk Pro
File: network/socket_client.py
Implements the client-side socket handling for RemoteDesk Pro.
Manages outgoing connections and message sending/receiving.
===============================================================================
"""

from __future__ import annotations

import socket
import threading
import time
import struct
import uuid
from typing import Optional, Callable, Dict, Tuple

from core.constants import DEFAULT_HOST, DEFAULT_PORT, SOCKET_TIMEOUT
from core.logger import logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage, MessageFactory, MessageType


class SocketClient:
    """
    Client class that handles outbound socket connections.
    Manages connection establishment and message sending/receiving.
    """
    
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        on_connect: Optional[Callable[[str, Tuple[str, int]], None]] = None,
        on_disconnect: Optional[Callable[[str], None]] = None,
        on_message_received: Optional[Callable[[RemoteDeskMessage], None]] = None,
    ) -> None:
        """
        Initialize the socket client.
        
        Args:
            host: Server host address
            port: Server port number
            on_connect: Callback when connected (client_id, address_tuple)
            on_disconnect: Callback when disconnected (client_id)
            on_message_received: Callback for incoming messages (message_object)
        """
        self._host = host
        self._port = port
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_message_received = on_message_received
        
        self._socket: Optional[socket.socket] = None
        self._client_id: str = f"client-{uuid.uuid4()}" # Unique ID for this client
        self._server_address: Optional[Tuple[str, int]] = None
        self._running = False
        self._lock = threading.Lock()
        self._packet_system = PacketSystem()
        self._receive_thread: Optional[threading.Thread] = None
    
    def connect(self) -> bool:
        """
        Establish a connection to the server.
        
        Returns:
            True if connection successful, False otherwise
        """
        with self._lock:
            if self._running:
                logger.warning("Client is already connected.")
                return True
            
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(SOCKET_TIMEOUT)
                self._socket.connect((self._host, self._port))
                self._server_address = self._socket.getpeername()
                
                self._running = True\n                self._receive_thread = threading.Thread(\n                    target=self._receive_loop,\n                    name=f\"ClientReceiveThread-{self._client_id}\",\n                    daemon=True\n                )\n                self._receive_thread.start()\n                \n                logger.info(f\"Client {self._client_id} connected to {self._host}:{self._port}\")\n                if self._on_connect:\n                    self._on_connect(self._client_id, self._server_address)\n                return True\n                \n            except Exception as e:\n                logger.error(f\"Connection failed to {self._host}:{self._port}: {e}\", exc_info=True)\n                self._cleanup_client()\n                return False\n    \n    def _receive_loop(self) -> None:\n        \"\"\"\n        Continuously receives and processes messages from the server.\n        \"\"\"\
        buffer = b\"\"\n        try:\n            while self._running:\n                try:\n                    data = self._socket.recv(4096)\n                    if not data:\n                        logger.info(\"Server closed connection gracefully.\")\n                        break\n                    \n                    buffer += data\n                    \n                    while len(buffer) >= 4: # Check for length prefix\n                        length = struct.unpack(\'!I\', buffer[:4])[0]\n                        if len(buffer) < 4 + length: # Incomplete packet\n                            break\n                        \n                        packet_data = buffer[4 : 4 + length]\n                        buffer = buffer[4 + length:] # Remove processed packet from buffer\n                        \n                        message_dict = self._packet_system.parse_packet(packet_data)\n                        if message_dict:\n                            rd_message = RemoteDeskMessage.from_dict(message_dict)\n                            if rd_message.is_valid() and self._on_message_received:\n                                self._on_message_received(rd_message)\n                            else:\n                                logger.warning(f\"Invalid or unhandled message from server: {message_dict}\")\n\n                except socket.timeout:\n                    # No data for a while, continue checking\n                    pass\n                except ConnectionResetError:\n                    logger.info(\"Server reset connection.\")\n                    break\n                except Exception as e:\n                    logger.error(f\"Error handling server communication: {e}\", exc_info=True)\n                    break\n\n        finally:\n            self.disconnect()\n\n    def send_message(self, message: RemoteDeskMessage) -> bool:\n        \"\"\"\n        Send a message to the connected server.\n        \n        Args:\n            message: RemoteDeskMessage object to send\n            \n        Returns:\n            True if message sent successfully, False otherwise\n        \"\"\"\n        with self._lock:\n            if not self._running or self._socket is None:\n                logger.warning(\"Not connected to server. Cannot send message.\")\n                return False\n            \n            try:\n                packet_data = self._packet_system.create_packet(message.to_dict())\n                self._socket.sendall(packet_data)\n                logger.debug(f\"Sent {message.message_type} message to server\")\n                return True\n            except Exception as e:\n                logger.error(f\"Failed to send message to server: {e}\", exc_info=True)\n                self.disconnect() # Disconnect on send failure\n                return False\n\n    def disconnect(self) -> None:\n        \"\"\"\n        Close the connection to the server and clean up resources.\n        \"\"\"\
        with self._lock:\n            if not self._running:\n                return\n            \n            logger.info(f\"Disconnecting client {self._client_id} from {self._server_address}...\")\n            self._running = False\n            \n            if self._socket:\n                try:\n                    self._socket.shutdown(socket.SHUT_RDWR) # Signal server to close\n                    self._socket.close()\n                except Exception as e:\n                    logger.debug(f\"Error closing client socket: {e}\")\n                self._socket = None\n            \n            if self._receive_thread and self._receive_thread.is_alive():\n                # Daemon thread, will exit when app closes or self._running is False\n                pass \n\n            self._cleanup_client()\n            logger.info(f\"Client {self._client_id} disconnected.\")\n            if self._on_disconnect:\n                self._on_disconnect(self._client_id)\n\n    def _cleanup_client(self) -> None:\n        \"\"\"\n        Clear any remaining client-side resources.\n        \"\"\"\
        self._socket = None\n        self._server_address = None\n        self._receive_thread = None\n\n    def is_connected(self) -> bool:\n        \"\"\"\n        Checks if the client is currently connected to a server.\n        \"\"\"\
        with self._lock:\n            return self._running and self._socket is not None\n\n    def get_client_id(self) -> str:\n        \"\"\"\n        Returns the unique ID of this client instance.\n        \"\"\"\
        return self._client_id\n\n    def get_server_address(self) -> Optional[Tuple[str, int]]:\n        \"\"\"\n        Returns the (host, port) of the connected server, or None if not connected.\n        \"\"\"\
        with self._lock:\n            return self._server_address\n\n\n# Standalone test / demo\nif __name__ == \"__main__\":\n    def on_client_connect(client_id: str, address: Tuple[str, int]):\n        logger.info(f\"DEMO: Client {client_id} connected to server at {address}\")\n        client_instance.send_message(MessageFactory.create_handshake(\"DemoUser\", client_id))\n        client_instance.send_message(MessageFactory.create_data(\"Hello from client!\"))\n\n    def on_client_disconnect(client_id: str):\n        logger.info(f\"DEMO: Client {client_id} disconnected from server.\")\n\n    def on_client_message_received(message: RemoteDeskMessage):\n        logger.info(f\"DEMO: Client received message from server: {message.to_dict()}\")\n\n    client_instance = SocketClient(\n        host=\"127.0.0.1\",\n        port=DEFAULT_PORT,\n        on_connect=on_client_connect,\n        on_disconnect=on_client_disconnect,\n        on_message_received=on_client_message_received,\n    )\n\n    logger.info(\"Client demo starting. Attempting to connect...\")\n    if client_instance.connect():\n        try:\n            for i in range(3):\n                client_instance.send_message(MessageFactory.create_ping())\n                time.sleep(2)\n            client_instance.disconnect()\n        except KeyboardInterrupt:\n            logger.info(\"Client demo interrupted.\")\n        finally:\n            client_instance.disconnect()\n            logger.info(\"Client demo finished.\")\n    else:\n        logger.error(\"Failed to connect client demo.\")