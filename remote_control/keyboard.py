"""
RemoteDesk Pro - Keyboard Control Module
Implements keyboard input simulation for remote control
"""

import platform
import threading
import time
from typing import Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class KeyAction(Enum):
    """Keyboard action types"""
    PRESS = "press"
    RELEASE = "release"
    TYPE = "type"
    COMBO = "combo"

@dataclass
class KeyEvent:
    """Keyboard event data structure"""
    action: KeyAction
    key: Optional[str] = None
    combo: Optional[List[str]] = None
    timestamp: float = 0.0

# Virtual key codes for Windows
VK_CODES = {
    'ctrl': 0x11,
    'shift': 0x10,
    'alt': 0x12,
    'win': 0x5B,
    'enter': 0x0D,
    'esc': 0x1B,
    'tab': 0x09,
    'space': 0x20,
    'backspace': 0x08,
    'delete': 0x2E,
    'up': 0x26,
    'down': 0x28,
    'left': 0x25,
    'right': 0x27,
    'f1': 0x70,
    'f2': 0x71,
    'f3': 0x72,
    'f4': 0x73,
    'f5': 0x74,
    'f6': 0x75,
    'f7': 0x76,
    'f8': 0x77,
    'f9': 0x78,
    'f10': 0x79,
    'f11': 0x7A,
    'f12': 0x7B,
}

class KeyboardController:
    """
    Handles keyboard input simulation and hotkey management.
    Supports individual key presses, key combinations, and typing.
    """
    
    def __init__(self, connection_manager=None):
        self.conn_manager = connection_manager
        self._is_active = False
        self._locked = False
        self._typed_buffer = ""
        self._callback: Optional[Callable] = None
        
        # Platform-specific initialization
        self._init_platform()
    
    def _init_platform(self):
        """Initialize platform-specific keyboard control"""
        system = platform.system()
        
        try:
            if system == "Windows":
                import ctypes
                from ctypes import wintypes
                self._user32 = ctypes.windll.user32
                self._platform = "windows"
                logger.info("Keyboard controller initialized for Windows")
            elif system == "Linux":
                import Xlib
                self._platform = "linux"
                logger.info("Keyboard controller initialized for Linux")
            else:
                self._platform = "generic"
                logger.warning("Using generic keyboard controller")
        except ImportError as e:
            logger.warning(f"Platform-specific keyboard control not available: {e}")
            self._platform = "generic"
    
    def press_key(self, key: str) -> bool:
        """
        Press a single key.
        
        Args:
            key: Key name (e.g., 'a', 'enter', 'ctrl')
            
        Returns:
            True if successful
        """
        if not self._is_active or self._locked:
            return False
        
        try:
            if self._platform == "windows":
                vk_code = VK_CODES.get(key.lower(), ord(key.upper()) if len(key) == 1 else 0)
                if vk_code:
                    self._user32.keybd_event(vk_code, 0, 0, 0)
            
            elif self._platform == "generic":
                # Fallback to pynput
                import pynput.keyboard as kb
                kb.Controller().press(key)
            
            # Send to remote
            if self.conn_manager:
                event = KeyEvent(
                    action=KeyAction.PRESS,
                    key=key,
                    timestamp=time.time()
                )
                self.conn_manager.send_keyboard_event(event)
            
            logger.debug(f"Key pressed: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return False
    
    def release_key(self, key: str) -> bool:
        """
        Release a single key.
        
        Args:
            key: Key name to release
            
        Returns:
            True if successful
        """
        if not self._is_active or self._locked:
            return False
        
        try:
            if self._platform == "windows":
                vk_code = VK_CODES.get(key.lower(), ord(key.upper()) if len(key) == 1 else 0)
                if vk_code:
                    self._user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
            
            elif self._platform == "generic":
                import pynput.keyboard as kb
                kb.Controller().release(key)
            
            if self.conn_manager:
                event = KeyEvent(
                    action=KeyAction.RELEASE,
                    key=key,
                    timestamp=time.time()
                )
                self.conn_manager.send_keyboard_event(event)
            
            logger.debug(f"Key released: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Key release failed: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text string with simulated keyboard input.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes in seconds
            
        Returns:
            True if successful
        """
        if not self._is_active or self._locked:
            return False
        
        try:
            if self._platform == "windows":
                for char in text:
                    vk_code = ord(char)
                    self._user32.keybd_event(vk_code, 0, 0, 0)  # Press
                    self._user32.keybd_event(vk_code, 0, 2, 0)  # Release
                    time.sleep(interval)
            
            elif self._platform == "generic":
                import pynput.keyboard as kb
                kb.Controller().type(text)
            
            if self.conn_manager:
                event = KeyEvent(
                    action=KeyAction.TYPE,
                    key=text,
                    timestamp=time.time()
                )
                self.conn_manager.send_keyboard_event(event)
            
            logger.debug(f"Text typed: {text[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Text typing failed: {e}")
            return False
    
    def send_combo(self, keys: List[str]) -> bool:
        """
        Send a key combination (hotkey).
        
        Args:
            keys: List of keys to press simultaneously (e.g., ['ctrl', 'c'])
            
        Returns:
            True if successful
        """
        if not self._is_active or self._locked:
            return False
        
        try:
            if self._platform == "windows":
                # Press all keys
                for key in keys:
                    vk_code = VK_CODES.get(key.lower(), ord(key.upper()) if len(key) == 1 else 0)
                    if vk_code:
                        self._user32.keybd_event(vk_code, 0, 0, 0)
                
                # Release all keys in reverse order
                for key in reversed(keys):
                    vk_code = VK_CODES.get(key.lower(), ord(key.upper()) if len(key) == 1 else 0)
                    if vk_code:
                        self._user32.keybd_event(vk_code, 0, 2, 0)
            
            elif self._platform == "generic":
                import pynput.keyboard as kb
                kb.Controller().press(keys[0] if keys else '')
                for key in keys[1:]:
                    kb.Controller().press(key)
                for key in reversed(keys):
                    kb.Controller().release(key)
            
            if self.conn_manager:
                event = KeyEvent(
                    action=KeyAction.COMBO,
                    combo=keys,
                    timestamp=time.time()
                )
                self.conn_manager.send_keyboard_event(event)
            
            logger.debug(f"Hotkey sent: {'+'.join(keys)}")
            return True
            
        except Exception as e:
            logger.error(f"Hotkey combination failed: {e}")
            return False
    
    def lock_keyboard(self) -> None:
        """Temporarily disable keyboard input."""
        self._locked = True
        logger.info("Keyboard locked")
    
    def unlock_keyboard(self) -> None:
        """Re-enable keyboard input."""
        self._locked = False
        logger.info("Keyboard unlocked")
    
    def activate(self) -> None:
        """Activate keyboard control."""
        self._is_active = True
        logger.info("Keyboard control activated")
    
    def deactivate(self) -> None:
        """Deactivate keyboard control."""
        self._is_active = False
        logger.info("Keyboard control deactivated")