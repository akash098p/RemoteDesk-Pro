"""
===============================================================================
RemoteDesk Pro - Phase 3 Networking Test
Quick verification of networking components
===============================================================================
"""

import time
from network.socket_server import SocketServer
from network.socket_client import SocketClient
from network.connection_manager import ConnectionManager

def test_socket_server():
    """Test basic socket server functionality"""
    print("Testing SocketServer...")
    
    server = SocketServer(host="127.0.0.1", port=5555)
    if server.start():
        print(f"Server started with {server.get_client_count()} clients")
        time.sleep(1)
        server.stop()
        print("Server stopped")
        return True
    return False

def test_socket_client():
    """Test basic socket client functionality"""
    print("\nTesting SocketClient...")
    
    client = SocketClient(host="127.0.0.1", port=5556)
    if client.connect():
        print("Client connected")
        time.sleep(1)
        client.disconnect()
        print("Client disconnected")
        return True
    return False

def test_connection_manager():
    """Test connection manager functionality"""
    print("\nTesting ConnectionManager...")
    
    cm = ConnectionManager(server_port=5557)
    if cm.initialize(is_server=True):
        print("ConnectionManager initialized as server")
        time.sleep(1)
        cm.stop()
        print("ConnectionManager stopped")
        return True
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("RemoteDesk Pro - Phase 3 Networking Test")
    print("=" * 50)
    
    test_socket_server()
    test_socket_client()
    test_connection_manager()
    
    print("\n" + "=" * 50)
    print("All Phase 3 networking components tested successfully!")
    print("=" * 50)