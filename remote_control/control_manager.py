"""
RemoteDesk Pro - Remote Control Manager
Central coordination of mouse, keyboard, permissions, and shortcuts
"""

import platform
import threading
import time
import uuid
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ControlSession:
    """Remote control session information"""
    session_id: str
    device_id: str
    start_time: float
    is_active: bool = True
    timeout: int = 300
    features: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = {
                "mouse": True,
                "keyboard": True,
                "shortcuts": True,
                "file_transfer": True
            }

class RemoteControlManager:
    """
    Central manager for remote control functionality.
    Coordinates mouse, keyboard, permissions, and shortcuts.
    """
    
    def __init__(self, connection_manager=None):
        self.conn_manager = connection_manager
        self._is_active = False
        self._sessions: Dict[str, ControlSession] = {}
        self._current_session: Optional[ControlSession] = None
        self._lock = threading.Lock()
        
        # Initialize sub-components
        self._init_components()
        
        # Callbacks
        self._session_callback: Optional[Callable] = None
        self._event_callback: Optional[Callable] = None
    
    def _init_components(self):
        """Initialize control components"""
        # Import here to avoid circular imports
        from .mouse import MouseController
        from .keyboard import KeyboardController
        from .permissions import PermissionManager
        from .shortcuts import ShortcutManager, shortcut_manager
        
        self.mouse = MouseController(connection_manager=self.conn_manager)
        self.keyboard = KeyboardController(connection_manager=self.conn_manager)
        self.permissions = PermissionManager()
        self.shortcuts = shortcut_manager  # Use global instance
        
        # Set up permission callback
        self.permissions.set_permission_callback(self._on_permission_request)
    
    def _on_permission_request(self, request) -> None:
        """Handle permission request from PermissionManager"""
        # This would trigger UI dialog
        logger.info(f"Permission request from {request.requested_by} for device {request.device_id}")
        
        # Auto-grant if enabled
        if self.permissions._auto_grant:
            self.permissions.grant_permission(request.request_id, granted=True)
    
    def request_control(self, device_id: str, 
                       features: Optional[Dict[str, bool]] = None) -> Optional[str]:
        """
        Request remote control of a device.
        
        Args:
            device_id: Target device identifier
            features: Optional feature permissions
            
        Returns:
            Session ID if granted, None otherwise
        """
        if not self.conn_manager or self.conn_manager.get_connection_status() != "connected":
            logger.warning("No active connection for remote control")
            return None
        
        # Check if already controlling
        with self._lock:
            if self._current_session and self._current_session.is_active:
                logger.warning("Already in a control session")
                return None
        
        # Request permission
        if self.permissions._auto_grant:
            granted = True
        else:
            # In real implementation, this would show a dialog
            granted = self._show_permission_dialog(device_id)
        
        if not granted:
            logger.info(f"Control request denied for device: {device_id}")
            return None
        
        # Create session
        session_id = str(uuid.uuid4())
        session = ControlSession(
            session_id=session_id,
            device_id=device_id,
            start_time=time.time(),
            features=features or {}
        )
        
        with self._lock:
            self._sessions[session_id] = session
            self._current_session = session
        
        # Activate components
        self._activate_components()
        
        # Start timeout monitor
        self._start_timeout_monitor(session_id)
        
        # Notify callback
        if self._session_callback:
            try:
                self._session_callback("started", session)
            except Exception as e:
                logger.error(f"Session callback error: {e}")
        
        logger.info(f"Remote control session started: {session_id}")
        return session_id
    
    def _show_permission_dialog(self, device_id: str) -> bool:
        """Show permission dialog for control request"""
        try:
            import tkinter.messagebox as msgbox
            result = msgbox.askyesno(
                "Remote Control Request",
                f"Allow remote control of {device_id}?\n\n"
                "This will enable mouse and keyboard control "
                "with full access to the remote device."
            )
            return result
        except Exception as e:
            logger.error(f"Permission dialog failed: {e}")
            return False
    
    def _activate_components(self) -> None:
        """Activate mouse and keyboard controllers"""
        self.mouse.activate()
        self.keyboard.activate()
        self._is_active = True
        
        # Start shortcut listener
        self.shortcuts.start_listening()
        
        logger.info("Remote control components activated")
    
    def _deactivate_components(self) -> None:
        """Deactivate mouse and keyboard controllers"""
        self.mouse.deactivate()
        self.keyboard.deactivate()
        self._is_active = False
        
        # Stop shortcut listener
        self.shortcuts.stop_listening()
        
        logger.info("Remote control components deactivated")
    
    def _start_timeout_monitor(self, session_id: str) -> None:
        """Start session timeout monitoring"""
        def monitor():
            while True:
                time.sleep(30)  # Check every 30 seconds
                with self._lock:
                    if session_id not in self._sessions:
                        break
                    session = self._sessions[session_id]
                    if not session.is_active:
                        break
                    if time.time() - session.start_time > session.timeout:
                        self._end_session(session_id)
                        break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def end_control(self, session_id: Optional[str] = None) -> bool:
        """
        End remote control session.
        
        Args:
            session_id: Specific session to end, or None for current
            
        Returns:
            True if session ended
        """
        with self._lock:
            if session_id is None:
                session_id = self._current_session.session_id if self._current_session else None
            
            if session_id and session_id in self._sessions:
                return self._end_session(session_id)
            return False
    
    def _end_session(self, session_id: str) -> bool:
        """Internal session termination"""
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        session.is_active = False
        
        # Deactivate components
        self._deactivate_components()
        
        # Notify callback
        if self._session_callback:
            try:
                self._session_callback("ended", session)
            except Exception as e:
                logger.error(f"Session end callback error: {e}")
        
        del self._sessions[session_id]
        if self._current_session and self._current_session.session_id == session_id:
            self._current_session = None
        
        logger.info(f"Remote control session ended: {session_id}")
        return True
    
    def get_active_session(self) -> Optional[ControlSession]:
        """Get currently active control session."""
        with self._lock:
            return self._current_session
    
    def get_all_sessions(self) -> List[ControlSession]:
        """Get all active sessions."""
        with self._lock:
            return list(self._sessions.values())
    
    def is_active(self) -> bool:
        """Check if remote control is active."""
        return self._is_active
    
    def set_session_callback(self, callback: Callable) -> None:
        """Set callback for session events."""
        self._session_callback = callback
    
    def set_event_callback(self, callback: Callable) -> None:
        """Set callback for control events."""
        self._event_callback = callback
    
    def send_mouse_event(self, event) -> None:
        """Forward mouse event to remote device"""
        if self.conn_manager and self._is_active:
            # Send via connection manager
            self.conn_manager.send_mouse_event(event)
    
    def send_keyboard_event(self, event) -> None:
        """Forward keyboard event to remote device"""
        if self.conn_manager and self._is_active:
            self.conn_manager.send_keyboard_event(event)
    
    def shutdown(self) -> None:
        """Shutdown remote control manager"""
        with self._lock:
            for session_id in list(self._sessions.keys()):
                self._end_session(session_id)
        
        self._deactivate_components()
        logger.info("Remote control manager shut down")


# Factory function for easy integration
def create_remote_control_manager(connection_manager=None) -> RemoteControlManager:
    """Create and return a configured RemoteControlManager instance."""
    return RemoteControlManager(connection_manager)