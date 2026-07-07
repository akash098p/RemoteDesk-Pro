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
from typing import Optional, Callable, Dict, Tuple, Any

from core.constants import DEFAULT_HOST, DEFAULT_PORT, SOCKET_TIMEOUT
from core.logger import logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage


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
        self._host = host
        self._port = port
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_message_received = on_message_received

        self._socket: Optional[socket.socket] = None
        self._client_id: str = f"client-{uuid.uuid4()}"
        self._server_address: Optional[Tuple[str, int]] = None
        self._running = False
        self._lock = threading.Lock()
        self._packet_system = PacketSystem()
        self._receive_thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        with self._lock:
            if self._running:
                logger.warning("Client is already connected.")
                return True

            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(SOCKET_TIMEOUT)
                self._socket.connect((self._host, self._port))
                self._server_address = self._socket.getpeername()
                self._running = True

                self._receive_thread = threading.Thread(
                    target=self._receive_loop,
                    name=f"ClientReceiveThread-{self._client_id}",
                    daemon=True,
                )
                self._receive_thread.start()

                logger.info(f"Client {self._client_id} connected to {self._host}:{self._port}")
                if self._on_connect:
                    self._on_connect(self._client_id, self._server_address)
                return True

            except Exception as e:
                logger.error(f"Connection failed to {self._host}:{self._port}: {e}", exc_info=True)
                self._cleanup_client()
                return False

    def _receive_loop(self) -> None:
        buffer = b""
        try:
            while self._running and self._socket:
                try:
                    data = self._socket.recv(4096)
                    if not data:
                        logger.info("Server closed connection gracefully.")
                        break

                    buffer += data
                    while len(buffer) >= 4:
                        packet_length = struct.unpack("!I", buffer[:4])[0]
                        if len(buffer) < 4 + packet_length:
                            break

                        packet = buffer[:4 + packet_length]
                        buffer = buffer[4 + packet_length:]

                        message_dict = self._packet_system.parse_packet(packet)
                        if not message_dict:
                            continue

                        rd_message = RemoteDeskMessage.from_dict(message_dict)
                        if rd_message.is_valid() and self._on_message_received:
                            self._on_message_received(rd_message)
                        else:
                            logger.warning(f"Invalid or unhandled message from server: {message_dict}")

                except socket.timeout:
                    continue
                except ConnectionResetError:
                    logger.info("Server reset connection.")
                    break
                except OSError as e:
                    if not self._running or self._socket is None or e.errno in {10038, 10053, 10054}:
                        break
                    logger.error(f"Error handling server communication: {e}", exc_info=True)
                    break
                except Exception as e:
                    logger.error(f"Error handling server communication: {e}", exc_info=True)
                    break

        finally:
            if self._running:
                self.disconnect()

    def send_message(self, message: Any) -> bool:
        if isinstance(message, RemoteDeskMessage):
            payload = message.to_dict()
        elif isinstance(message, dict):
            payload = message
        else:
            logger.error("Unsupported message type for send_message")
            return False

        packet = self._packet_system.create_packet(payload)
        with self._lock:
            if not self._running or self._socket is None:
                logger.warning("Cannot send message, client is not connected.")
                return False
            try:
                self._socket.sendall(packet)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to server: {e}", exc_info=True)
                self.disconnect()
                return False

    def disconnect(self) -> None:
        with self._lock:
            if not self._running and self._socket is None:
                return
            self._running = False
            client_socket = self._socket
            self._socket = None

        if client_socket:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                client_socket.close()
            except Exception:
                pass

        logger.info(f"Client {self._client_id} disconnected.")
        if self._on_disconnect:
            self._on_disconnect(self._client_id)

    def _cleanup_client(self) -> None:
        self._socket = None
        self._server_address = None
        self._receive_thread = None
        self._running = False

    def is_connected(self) -> bool:
        with self._lock:
            return self._running and self._socket is not None

    def get_client_id(self) -> str:
        return self._client_id

    def get_server_address(self) -> Optional[Tuple[str, int]]:
        with self._lock:
            return self._server_address


if __name__ == "__main__":
    def on_client_connect(client_id: str, address: Tuple[str, int]) -> None:
        logger.info(f"DEMO: Client {client_id} connected to server at {address}")

    def on_client_disconnect(client_id: str) -> None:
        logger.info(f"DEMO: Client {client_id} disconnected from server.")

    def on_client_message_received(message: RemoteDeskMessage) -> None:
        logger.info(f"DEMO: Client received message from server: {message.to_dict()}")

    client_instance = SocketClient(
        host="127.0.0.1",
        port=DEFAULT_PORT,
        on_connect=on_client_connect,
        on_disconnect=on_client_disconnect,
        on_message_received=on_client_message_received,
    )

    logger.info("Client demo starting. Attempting to connect...")
    if client_instance.connect():
        try:
            for _ in range(3):
                client_instance.send_message({"type": "ping", "payload": {}})
                time.sleep(2)
        except KeyboardInterrupt:
            logger.info("Client demo interrupted.")
        finally:
            client_instance.disconnect()
            logger.info("Client demo finished.")
    else:
        logger.error("Failed to connect client demo.")