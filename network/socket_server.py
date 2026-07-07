"""
===============================================================================
RemoteDesk Pro
File: network/socket_server.py
Implements the server-side socket handling for RemoteDesk Pro.
Manages incoming client connections and message routing.
===============================================================================
"""

from __future__ import annotations

import socket
import threading
import time
import struct
import uuid
from typing import Optional, Callable, Dict, Tuple, List, Any

from core.constants import DEFAULT_HOST, DEFAULT_PORT, SOCKET_TIMEOUT
from core.logger import logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage


class SocketServer:
    """
    Server class that handles incoming socket connections.
    Supports multiple concurrent client connections.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        max_clients: int = 10,
        on_client_connect: Optional[Callable[[str, Tuple[str, int]], None]] = None,
        on_client_disconnect: Optional[Callable[[str], None]] = None,
        on_message_received: Optional[Callable[[str, RemoteDeskMessage], None]] = None,
    ) -> None:
        self._host = host
        self._port = port
        self._max_clients = max_clients
        self._on_client_connect = on_client_connect
        self._on_client_disconnect = on_client_disconnect
        self._on_message_received = on_message_received

        self._server_socket: Optional[socket.socket] = None
        self._clients: Dict[str, socket.socket] = {}
        self._client_addresses: Dict[str, Tuple[str, int]] = {}
        self._client_threads: Dict[str, threading.Thread] = {}
        self._running = False
        self._lock = threading.Lock()
        self._packet_system = PacketSystem()
        self._accept_thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        with self._lock:
            if self._running:
                logger.warning("Server is already running.")
                return True

            try:
                self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._server_socket.bind((self._host, self._port))
                self._server_socket.listen(self._max_clients)
                self._server_socket.settimeout(1.0)

                self._running = True
                self._accept_thread = threading.Thread(
                    target=self._accept_clients_loop,
                    name="ServerAcceptThread",
                    daemon=True,
                )
                self._accept_thread.start()

                logger.info(f"Server started on {self._host}:{self._port}")
                return True

            except Exception as e:
                logger.error(f"Failed to start server on {self._host}:{self._port}: {e}", exc_info=True)
                self._cleanup_server()
                return False

    def _accept_clients_loop(self) -> None:
        while self._running and self._server_socket:
            try:
                client_socket, address = self._server_socket.accept()
                client_socket.settimeout(SOCKET_TIMEOUT)
                client_id = str(uuid.uuid4())

                with self._lock:
                    self._clients[client_id] = client_socket
                    self._client_addresses[client_id] = address

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_id,),
                    name=f"ServerClientThread-{client_id}",
                    daemon=True,
                )
                with self._lock:
                    self._client_threads[client_id] = thread
                thread.start()

                logger.info(f"New client connected: {client_id} from {address}")
                if self._on_client_connect:
                    self._on_client_connect(client_id, address)

            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as e:
                logger.error(f"Error accepting client connection: {e}", exc_info=True)
                break

    def _handle_client(self, client_id: str) -> None:
        client_socket = None
        with self._lock:
            client_socket = self._clients.get(client_id)

        if client_socket is None:
            return

        buffer = b""
        try:
            while self._running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        logger.info(f"Client {client_id} closed connection.")
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

                        message = RemoteDeskMessage.from_dict(message_dict)
                        if message.is_valid():
                            if self._on_message_received:
                                self._on_message_received(client_id, message)
                        else:
                            logger.warning(f"Received invalid message from {client_id}: {message_dict}")

                except socket.timeout:
                    continue
                except ConnectionResetError:
                    logger.info(f"Connection reset by client {client_id}")
                    break
                except Exception as e:
                    logger.error(f"Error receiving data from {client_id}: {e}", exc_info=True)
                    break

        finally:
            self._disconnect_client(client_id)

    def send_to_client(self, client_id: str, message: Any) -> bool:
        if isinstance(message, RemoteDeskMessage):
            data = message.to_dict()
        elif isinstance(message, dict):
            data = message
        else:
            logger.error("Unsupported message type for send_to_client")
            return False

        packet = self._packet_system.create_packet(data)
        with self._lock:
            client_socket = self._clients.get(client_id)

        if client_socket is None:
            logger.warning(f"Client {client_id} not found for sending message")
            return False

        try:
            client_socket.sendall(packet)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to client {client_id}: {e}", exc_info=True)
            self._disconnect_client(client_id)
            return False

    def broadcast_message(self, message: Any) -> bool:
        success = True
        with self._lock:
            client_ids = list(self._clients.keys())

        for client_id in client_ids:
            if not self.send_to_client(client_id, message):
                success = False
        return success

    def _disconnect_client(self, client_id: str) -> None:
        with self._lock:
            client_socket = self._clients.pop(client_id, None)
            if client_id in self._client_addresses:
                self._client_addresses.pop(client_id)
            if client_id in self._client_threads:
                self._client_threads.pop(client_id)

        if client_socket:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                client_socket.close()
            except Exception:
                pass

        logger.info(f"Client {client_id} disconnected.")
        if self._on_client_disconnect:
            self._on_client_disconnect(client_id)

    def stop(self) -> None:
        with self._lock:
            if not self._running:
                logger.warning("Server is not running.")
                return
            self._running = False

            client_ids = list(self._clients.keys())

        for client_id in client_ids:
            self._disconnect_client(client_id)

        self._cleanup_server()
        logger.info("Server stopped successfully.")

    def _cleanup_server(self) -> None:
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

        with self._lock:
            self._clients.clear()
            self._client_addresses.clear()
            self._client_threads.clear()

    def get_client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    def get_client_ids(self) -> List[str]:
        with self._lock:
            return list(self._clients.keys())

    def get_client_address(self, client_id: str) -> Optional[Tuple[str, int]]:
        with self._lock:
            return self._client_addresses.get(client_id)


if __name__ == "__main__":
    def on_server_client_connect(client_id: str, address: Tuple[str, int]) -> None:
        logger.info(f"DEMO: Server received connection from {client_id} ({address})")

    def on_server_client_disconnect(client_id: str) -> None:
        logger.info(f"DEMO: Server detected disconnection from {client_id}")

    def on_message_received(client_id: str, message: RemoteDeskMessage) -> None:
        logger.info(f"DEMO: Server received message from {client_id}: {message.to_dict()}")

    server_instance = SocketServer(
        host="0.0.0.0",
        port=DEFAULT_PORT,
        on_client_connect=on_server_client_connect,
        on_client_disconnect=on_server_client_disconnect,
        on_message_received=on_message_received,
    )

    if server_instance.start():
        logger.info("Server demo started. Waiting for clients...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server demo interrupted.")
        finally:
            server_instance.stop()
            logger.info("Server demo finished.")
    else:
        logger.error("Failed to start server demo.")