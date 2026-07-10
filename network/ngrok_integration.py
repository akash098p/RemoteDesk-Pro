"""
===============================================================================
RemoteDesk Pro
File: network/ngrok_integration.py
Provides Ngrok tunnel management for remote connections.
Enables connections through NAT and firewall restrictions.
===============================================================================
"""

from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

class NgrokIntegration:
    """
    Handles Ngrok tunnel creation and management.
    Allows RemoteDesk Pro to be accessible from anywhere.
    """
    
    def __init__(
        self,
        auth_token: Optional[str] = None,
        region: str = "us",
        on_status_change: Optional[Callable[[str, dict], None]] = None,
    ) -> None:
        """
        Initialize Ngrok integration.
        
        Args:
            auth_token: Ngrok authentication token
            region: Ngrok region (us, eu, ap, au, sa, jp, in)
            on_status_change: Callback for status updates (status, details)
        """
        self._auth_token = auth_token
        self._region = region
        self._on_status_change = on_status_change
        self._tunnel = None
        self._public_url: Optional[str] = None
        self._is_active = False
    
    def start_tunnel(
        self,
        service: str = "tcp",
        port: int = 5000,
        proto: str = "tcp",
    ) -> bool:
        """
        Start an Ngrok tunnel.
        
        Args:
            service: Service type (tcp, http, tcp)
            port: Local port to expose
            proto: Protocol (tcp, http)
            
        Returns:
            True if tunnel started successfully, False otherwise
        """
        try:
            # Import pyngrok here to allow graceful failure if not installed
            from pyngrok import ngrok
            
            # Set auth token if provided
            if self._auth_token:
                ngrok.set_auth_token(self._auth_token)
            
            # Configure region
            ngrok.set_default_region(self._region)
            
            # Start tunnel
            if proto == "http":
                self._tunnel = ngrok.connect(port, proto)
            else:
                self._tunnel = ngrok.connect(port)
            
            if self._tunnel:
                self._public_url = self._tunnel.public_url
                self._is_active = True
                
                if self._on_status_change:
                    self._on_status_change("active", {
                        "public_url": self._public_url,
                        "tunnel": str(self._tunnel)
                    })
                
                return True
            
            return False
            
        except ImportError:
            # pyngrok not installed - return False for graceful handling
            if self._on_status_change:
                self._on_status_change("error", {
                    "message": "pyngrok not installed. Install with: pip install pyngrok"
                })
            return False
        except Exception as e:
            if self._on_status_change:
                self._on_status_change("error", {"message": str(e)})
            return False
    
    def stop_tunnel(self) -> bool:
        """
        Stop the active Ngrok tunnel.
        
        Returns:
            True if tunnel stopped successfully, False otherwise
        """
        try:
            if self._tunnel:
                from pyngrok import ngrok
                ngrok.disconnect(self._tunnel.public_url)
                self._tunnel = None
                self._public_url = None
                self._is_active = False
                
                if self._on_status_change:
                    self._on_status_change("stopped", {})
                
                return True
            return False
        except Exception as e:
            if self._on_status_change:
                self._on_status_change("error", {"message": str(e)})
            return False
    
    def get_public_url(self) -> Optional[str]:
        """
        Get the public URL for the active tunnel.
        
        Returns:
            Public URL string or None if no active tunnel
        """
        return self._public_url
    
    def is_active(self) -> bool:
        """Check if a tunnel is currently active."""
        return self._is_active

    def log_info(self, message: str) -> None:
        """Log info message."""
        logger.info(message)
        if self._on_status_change:
            self._on_status_change("info", {"message": message})

    def log_error(self, message: str) -> None:
        """Log error message."""
        logger.error(message)
        if self._on_status_change:
            self._on_status_change("error", {"message": message})

    def connect_devices(self, local_port: int, remote_url: str) -> bool:
        """
        Establish cross-network connection between devices.

        Args:
            local_port: Port exposed by local device
            remote_url: Public URL of remote device (e.g., 'ngrok.io:5000')

        Returns:
            True if connection established, False otherwise
        """
        try:
            # Start local tunnel if not active
            if not self.is_active():
                self.start_tunnel(port=local_port)

            # Connect to remote device
            if not self.is_active():
                self.log_error("Local tunnel inactive")
                return False

            # Validate remote URL format
            if not remote_url.startswith('http'):
                remote_url = f'http://{remote_url}'

            # Test connection using simple HTTP request
            import requests
            response = requests.get(remote_url, timeout=5)
            if response.status_code == 200:
                self.log_info(f"Connected to {remote_url}")
                return True
            else:
                self.log_error(f"Connection failed to {remote_url}: {response.status_code}")
                return False
        except Exception as e:
            self.log_error(f"Network connection error: {str(e)}")
            return False
    
    def get_local_port(self) -> int:
        """
        Get the local port being tunneled.
        
        Returns:
            Local port number or 0 if not active
        """
        if self._tunnel and hasattr(self._tunnel, 'proto'):
            return self._tunnel.proto.get("port", 0)
        return 0
    
    def close(self) -> None:
        """Clean up resources."""
        if self._is_active:
            self.stop_tunnel()


# Convenience function
def create_ngrok_tunnel(
    port: int = 5000,
    auth_token: Optional[str] = None,
    region: str = "us",
    on_status_change: Optional[Callable[[str, dict], None]] = None,
) -> Optional[NgrokIntegration]:
    """
    Create and start an Ngrok tunnel.
    
    Args:
        port: Local port to expose
        auth_token: Ngrok authentication token
        region: Ngrok region
        on_status_change: Callback for status updates
        
    Returns:
        NgrokIntegration instance or None if failed
    """
    ngrok = NgrokIntegration(auth_token=auth_token, region=region, on_status_change=on_status_change)
    if ngrok.start_tunnel(port=port):
        return ngrok
    return None