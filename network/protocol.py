"""
===============================================================================
RemoteDesk Pro
File: network/protocol.py
Defines the message structure and protocol between clients and servers
===============================================================================
"""

import time
from enum import Enum
from dataclasses import dataclass
import json
from typing import Dict, Any

class MessageType(Enum):
    """Types of messages exchanged between client and server"""
    SCREEN_FRAME = 1       # Screen sharing frame message
    MOUSE_EVENT = 2       # Mouse movement or button click
    KEYBOARD_EVENT = 3    # Keyboard keystroke
    CONTROL_REQUEST = 4   # Permission request from remote client
    HEARTBEAT = 5         # Heartbeat message for connection checking
    AUDIO_FRAME = 6       # Audio frame for real-time audio streaming
    CHAT_MESSAGE = 7      # Text chat between peers

@dataclass
class RemoteDeskMessage:
    """Data structure for messages exchanged between components"""
    type: MessageType
    payload: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "type": self.type.value,
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RemoteDeskMessage':
        """Create RemoteDeskMessage from dictionary"""
        msg_type = MessageType(data["type"])
        payload = data["payload"]
        return cls(type=msg_type, payload=payload)
    
    def to_json(self) -> str:
        """Serialize message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RemoteDeskMessage':
        """Deserialize JSON string to RemoteDeskMessage"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"RemoteDeskMessage(type={self.type}, payload={self.payload})"

class MessageFactory:
    """Factory class for creating RemoteDeskMessage instances"""
    
    @staticmethod
    def create_screen_frame(frame_data: bytes, timestamp: float = None) -> RemoteDeskMessage:
        """Create a screen frame message"""
        payload = {
            "frame_data": frame_data,
            "timestamp": timestamp or time.time(),
            "width": 1920,  # Default width
            "height": 1080  # Default height
        }
        return RemoteDeskMessage(type=MessageType.SCREEN_FRAME, payload=payload)
    
    @staticmethod
    def create_mouse_event(x: int, y: int, button: str = "left", action: str = "move") -> RemoteDeskMessage:
        """Create a mouse event message"""
        payload = {
            "x": x,
            "y": y,
            "button": button,
            "action": action
        }
        return RemoteDeskMessage(type=MessageType.MOUSE_EVENT, payload=payload)
    
    @staticmethod
    def create_keyboard_event(key: str, action: str = "press") -> RemoteDeskMessage:
        """Create a keyboard event message"""
        payload = {
            "key": key,
            "action": action
        }
        return RemoteDeskMessage(type=MessageType.KEYBOARD_EVENT, payload=payload)
    
    @staticmethod
    def create_audio_frame(audio_data: bytes, timestamp: float = None) -> RemoteDeskMessage:
        """Create an audio frame message for real-time audio streaming"""
        payload = {
            "audio_data": audio_data,
            "timestamp": timestamp or time.time()
        }
        return RemoteDeskMessage(type=MessageType.AUDIO_FRAME, payload=payload)
    
    @staticmethod
    def create_control_request(request_type: str, data: Dict[str, Any]) -> RemoteDeskMessage:
        """Create a control request message"""
        payload = {
            "type": request_type,
            "data": data
        }
        return RemoteDeskMessage(type=MessageType.CONTROL_REQUEST, payload=payload)
