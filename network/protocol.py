"""
===============================================================================
RemoteDesk Pro
File: network/protocol.py
Defines message protocols for network communication.
Enforces structured and type-safe message passing.
===============================================================================
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class MessageType(Enum):
    """Types of messages exchanged in the network."""
    SYSTEM = "system"
    CONNECTION = "connection"
    HANDSHAKE = "handshake"
    PING = "ping"
    PONG = "pong"
    DATA = "data"
    CONTROL = "control"
    ERROR = "error"
    LOG = "log"
    CHAT_MESSAGE = "chat_message"
    ATTACHMENT_METADATA = "attachment_metadata"
    ATTACHMENT_CHUNK = "attachment_chunk"
    CLIPBOARD_SYNC = "clipboard_sync"

class ProtocolVersion(Enum):
    """Supported protocol versions."""
    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"

class RemoteDeskMessage:
    """
    Standard message structure for all network communications.
    Ensures consistency across the application.
    """
    
    def __init__(
        self,
        message_type: str,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        version: str = ProtocolVersion.V2_0.value,
        sender_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        sequence_number: Optional[int] = None,
        compression: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message_type = message_type
        self.payload = payload
        self.message_id = message_id
        self.version = version
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.timestamp = timestamp or time.time()
        self.sequence_number = sequence_number
        self.compression = compression
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "type": self.message_type,
            "payload": self.payload,
            "id": self.message_id,
            "version": self.version,
            "sender": self.sender_id,
            "recipient": self.recipient_id,
            "timestamp": self.timestamp,
            "sequence": self.sequence_number,
            "compression": self.compression,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemoteDeskMessage":
        """Create a message from dictionary representation."""
        return cls(
            message_type=data["type"],
            payload=data["payload"],
            message_id=data.get("id"),
            version=data.get("version", ProtocolVersion.V2_0.value),
            sender_id=data.get("sender"),
            recipient_id=data.get("recipient"),
            timestamp=data.get("timestamp"),
            sequence_number=data.get("sequence"),
            compression=data.get("compression"),
            metadata=data.get("metadata"),
        )

    def is_valid(self) -> bool:
        """
        Validate the message.
        
        Returns:
            True if message is valid, False otherwise
        """
        if not self.message_type:
            return False
        
        if not isinstance(self.message_type, str) or not MessageType(self.message_type):
            return False
        
        if not isinstance(self.payload, dict):
            return False
        
        return True

    def __str__(self) -> str:
        return f"RemoteDeskMessage(type={self.message_type}, sender={self.sender_id}, recipient={self.recipient_id})"

class MessageFactory:
    """
    Factory class for creating different types of messages.
    Provides helper methods for common message types.
    """
    
    @staticmethod
    def create_handshake(username: str, client_id: str) -> "RemoteDeskMessage":
        """Create a handshake message."""
        return RemoteDeskMessage(
            message_type=MessageType.HANDSHAKE.value,
            payload={
                "username": username,
                "client_id": client_id,
                "platform": "windows",
                "version": ProtocolVersion.V2_0.value,
            },
        )

    @staticmethod
    def create_ping() -> "RemoteDeskMessage":
        """Create a ping message."""
        return RemoteDeskMessage(
            message_type=MessageType.PING.value,
            payload={},
        )

    @staticmethod
    def create_pong(ping_id: str) -> "RemoteDeskMessage":
        """Create a pong message."""
        return RemoteDeskMessage(
            message_type=MessageType.PONG.value,
            payload={
                "ping_id": ping_id,
                "response_time": time.time(),
            },
        )

    @staticmethod
    def create_data(message: str, file_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> "RemoteDeskMessage":
        """Create a data message."""
        payload = {"message": message}
        if file_path:
            payload["file_path"] = file_path
        if metadata:
            payload["metadata"] = metadata
            
        return RemoteDeskMessage(
            message_type=MessageType.DATA.value,
            payload=payload,
        )

    @staticmethod
    def create_system_info(cpu_usage: float, ram_usage: float, free_memory: float) -> "RemoteDeskMessage":
        """Create a system information message."""
        return RemoteDeskMessage(
            message_type=MessageType.SYSTEM.value,
            payload={
                "cpu_usage": cpu_usage,
                "ram_usage": ram_usage,
                "free_memory": free_memory,
            },
        )

    @staticmethod
    def create_error(error_type: str, error_message: str, details: Optional[Dict[str, Any]] = None) -> "RemoteDeskMessage":
        """Create an error message."""
        payload = {
            "error_type": error_type,
            "error_message": error_message,
        }
        if details:
            payload["details"] = details
            
        return RemoteDeskMessage(
            message_type=MessageType.ERROR.value,
            payload=payload,
        )

    @staticmethod
    def create_log(level: str, message: str, source: Optional[str] = None) -> "RemoteDeskMessage":
        """Create a log message."""
        payload = {
            "level": level,
            "message": message,
            "source": source or "system",
            "timestamp": time.time(),
        }
        return RemoteDeskMessage(
            message_type=MessageType.LOG.value,
            payload=payload,
        )

    @staticmethod
    def create_ping_pong_pair() -> Tuple["RemoteDeskMessage", "RemoteDeskMessage"]:
        """Create a ping-pong pair for round-trip time measurement."""
        import uuid
        ping_id = str(uuid.uuid4())
        ping = MessageFactory.create_ping()
        pong = MessageFactory.create_pong(ping_id)
        return ping, pong


import time
from typing import Tuple