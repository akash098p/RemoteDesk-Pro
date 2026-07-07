
import threading
import socket
import json
from typing import Callable, Optional

from core.logger import get_logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage, MessageType
from chat.message import ChatMessage

class ChatClient:
    """
    Manages sending and receiving chat messages on the client side.
    """
    def __init__(
        self,
        client_socket: socket.socket,
        on_message_received: Callable[[ChatMessage], None],
        username: str = "Guest",
    ):
        self.logger = get_logger()
        self.client_socket = client_socket
        self.on_message_received = on_message_received
        self.username = username
        self.is_running = threading.Event()
        self.is_running.set() # Set to true initially
        self.receive_thread: Optional[threading.Thread] = None
        self.logger.info(f"ChatClient initialized for user: {self.username}")

    def start_receiving(self):
        """
        Starts a background thread to continuously receive chat messages from the server.
        """
        if self.receive_thread and self.receive_thread.is_alive():
            self.logger.warning("Chat receive thread already running.")
            return

        self.receive_thread = threading.Thread(target=self._receive_messages_loop, daemon=True)
        self.receive_thread.start()
        self.logger.info("Chat client started receiving messages.")

    def _receive_messages_loop(self):
        """
        Main loop for receiving messages. Runs in a separate thread.
        """
        self.logger.debug("Chat client receive loop started.")
        while self.is_running.is_set():
            try:
                raw_packet = PacketSystem.receive_packet(self.client_socket)
                if not raw_packet: # Server disconnected or socket closed
                    self.logger.warning("Chat client disconnected or no data received.")
                    self.is_running.clear()
                    break

                rd_message = RemoteDeskMessage.deserialize(raw_packet)

                if rd_message.message_type == MessageType.CHAT_MESSAGE:
                    chat_message = ChatMessage.deserialize(rd_message.payload)
                    self.logger.debug(f"Received chat message: {chat_message.sender}: {chat_message.content[:50]}...")
                    if self.on_message_received:
                        self.on_message_received(chat_message)
                else:
                    self.logger.debug(f"Received non-chat message type: {rd_message.message_type}")

            except (socket.timeout, BlockingIOError):
                # No data for now, continue polling
                continue
            except (ConnectionResetError, BrokenPipeError) as e:
                self.logger.error(f"Chat client connection lost: {e}")
                self.is_running.clear()
                break
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding incoming message in chat client: {e} - Raw: {raw_packet[:100] if raw_packet else ''}...")
            except Exception as e:
                self.logger.error(f"Unexpected error in chat client receive loop: {e}")
                self.is_running.clear()
                break
        self.logger.info("Chat client receive loop stopped.")

    def send_chat_message(self, content: str, message_type: str = "text", metadata: Optional[Dict] = None):
        """
        Constructs and sends a ChatMessage to the server.
        """
        if not self.is_running.is_set():
            self.logger.warning("Attempted to send chat message while client is not running.")
            return

        if metadata is None:
            metadata = {}

        chat_message = ChatMessage(
            sender=self.username,
            content=content,
            message_type=message_type,
            metadata=metadata
        )

        try:
            chat_data = chat_message.serialize()
            rd_message = RemoteDeskMessage(
                message_type=MessageType.CHAT_MESSAGE,
                payload=chat_data
            )
            PacketSystem.send_packet(self.client_socket, rd_message.serialize())
            self.logger.info(f"Sent chat message: {content[:50]}...")
        except Exception as e:
            self.logger.error(f"Error sending chat message: {e}")

    def shutdown(self):
        """
        Stops the chat client's receive thread and cleans up resources.
        """
        self.logger.info("ChatClient shutting down.")
        self.is_running.clear()
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=2) # Give some time for the thread to finish
            if self.receive_thread.is_alive():
                self.logger.warning("Chat receive thread did not terminate gracefully.")
        self.logger.info("ChatClient shut down complete.")
