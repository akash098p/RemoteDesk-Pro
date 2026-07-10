"""
RemoteDesk Pro - Mouse Control Module
Implements mouse movement, clicking, and scrolling for remote control
"""

import platform
import threading
import time
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MouseButton(Enum):
    """Mouse button types"""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    DOUBLE = "double"

@dataclass
class MouseEvent:
    """Mouse event data structure"""
    event_type: str  # move, click, scroll
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[MouseButton] = None
    delta: Optional[int] = None
    timestamp: float = 0.0

class MouseController:
    """
    Handles mouse input simulation and synchronization.
    Supports movement, clicking, scrolling, and cursor visibility.
    """
    
    def __init__(self, connection_manager=None):
        self.conn_manager = connection_manager
        self._is_active = False
        self._cursor_visible = True
        self._position_lock = threading.Lock()
        self._current_position = (0, 0)
        self._click_callback: Optional[Callable] = None
        self._move_callback: Optional[Callable] = None
        
        # Platform-specific initialization
        self._init_platform()
    
    def _init_platform(self):
        """Initialize platform-specific mouse control"""
        system = platform.system()
        
        if system == "Windows":
            self._init_windows()
        elif system == "Linux":
            self._init_linux()
        else:
            self._init_generic()
    
    def _init_windows(self):
        """Windows-specific mouse initialization"""
        try:
            import pyautogui
            self._pyautogui = pyautogui
            self._platform = "windows"
            logger.info("Mouse controller initialized for Windows")
        except ImportError:
            logger.warning("pyautogui not available, using generic controller")
            self._init_generic()
    
    def _init_linux(self):
        """Linux-specific mouse initialization"""
        try:
            import pymouse
            self._pymouse = pymouse.PyMouse()
            self._platform = "linux"
            logger.info("Mouse controller initialized for Linux")
        except ImportError:
            self._init_generic()
    
    def _init_generic(self):
        """Generic fallback initialization"""
        self._platform = "generic"
        logger.warning("Using generic mouse controller - limited functionality")
    
    def move_to(self, x: int, y: int, duration: float = 0.0) -> bool:
        """
        Move mouse cursor to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate  
            duration: Movement duration in seconds (0 = instant)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_active:
            return False
        
        try:
            with self._position_lock:
                self._current_position = (x, y)
            
            if self._platform == "windows":
                self._pyautogui.moveTo(x, y, duration=duration)
            elif self._platform == "linux":
                self._pymouse.move(x, y)
            else:
                # Generic implementation would use ctypes or other methods
                pass
            
            # Send movement to remote device
            if self.conn_manager:
                event = MouseEvent(
                    event_type="move",
                    x=x,
                    y=y,
                    timestamp=time.time()
                )
                self.conn_manager.send_mouse_event(event)
            
            logger.debug(f"Mouse moved to ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
            return False
    
    def click(self, button: MouseButton = MouseButton.LEFT, 
              x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Perform mouse click.
        
        Args:
            button: Mouse button to click
            x: Optional X coordinate (uses current position if None)
            y: Optional Y coordinate (uses current position if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_active:
            return False
        
        try:
            # Move to position if coordinates provided
            if x is not None and y is not None:
                self.move_to(x, y)
            
            if self._platform == "windows":
                if button == MouseButton.LEFT:
                    self._pyautogui.click()
                elif button == MouseButton.RIGHT:
                    self._pyautogui.rightClick()
                elif button == MouseButton.MIDDLE:
                    self._pyautogui.middleClick()
                elif button == MouseButton.DOUBLE:
                    self._pyautogui.doubleClick()
                    
            elif self._platform == "linux":
                if button == MouseButton.LEFT:
                    self._pymouse.click(x or self._current_position[0], 
                                         y or self._current_position[1], 1)
                elif button == MouseButton.RIGHT:
                    self._pymouse.click(x or self._current_position[0],
                                         y or self._current_position[1], 2)
            
            # Send click event to remote
            if self.conn_manager:
                event = MouseEvent(
                    event_type="click",
                    x=x or self._current_position[0],
                    y=y or self._current_position[1],
                    button=button,
                    timestamp=time.time()
                )
                self.conn_manager.send_mouse_event(event)
            
            logger.debug(f"Mouse click: {button.value}")
            return True
            
        except Exception as e:
            logger.error(f"Mouse click failed: {e}")
            return False
    
    def scroll(self, dx: int = 0, dy: int = 0) -> bool:
        """
        Scroll mouse wheel.
        
        Args:
            dx: Horizontal scroll amount
            dy: Vertical scroll amount (positive = up, negative = down)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_active:
            return False
        
        try:
            if self._platform == "windows":
                self._pyautogui.scroll(dy)
                self._pyautogui.hscroll(dx)
            elif self._platform == "linux":
                # Linux scrolling implementation
                pass
            
            # Send scroll event
            if self.conn_manager:
                event = MouseEvent(
                    event_type="scroll",
                    delta=dy,
                    timestamp=time.time()
                )
                self.conn_manager.send_mouse_event(event)
            
            logger.debug(f"Mouse scroll: dx={dx}, dy={dy}")
            return True
            
        except Exception as e:
            logger.error(f"Mouse scroll failed: {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position."""
        with self._position_lock:
            return self._current_position
    
    def set_cursor_visibility(self, visible: bool) -> None:
        """
        Show or hide the mouse cursor.
        
        Args:
            visible: True to show cursor, False to hide
        """
        if self._cursor_visible == visible:
            return
        
        self._cursor_visible = visible
        
        if self._platform == "windows":
            try:
                import ctypes
                from ctypes import wintypes
                
                # Show/hide cursor
                ctypes.windll.user32.ShowCursor(visible)
                logger.debug(f"Cursor visibility set to: {visible}")
            except Exception as e:
                logger.warning(f"Failed to set cursor visibility: {e}")
    
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[bytes]:
        """
        Capture a region of the screen.
        
        Args:
            x, y: Top-left corner coordinates
            width, height: Region dimensions
            
        Returns:
            Image data as bytes, or None if failed
        """
        try:
            if self._platform == "windows":
                screenshot = self._pyautogui.screenshot(region=(x, y, width, height))
                # Convert to bytes
                from io import BytesIO
                img_bytes = BytesIO()
                screenshot.save(img_bytes, format='PNG')
                return img_bytes.getvalue()
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
        
        return None
    
    def activate(self) -> None:
        """Activate mouse control."""
        self._is_active = True
        logger.info("Mouse control activated")
    
    def deactivate(self) -> None:
        """Deactivate mouse control."""
        self._is_active = False
        logger.info("Mouse control deactivated")