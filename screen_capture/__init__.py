"""
===============================================================================
RemoteDesk Pro - Screen Capture Module
Implements screen sharing functionality for RemoteDesk Pro.
===============================================================================
"""

from screen_capture.capture import ScreenCapture, create_screen_capture
from screen_capture.streaming_server import StreamingServer, create_streaming_server
from screen_capture.streaming_client import StreamingClient, create_streaming_client

__all__ = [
    'ScreenCapture',
    'create_screen_capture',
    'StreamingServer',
    'create_streaming_server',
    'StreamingClient',
    'create_streaming_client',
]