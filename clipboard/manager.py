
import threading
from typing import Callable, Any, Optional

from core.logger import get_logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage, MessageType
from clipboard.watcher import ClipboardWatcher

class ClipboardManager:
    """
    Manages the synchronization of clipboard content between connected devices.
    It uses a ClipboardWatcher to detect local changes and sends them over the network,
    and also updates the local clipboard with remote changes.
    """
    def __init__(self, connection_manager: Any):
        self.logger = get_logger()
        self.connection_manager = connection_manager
        self.clipboard_watcher: Optional[ClipboardWatcher] = None
        self.is_server_mode = False
        self.logger.info("ClipboardManager initialized.")

    def start(self, is_server: bool = False):
        """
        Starts the clipboard manager, initializing the watcher and setting the mode (server/client).
        """
        self.is_server_mode = is_server
        if ClipboardWatcher is not None: # Check if pyperclip was successfully imported
            if self.clipboard_watcher:
                self.clipboard_watcher.stop()
            self.clipboard_watcher = ClipboardWatcher(on_clipboard_change=self._on_local_clipboard_change)
            self.clipboard_watcher.start()
            self.logger.info(f"ClipboardManager started in {'server' if is_server else 'client'} mode.")
        else:
            self.logger.warning("ClipboardWatcher not available, clipboard synchronization will be disabled.")

    def _on_local_clipboard_change(self, content: str):
        """
        Callback triggered when the local clipboard content changes.
        Sends the new content over the network.
        """
        self.logger.debug(f"Local clipboard changed, sending to remote: {content[:50]}...")
        self.send_clipboard_update(content)

    def send_clipboard_update(self, content: str):
        """
        Sends the clipboard content to the connected peer(s).
        """
        clipboard_message = RemoteDeskMessage(
            message_type=MessageType.CLIPBOARD_SYNC,
            payload=content
        )
        try:
            if self.is_server_mode:
                # If server, broadcast to all connected clients
                with self.connection_manager.clients_lock:
                    for client_id, client_data in self.connection_manager.get_connected_clients().items():
                        client_socket = client_data["socket"]
                        PacketSystem.send_packet(client_socket, clipboard_message.serialize())
                self.logger.debug("Broadcasted clipboard update to clients.")
            else:
                # If client, send to the connected server
                if self.connection_manager.client_socket:
                    PacketSystem.send_packet(self.connection_manager.client_socket, clipboard_message.serialize())
                    self.logger.debug("Sent clipboard update to server.")
                else:
                    self.logger.warning("Attempted to send clipboard update as client, but no server connection.")
        except Exception as e:
            self.logger.error(f"Error sending clipboard update: {e}")

    def handle_incoming_clipboard_update(self, sender_socket: Any, payload: str):
        """
        Handles an incoming clipboard update from the network.
        Updates the local clipboard if the content is different.
        """
        self.logger.debug(f"Received remote clipboard update: {payload[:50]}...")
        if self.clipboard_watcher and self.clipboard_watcher.last_clipboard_content != payload:
            self.clipboard_watcher.update_clipboard(payload)
            self.logger.info("Local clipboard updated with remote content.")
        else:
            self.logger.debug("Incoming clipboard content is same as local or watcher not active, skipping update.")

    def shutdown(self):
        """
        Shuts down the clipboard manager and its watcher.
        """
        self.logger.info("ClipboardManager shutting down.")
        if self.clipboard_watcher:
            self.clipboard_watcher.stop()
        self.logger.info("ClipboardManager shut down complete.")
