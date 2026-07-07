
import threading
import socket
import json
from typing import Dict, Callable, Optional

from core.logger import get_logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage, MessageType
from chat.message import ChatMessage

class ChatServer:
    """
    Handles broadcasting chat messages to all connected clients.
    Integrates with the main `ConnectionManager` to get client sockets.
    """
    def __init__(self, connection_manager: Any):  # Avoid circular import with ConnectionManager
        self.logger = get_logger()
        self.connection_manager = connection_manager
        self.clients_lock = threading.Lock()
        self.logger.info("ChatServer initialized.")

    def send_chat_message(self, client_socket: socket.socket, message: ChatMessage):
        """
        Sends a single ChatMessage to a specific client.
        """
        try:
            chat_data = message.serialize()
            rd_message = RemoteDeskMessage(
                message_type=MessageType.CHAT_MESSAGE,
                payload=chat_data
            )
            PacketSystem.send_packet(client_socket, rd_message.serialize())
            self.logger.debug(f"Sent chat message to {client_socket.getpeername()}: {message.content[:50]}...")
        except Exception as e:
            self.logger.error(f"Error sending chat message to client {client_socket.getpeername()}: {e}")

    def broadcast_chat_message(self, chat_message: ChatMessage, exclude_socket: Optional[socket.socket] = None):
        """
        Broadcasts a ChatMessage to all connected clients.
        Optionally excludes a specific client socket (e.g., the sender).
        """
        self.logger.info(f"Broadcasting chat message: {chat_message.sender} - {chat_message.content[:50]}...")
        with self.clients_lock:
            for client_id, client_data in self.connection_manager.get_connected_clients().items():
                client_socket = client_data["socket"]
                if client_socket != exclude_socket:
                    self.send_chat_message(client_socket, chat_message)
                else:
                    self.logger.debug(f"Skipping sender {client_socket.getpeername()} for broadcast.")

    def handle_incoming_chat_message(self, client_socket: socket.socket, payload: str):
        """
        Handles an incoming chat message from a client.
        Deserializes it and broadcasts it to other clients.
        """
        try:
            chat_message = ChatMessage.deserialize(payload)
            self.logger.info(f"Received chat message from {client_socket.getpeername()}: {chat_message.sender} - {chat_message.content[:50]}...")

            # Broadcast to all other clients
            self.broadcast_chat_message(chat_message, exclude_socket=client_socket)

            # Optional: Store in chat history
            # self.chat_history_manager.add_message(chat_message)

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding chat message from {client_socket.getpeername()}: {e} - Payload: {payload[:100]}...")
        except Exception as e:
            self.logger.error(f"Unexpected error handling incoming chat message from {client_socket.getpeername()}: {e}")

    def shutdown(self):
        self.logger.info("ChatServer shutting down.")

