"""
===============================================================================
RemoteDesk Pro
File: network/packet_system.py
Provides serialization/deserialization for network messages.
Ensures consistent message format across the application.
===============================================================================
"""

import json
import struct
from typing import Dict, Any

class PacketSystem:
    """
    Handles serialization and deserialization of network packets.
    Ensures consistency in message format across RemoteDesk Pro.
    """

    @staticmethod
    def create_packet(data: Dict[str, Any]) -> bytes:
        """
        Serialize a dictionary into a network packet.
        
        Args:
            data: Dictionary to serialize
            
        Returns:
            Byte representation of the data with length prefix
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, ensure_ascii=False)
            
            # Add length prefix for easier parsing
            length_prefix = struct.pack('!I', len(json_data))
            packet = length_prefix + json_data.encode('utf-8')
            
            return packet
            
        except Exception as e:
            # Import here to avoid circular imports
            from core.logger import logger
            logger.error(f"Failed to create packet: {e}")
            return b''
    
    @staticmethod
    def parse_packet(data: bytes) -> Dict[str, Any]:
        """
        Deserialize a network packet into a dictionary.
        
        Args:
            data: Byte representation of a packet
            
        Returns:
            Parsed dictionary or empty dict if parsing fails
        """
        try:
            # Extract length prefix to determine message length
            if len(data) < 4:
                from core.logger import logger
                logger.error("Packet too short (no length prefix)")
                return {}
            
            length = struct.unpack('!I', data[:4])[0]
            if len(data) < 4 + length:
                from core.logger import logger
                logger.error(f"Packet incomplete. Expected {length} bytes of payload, got {len(data) - 4}")
                return {}
            
            # Extract payload and decode JSON
            payload = data[4:4 + length].decode('utf-8')
            parsed_data = json.loads(payload)
            
            from core.logger import logger
            logger.info(f"Packet parsed: {parsed_data}")
            
            return parsed_data
            
        except (struct.error, json.JSONDecodeError) as e:
            from core.logger import logger
            logger.error(f"Failed to parse packet: {e}")
            return {}
        except Exception as e:
            from core.logger import logger
            logger.error(f"Unexpected error parsing packet: {e}")
            return {}

# Convenience functions
def serialize_message(data: Dict[str, Any]) -> bytes:
    """Serialize a single message."""
    return PacketSystem.create_packet(data)

def deserialize_message(data: bytes) -> Dict[str, Any]:
    """Deserialize a message."""
    return PacketSystem.parse_packet(data)