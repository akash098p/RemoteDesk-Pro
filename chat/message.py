
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from core.constants import JSON_INDENT, JSON_SORT_KEYS

@dataclass
class ChatMessage:
    """
    Represents a single chat message, encapsulating its content, sender,
    timestamp, and other relevant metadata.
    """
    sender: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "text"  # e.g., "text", "emoji", "attachment"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the ChatMessage instance to a dictionary."""
        return {
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Creates a ChatMessage instance from a dictionary."""
        return cls(
            sender=data["sender"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata", {})
        )

    def serialize(self) -> str:
        """Serializes the ChatMessage to a JSON string."""
        return json.dumps(self.to_dict(), indent=JSON_INDENT, sort_keys=JSON_SORT_KEYS)

    @classmethod
    def deserialize(cls, json_string: str) -> 'ChatMessage':
        """Deserializes a JSON string back into a ChatMessage instance."""
        data = json.loads(json_string)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Returns a string representation of the chat message."""
        return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender}: {self.content}"
