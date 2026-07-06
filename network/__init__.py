"""
===============================================================================
RemoteDesk Pro - Network Module
Implements networking functionality for RemoteDesk Pro.
===============================================================================
"""

from network.socket_server import SocketServer
from network.socket_client import SocketClient
from network.connection_manager import ConnectionManager
from network.packet_system import PacketSystem
from network.encryption import Encryption
from network.ngrok_integration import NgrokIntegration
from network.heartbeat import Heartbeat, create_heartbeat
from network.device_discovery import DeviceDiscovery

__all__ = [
    'SocketServer',
    'SocketClient',
    'ConnectionManager',
    'PacketSystem',
    'Encryption',
    'NgrokIntegration',
    'Heartbeat',
    'create_heartbeat',
    'DeviceDiscovery',
]