
import threading
from typing import Callable, Any, Optional

from core.logger import get_logger
from chat.message import ChatMessage
from chat.client import ChatClient
# from chat.server import ChatServer # Will be passed from connection_manager

class ChatManager:
    """
    Manages chat functionalities, orchestrating between the ChatClient/ChatServer
    and the GUI components. It acts as a central point for sending and receiving
    chat messages within the application.
    """
    def __init__(self, 
                 connection_manager: Any, 
                 on_new_message_callback: Callable[[ChatMessage], None], 
                 username: str = "User"): # Default username
        
        self.logger = get_logger()
        self.connection_manager = connection_manager
        self.on_new_message_callback = on_new_message_callback
        self.username = username

        self.chat_client: Optional[ChatClient] = None
        # self.chat_server: Optional[ChatServer] = None # Handled by ConnectionManager

        self.is_server = False # Flag to indicate if this instance is running as server
        self.logger.info(f"ChatManager initialized with username: {self.username}")

    def set_username(self, username: str):
        """
        Sets the username for the chat manager and updates the chat client if active.
        """
        self.username = username
        if self.chat_client:
            self.chat_client.username = username
        self.logger.info(f"ChatManager username set to: {self.username}")

    def start_chat_client(self, client_socket: socket.socket):
        """
        Starts the chat client part of the manager.
        """
        self.is_server = False
        if self.chat_client:
            self.chat_client.shutdown()

        self.chat_client = ChatClient(
            client_socket=client_socket,
            on_message_received=self._handle_client_incoming_message,
            username=self.username
        )
        self.chat_client.start_receiving()
        self.logger.info("ChatManager started as client.")

    # The server-side handling is primarily done by ChatServer, which is instantiated
    # and managed by ConnectionManager. ChatManager simply provides the callback for it.
    def _handle_server_incoming_message(self, client_socket: socket.socket, payload: str):
        """
        Callback for `ChatServer` to handle incoming messages. This will be registered
        with the `ConnectionManager`.
        """
        try:
            chat_message = ChatMessage.deserialize(payload)
            self.logger.info(f"Server received chat message from {client_socket.getpeername()}: {chat_message.sender} - {chat_message.content[:50]}...")
            
            # Notify GUI of the new message
            self.on_new_message_callback(chat_message)

            # Broadcast to other clients (handled by ChatServer itself)
            # No need to explicitly call broadcast_chat_message here as ConnectionManager
            # will call ChatServer's handle_incoming_chat_message which does the broadcast.

        except Exception as e:
            self.logger.error(f"ChatManager (server-side) error handling incoming message: {e}")

    def _handle_client_incoming_message(self, chat_message: ChatMessage):
        """
        Callback for `ChatClient` when a new message is received from the server.
        """
        self.logger.info(f"Client received chat message: {chat_message.sender} - {chat_message.content[:50]}...")
        self.on_new_message_callback(chat_message)

    def send_message(self, content: str, message_type: str = "text", metadata: Optional[Dict] = None):
        """
        Sends a chat message to the connected peer (server if client, or all clients if server).
        """
        if self.is_server:
            # If acting as server, broadcast the message to all clients
            chat_message = ChatMessage(
                sender=self.username,
                content=content,
                message_type=message_type,
                metadata=metadata if metadata else {}
            )
            # The connection_manager holds the ChatServer instance
            if self.connection_manager.chat_server:
                self.connection_manager.chat_server.broadcast_chat_message(chat_message)
            else:
                self.logger.warning("Attempted to send message as server, but ChatServer is not active.")
        else:
            # If acting as client, send the message to the server
            if self.chat_client:
                self.chat_client.send_chat_message(content, message_type, metadata)
            else:
                self.logger.warning("Attempted to send message as client, but ChatClient is not active.")

    def shutdown(self):
        """
        Shuts down the chat manager and its components.
        """
        self.logger.info("ChatManager shutting down.")
        if self.chat_client:
            self.chat_client.shutdown()
        self.logger.info("ChatManager shut down complete.")
