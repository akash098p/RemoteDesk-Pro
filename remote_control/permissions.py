"""
RemoteDesk Pro - Permission Manager
Handles remote control permission requests and session management
"""

import threading
import time
import uuid
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PermissionLevel(Enum):
    """Permission levels for remote control"""
    DENIED = "denied"
    REQUIRED_CONFIRMATION = "required_confirmation"
    GRANTED = "granted"
    TEMPORARY = "temporary"

@dataclass
class PermissionRequest:
    """Represents a permission request"""
    request_id: str
    device_id: str
    requested_by: str
    timestamp: float
    level: PermissionLevel
    features: Dict[str, bool] = field(default_factory=dict)
    granted: bool = False
    response_callback: Optional[Callable] = None

@dataclass
class ControlSession:
    """Active remote control session"""
    session_id: str
    device_id: str
    start_time: float
    timeout: int = 300  # 5 minutes default
    permissions: PermissionLevel = PermissionLevel.GRANTED
    is_active: bool = True

class PermissionManager:
    """
    Manages remote control permissions and session lifecycle.
    Implements confirmation dialogs, timeout handling, and audit logging.
    """
    
    def __init__(self):
        self._requests: Dict[str, PermissionRequest] = {}
        self._sessions: Dict[str, ControlSession] = {}
        self._lock = threading.Lock()
        self._default_timeout = 300
        self._auto_grant = False
        self._permission_callback: Optional[Callable] = None
    
    def request_permission(self, device_id: str, requested_by: str,
                          features: Dict[str, bool]) -> str:
        """
        Create a new permission request.
        
        Args:
            device_id: Target device identifier
            requested_by: Requester identification
            features: Dictionary of requested features
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        request = PermissionRequest(
            request_id=request_id,
            device_id=device_id,
            requested_by=requested_by,
            timestamp=time.time(),
            level=PermissionLevel.REQUIRED_CONFIRMATION,
            features=features
        )
        
        with self._lock:
            self._requests[request_id] = request
        
        logger.info(f"Permission request created: {request_id} from {requested_by}")
        
        # Trigger callback for UI notification
        if self._permission_callback:
            self._permission_callback(request)
        
        return request_id
    
    def grant_permission(self, request_id: str, granted: bool = True,
                        timeout: Optional[int] = None) -> bool:
        """
        Grant or deny a permission request.
        
        Args:
            request_id: Request identifier
            granted: True to grant, False to deny
            timeout: Optional session timeout in seconds
            
        Returns:
            True if operation successful
        """
        with self._lock:
            if request_id not in self._requests:
                logger.warning(f"Permission request not found: {request_id}")
                return False
            
            request = self._requests[request_id]
            request.granted = granted
            
            if granted:
                request.level = PermissionLevel.GRANTED
                # Create control session
                session = ControlSession(
                    session_id=request_id,
                    device_id=request.device_id,
                    start_time=time.time(),
                    timeout=timeout or self._default_timeout,
                    permissions=PermissionLevel.GRANTED
                )
                self._sessions[request_id] = session
                logger.info(f"Permission granted: {request_id}")
            else:
                request.level = PermissionLevel.DENIED
                logger.info(f"Permission denied: {request_id}")
            
            # Call response callback
            if request.response_callback:
                try:
                    request.response_callback(granted)
                except Exception as e:
                    logger.error(f"Permission response callback failed: {e}")
            
            return True
    
    def get_session(self, session_id: str) -> Optional[ControlSession]:
        """Get active control session by ID."""
        with self._lock:
            return self._sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """
        End an active control session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
        """
        with self._lock:
            if session_id in self._sessions:
                self._sessions[session_id].is_active = False
                del self._sessions[session_id]
                logger.info(f"Control session ended: {session_id}")
                return True
            return False
    
    def check_session_timeout(self) -> None:
        """Check and expire timed-out sessions."""
        current_time = time.time()
        expired_sessions = []
        
        with self._lock:
            for session_id, session in self._sessions.items():
                if current_time - session.start_time > session.timeout:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self._sessions[session_id].is_active = False
                del self._sessions[session_id]
                logger.info(f"Session timed out: {session_id}")
    
    def get_active_sessions(self) -> List[ControlSession]:
        """Get list of active control sessions."""
        with self._lock:
            return list(self._sessions.values())
    
    def set_permission_callback(self, callback: Callable) -> None:
        """Set callback for permission requests."""
        self._permission_callback = callback
    
    def set_auto_grant(self, enabled: bool) -> None:
        """Enable/disable automatic permission granting."""
        self._auto_grant = enabled
    
    def set_default_timeout(self, timeout: int) -> None:
        """Set default session timeout."""
        self._default_timeout = timeout
    
    def cleanup_expired_requests(self) -> None:
        """Remove expired permission requests."""
        current_time = time.time()
        expired = []
        
        with self._lock:
            for request_id, request in self._requests.items():
                # Requests older than 5 minutes
                if current_time - request.timestamp > 300:
                    expired.append(request_id)
            
            for request_id in expired:
                del self._requests[request_id]