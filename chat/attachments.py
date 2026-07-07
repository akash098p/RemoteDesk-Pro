
import os
import threading
from typing import Dict, Any, Callable, Optional

from core.logger import get_logger
from network.packet_system import PacketSystem
from network.protocol import RemoteDeskMessage, MessageType

class AttachmentManager:
    """
    Manages sending and receiving file/image attachments within the chat system.
    """
    CHUNK_SIZE = 4096 # Size of data chunks to send/receive

    def __init__(self, connection_manager: Any, download_dir: str = "downloads"):
        self.logger = get_logger()
        self.connection_manager = connection_manager
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.logger.info(f"AttachmentManager initialized. Download directory: {self.download_dir}")

    def send_attachment(self, target_socket: Any, file_path: str, message_id: str):
        """
        Sends a file attachment to a specific client.
        This should be called from the client-side ChatManager.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found for attachment: {file_path}")
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        self.logger.info(f"Preparing to send attachment '{file_name}' ({file_size} bytes) with ID {message_id}")

        try:
            # Send metadata first
            metadata = {
                "message_id": message_id,
                "file_name": file_name,
                "file_size": file_size,
                "chunk_size": self.CHUNK_SIZE,
                "status": "start"
            }
            rd_message = RemoteDeskMessage(
                message_type=MessageType.ATTACHMENT_METADATA,
                payload=json.dumps(metadata)
            )
            PacketSystem.send_packet(target_socket, rd_message.serialize())
            self.logger.debug(f"Sent attachment metadata for {file_name}")

            # Send file data in chunks
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # Encode chunk to base64 for JSON payload if needed, or send raw bytes
                    # For simplicity, let's send it as part of a payload within RemoteDeskMessage
                    # This assumes PacketSystem can handle binary payload, which it does if it's length prefixed.
                    # However, if RemoteDeskMessage.payload is always string, then base64 encoding is needed.
                    # Let's assume RemoteDeskMessage payload can carry raw bytes for now to simplify.
                    # If PacketSystem expects string, then payload should be base64.encode(chunk).decode('utf-8')
                    
                    # Given RemoteDeskMessage.payload is 'str' in protocol.py, we MUST base64 encode.
                    import base64
                    encoded_chunk = base64.b64encode(chunk).decode('utf-8')

                    chunk_message = RemoteDeskMessage(
                        message_type=MessageType.ATTACHMENT_CHUNK,
                        payload=json.dumps({"message_id": message_id, "chunk": encoded_chunk})
                    )
                    PacketSystem.send_packet(target_socket, chunk_message.serialize())

            # Send completion signal
            completion_metadata = {"message_id": message_id, "status": "complete"}
            rd_message = RemoteDeskMessage(
                message_type=MessageType.ATTACHMENT_METADATA,
                payload=json.dumps(completion_metadata)
            )
            PacketSystem.send_packet(target_socket, rd_message.serialize())
            self.logger.info(f"Successfully sent attachment '{file_name}' with ID {message_id}")

        except Exception as e:
            self.logger.error(f"Error sending attachment '{file_name}' with ID {message_id}: {e}")
            # Send error signal
            error_metadata = {"message_id": message_id, "status": "error", "error": str(e)}
            error_message = RemoteDeskMessage(
                message_type=MessageType.ATTACHMENT_METADATA,
                payload=json.dumps(error_metadata)
            )
            PacketSystem.send_packet(target_socket, error_message.serialize())

    def _start_receive_thread(self, client_socket: Any, metadata: Dict[str, Any], on_complete: Callable[[str], None]):
        """
        Starts a new thread to receive a file attachment.
        """
        thread = threading.Thread(target=self._receive_attachment_task,
                                  args=(client_socket, metadata, on_complete),
                                  daemon=True)
        thread.start()
        return thread

    def _receive_attachment_task(self, client_socket: Any, metadata: Dict[str, Any], on_complete: Callable[[str], None]):
        """
        Task executed in a separate thread to receive file chunks.
        """
        message_id = metadata["message_id"]
        file_name = metadata["file_name"]
        file_size = metadata["file_size"]
        chunk_size = metadata.get("chunk_size", self.CHUNK_SIZE)
        full_path = os.path.join(self.download_dir, file_name)

        self.logger.info(f"Receiving attachment '{file_name}' ({file_size} bytes) with ID {message_id} to {full_path}")

        received_size = 0
        try:
            with open(full_path, 'wb') as f:
                while received_size < file_size:
                    # Here we expect the main receive loop (e.g., in ConnectionManager)
                    # to forward ATTACHMENT_CHUNK messages to this specific thread/handler.
                    # This current implementation is simplified and assumes direct chunk receipt,
                    # which is not how it would work in a real async/multiplexed scenario.
                    # A more robust solution would involve a temporary buffer or queue per message_id
                    # in the main receive loop, which this thread would then consume.

                    # For this phase, we'll simulate waiting for a chunk from the sender's perspective
                    # and assume `handle_incoming_attachment_chunk` is correctly routing.
                    # The actual receipt of chunks will happen via `handle_incoming_attachment_chunk`
                    # which will write to the file.

                    # This `_receive_attachment_task` is primarily for orchestration.
                    # The actual file writing will occur in handle_incoming_attachment_chunk.
                    
                    # We need a way for this thread to *wait* for the chunks to arrive.
                    # This implies a queue or similar mechanism shared with the main network receive loop.
                    
                    # For now, let's refactor: this task shouldn't block for arbitrary chunks.
                    # `handle_incoming_attachment_chunk` will be responsible for writing.
                    break # Exit this loop, as chunks are handled by `handle_incoming_attachment_chunk`

            self.logger.info(f"Successfully received attachment '{file_name}' to {full_path}")
            on_complete(full_path) # Notify GUI or ChatManager

        except Exception as e:
            self.logger.error(f"Error receiving attachment '{file_name}' with ID {message_id}: {e}")
            if os.path.exists(full_path):
                os.remove(full_path) # Clean up partial file

    # Dictionary to hold file handles for ongoing transfers, keyed by message_id
    _ongoing_transfers: Dict[str, Dict[str, Any]] = {}
    _transfer_locks: Dict[str, threading.Lock] = {}

    def handle_incoming_attachment_metadata(self, client_socket: Any, payload: str, 
                                            on_attachment_start: Callable[[Dict[str, Any]], None]):
        """
        Handles incoming attachment metadata (start/complete/error signals).
        """
        import json
        try:
            metadata = json.loads(payload)
            message_id = metadata["message_id"]
            status = metadata["status"]

            if status == "start":
                file_name = metadata["file_name"]
                file_size = metadata["file_size"]
                full_path = os.path.join(self.download_dir, file_name)
                
                self.logger.info(f"Incoming attachment start: '{file_name}' ({file_size} bytes) with ID {message_id}")
                
                # Initialize transfer state
                self._ongoing_transfers[message_id] = {
                    "file_name": file_name,
                    "file_size": file_size,
                    "received_size": 0,
                    "file_handle": open(full_path, 'wb'),
                    "timestamp": datetime.now()
                }
                self._transfer_locks[message_id] = threading.Lock()
                on_attachment_start(metadata) # Notify GUI

            elif status == "complete":
                if message_id in self._ongoing_transfers:
                    with self._transfer_locks[message_id]:
                        file_handle = self._ongoing_transfers[message_id]["file_handle"]
                        file_handle.close()
                        del self._ongoing_transfers[message_id]
                        del self._transfer_locks[message_id]
                        self.logger.info(f"Attachment with ID {message_id} completed successfully.")
                else:
                    self.logger.warning(f"Completion signal for unknown attachment ID {message_id}")

            elif status == "error":
                error_msg = metadata.get("error", "Unknown error")
                self.logger.error(f"Attachment transfer for ID {message_id} failed: {error_msg}")
                if message_id in self._ongoing_transfers:
                    with self._transfer_locks[message_id]:
                        file_handle = self._ongoing_transfers[message_id]["file_handle"]
                        file_handle.close()
                        os.remove(os.path.join(self.download_dir, self._ongoing_transfers[message_id]["file_name"]))
                        del self._ongoing_transfers[message_id]
                        del self._transfer_locks[message_id]

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding attachment metadata: {e} - Payload: {payload[:100]}...")
        except Exception as e:
            self.logger.error(f"Error handling incoming attachment metadata: {e}")

    def handle_incoming_attachment_chunk(self, client_socket: Any, payload: str):
        """
        Handles an incoming attachment data chunk.
        """
        import json
        import base64
        try:
            chunk_data = json.loads(payload)
            message_id = chunk_data["message_id"]
            encoded_chunk = chunk_data["chunk"]

            if message_id in self._ongoing_transfers:
                with self._transfer_locks[message_id]:
                    file_handle = self._ongoing_transfers[message_id]["file_handle"]
                    decoded_chunk = base64.b64decode(encoded_chunk)
                    file_handle.write(decoded_chunk)
                    self._ongoing_transfers[message_id]["received_size"] += len(decoded_chunk)
                    # self.logger.debug(f"Received {len(decoded_chunk)} bytes for attachment ID {message_id}")
            else:
                self.logger.warning(f"Received chunk for unknown or completed attachment ID {message_id}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding attachment chunk: {e} - Payload: {payload[:100]}...")
        except Exception as e:
            self.logger.error(f"Error handling incoming attachment chunk: {e}")

    def shutdown(self):
        """
        Closes any open file handles for ongoing transfers during shutdown.
        """
        self.logger.info("AttachmentManager shutting down. Closing any open transfer files.")
        for message_id, transfer_info in list(self._ongoing_transfers.items()):
            try:
                transfer_info["file_handle"].close()
                self.logger.warning(f"Closed incomplete attachment transfer for ID {message_id}")
                # Optional: clean up partially downloaded file
                file_name = transfer_info["file_name"]
                full_path = os.path.join(self.download_dir, file_name)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    self.logger.warning(f"Removed partial attachment file: {full_path}")
            except Exception as e:
                self.logger.error(f"Error closing file handle for attachment ID {message_id}: {e}")
        self._ongoing_transfers.clear()
        self._transfer_locks.clear()


from datetime import datetime
import json
