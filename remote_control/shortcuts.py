"""
RemoteDesk Pro - Shortcut Manager
Handles keyboard shortcuts and hotkeys for remote control operations
"""

import threading
import time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ShortcutType(Enum):
    """Types of shortcuts"""
    SYSTEM = "system"
    APPLICATION = "application"
    REMOTE_CONTROL = "remote_control"
    CUSTOM = "custom"

@dataclass
class Shortcut:
    """Represents a keyboard shortcut"""
    id: str
    name: str
    keys: List[str]  # e.g., ['ctrl', 'c'] for copy
    action: Callable
    description: str
    shortcut_type: ShortcutType
    enabled: bool = True
    global_scope: bool = False  # Whether it works globally or only in app

class ShortcutManager:
    """
    Manages keyboard shortcuts and hotkeys.
    Supports registration, execution, and global/system-level shortcuts.
    """
    
    def __init__(self):
        self._shortcuts: Dict[str, Shortcut] = {}
        self._global_shortcuts: Dict[str, Shortcut] = {}
        self._listener_thread: Optional[threading.Thread] = None
        self._is_listening = False
        self._pressed_keys: set = set()
        self._lock = threading.Lock()
        
        # Register default shortcuts
        self._register_default_shortcuts()
    
    def _register_default_shortcuts(self) -> None:
        """Register default application shortcuts."""
        # Remote control shortcuts
        self.register_shortcut(
            id="rc_toggle",
            name="Toggle Remote Control",
            keys=["ctrl", "alt", "r"],
            action=self._toggle_remote_control,
            description="Enable/disable remote control mode",
            shortcut_type=ShortcutType.REMOTE_CONTROL,
            global_scope=True
        )
        
        self.register_shortcut(
            id="rc_screenshot",
            name="Take Screenshot",
            keys=["ctrl", "shift", "s"],
            action=self._take_screenshot,
            description="Capture and share screen",
            shortcut_type=ShortcutType.REMOTE_CONTROL,
            global_scope=True
        )
        
        self.register_shortcut(
            id="rc_pause",
            name="Pause/Resume Control",
            keys=["ctrl", "shift", "p"],
            action=self._pause_resume_control,
            description="Pause or resume remote control session",
            shortcut_type=ShortcutType.REMOTE_CONTROL,
            global_scope=True
        )
        
        self.register_shortcut(
            id="rc_lock_kb",
            name="Lock Keyboard",
            keys",
            keys=["ctrl", "alt", "k"],
            action=self._lock_keyboard,
            description="Temporarily disable remote keyboard input",
            shortcut_type=ShortcutType.REMOTE_CONTROL,
            global_scope=True
        )
        
        self.register_shortcut(
            id="rc_show_perms",
            name="Show Permissions",
            keys=["ctrl", "win", "h"],
            action=self._show_permissions,
            description="Display permission management dialog",
            shortcut_type=ShortcutType.REMOTE_CONTROL,
            global_scope=True
        )
        
        # Application shortcuts
        self.register_shortcut(
            id="app_settings",
            name="Open Settings",
            keys=["ctrl", ","],
            action=self._open_settings,
            description="Open application settings",
            shortcut_type=ShortcutType.APPLICATION
        )
        
        self.register_shortcut(
            id="app_logs",
            name="View Logs",
            keys=["ctrl", "l"],
            action=self._view_logs,
            description="Open application logs viewer",
            shortcut_type=ShortcutType.APPLICATION
        )
    
    def register_shortcut(self, id: str, name: str, keys: List[str], 
                         action: Callable, description: str,
                         shortcut_type: ShortcutType = ShortcutType.APPLICATION,
                         enabled: bool = True, global_scope: bool = False) -> bool:
        """
        Register a new keyboard shortcut.
        
        Args:
            id: Unique identifier for the shortcut
            name: Display name
            keys: List of key names (e.g., ['ctrl', 'c'])
            action: Function to call when shortcut is triggered
            description: Description of what the shortcut does
            shortcut_type: Category of shortcut
            enabled: Whether shortcut is initially active
            global_scope: Whether shortcut works globally
            
        Returns:
            True if registered successfully
        """
        try:
            shortcut = Shortcut(
                id=id,
                name=name,
                keys=[k.lower() for k in keys],
                action=action,
                description=description,
                shortcut_type=shortcut_type,
                enabled=enabled,
                global_scope=global_scope
            )
            
            with self._lock:
                if global_scope:
                    self._global_shortcuts[id] = shortcut
                else:
                    self._shortcuts[id] = shortcut
            
            logger.debug(f"Registered shortcut: {id} ({'+'.join(keys)})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register shortcut {id}: {e}")
            return False
    
    def unregister_shortcut(self, id: str) -> bool:
        """Remove a shortcut by ID."""
        with self._lock:
            if id in self._shortcuts:
                del self._shortcuts[id]
                logger.debug(f"Unregistered shortcut: {id}")
                return True
            elif id in self._global_shortcuts:
                del self._global_shortcuts[id]
                logger.debug(f"Unregistered global shortcut: {id}")
                return True
            return False
    
    def enable_shortcut(self, id: str) -> bool:
        """Enable a shortcut by ID."""
        with self._lock:
            shortcut = self._shortcuts.get(id) or self._global_shortcuts.get(id)
            if shortcut:
                shortcut.enabled = True
                logger.debug(f"Enabled shortcut: {id}")
                return True
            return False
    
    def disable_shortcut(self, id: str) -> bool:
        """Disable a shortcut by ID."""
        with self._lock:
            shortcut = self._shortcuts.get(id) or self._global_shortcuts.get(id)
            if shortcut:
                shortcut.enabled = False
                logger.debug(f"Disabled shortcut: {id}")
                return True
            return False
    
    def start_listening(self) -> None:
        """Start listening for keyboard shortcuts."""
        if self._is_listening:
            return
        
        self._is_listening = True
        self._listener_thread = threading.Thread(target=self._listen_for_shortcuts, daemon=True)
        self._listener_thread.start()
        logger.info("Shortcut listener started")
    
    def stop_listening(self) -> None:
        """Stop listening for keyboard shortcuts."""
        self._is_listening = False
        if self._listener_thread:
            self._listener_thread.join(timeout=2)
        logger.info("Shortcut listener stopped")
    
    def _listen_for_shortcuts(self) -> None:
        """Main loop for detecting keyboard shortcuts."""
        try:
            # This would use platform-specific keyboard listeners
            # For demonstration, using a simplified approach
            import pynput.keyboard as kb
            
            def on_press(key):
                try:
                    key_name = key.name if hasattr(key, 'name') else str(key.char).lower()
                    with self._lock:
                        self._pressed_keys.add(key_name)
                    self._check_shortcuts()
                except Exception as e:
                    logger.debug(f"Key press processing error: {e}")
            
            def on_release(key):
                try:
                    key_name = key.name if hasattr(key, 'name') else str(key.char).lower()
                    with self._lock:
                        self._pressed_keys.discard(key_name)
                except Exception as e:
                    logger.debug(f"Key release processing error: {e}")
            
            with kb.Listener(on_press=on_press, on_release=on_release) as listener:
                while self._is_listening:
                    time.sleep(0.1)
                    listener.join(0.1)  # Non-blocking join
                    
        except ImportError:
            logger.warning("pynput not available for shortcut listening")
        except Exception as e:
            logger.error(f"Shortcut listener error: {e}")
    
    def _check_shortcuts(self) -> None:
        """Check if current key combination matches any registered shortcut."""
        with self._lock:
            pressed = set(self._pressed_keys)
            
            # Check application shortcuts
            for shortcut in self._shortcuts.values():
                if shortcut.enabled and self._matches_shortcut(shortcut.keys, pressed):
                    try:
                        shortcut.action()
                        logger.debug(f"Executed shortcut: {shortcut.name}")
                    except Exception as e:
                        logger.error(f"Shortcut execution failed: {shortcut.id} - {e}")
            
            # Check global shortcuts
            for shortcut in self._global_shortcuts.values():
                if shortcut.enabled and self._matches_shortcut(shortcut.keys, pressed):
                    try:
                        shortcut.action()
                        logger.debug(f"Executed global shortcut: {shortcut.name}")
                    except Exception as e:
                        logger.error(f"Global shortcut execution failed: {shortcut.id} - {e}")
    
    def _matches_shortcut(self, shortcut_keys: List[str], pressed_keys: set) -> bool:
        """Check if pressed keys match a shortcut combination."""
        # Convert to sets for comparison
        shortcut_set = set(shortcut_keys)
        return shortcut_set.issubset(pressed_keys) and len(shortcut_set) == len(pressed_keys.intersection(shortcut_set))
    
    def _toggle_remote_control(self) -> None:
        """Toggle remote control mode."""
        logger.info("Toggle remote control shortcut activated")
        # This would interface with the RemoteControlManager
    
    def _take_screenshot(self) -> None:
        """Take and share a screenshot."""
        logger.info("Screenshot shortcut activated")
        # Interface with screen sharing module
    
    def _pause_resume_control(self) -> None:
        """Pause or resume remote control session."""
        logger.info("Pause/resume control shortcut activated")
        # Interface with RemoteControlManager
    
    def _lock_keyboard(self) -> None:
        """Lock remote keyboard input."""
        logger.info("Lock keyboard shortcut activated")
        # Interface with KeyboardController
    
    def _show_permissions(self) -> None:
        """Show permission management dialog."""
        logger.info("Show permissions shortcut activated")
        # Interface with permission dialog
    
    def _open_settings(self) -> None:
        """Open application settings."""
        logger.info("Open settings shortcut activated")
        # Interface with settings page
    
    def _view_logs(self) -> None:
        """View application logs."""
        logger.info("View logs shortcut activated")
        # Interface with logs page
    
    def get_shortcuts(self, shortcut_type: Optional[ShortcutType] = None) -> List[Shortcut]:
        """Get list of registered shortcuts."""
        with self._lock:
            all_shortcuts = list(self._shortcuts.values()) + list(self._global_shortcuts.values())
            if shortcut_type:
                return [s for s in all_shortcuts if s.shortcut_type == shortcut_type]
            return all_shortcuts
    
    def get_shortcut_by_id(self, id: str) -> Optional[Shortcut]:
        """Get shortcut by ID."""
        with self._lock:
            return self._shortcuts.get(id) or self._global_shortcuts.get(id)

# Global shortcut manager instance
shortcut_manager = ShortcutManager()

# Convenience functions
def register_shortcut(*args, **kwargs) -> bool:
    """Register a shortcut using the global manager."""
    return shortcut_manager.register_shortcut(*args, **kwargs)

def start_shortcut_listener() -> None:
    """Start the global shortcut listener."""
    shortcut_manager.start_listening()

def stop_shortcut_listener() -> None:
    """Stop the global shortcut listener."""
    shortcut_manager.stop_listening()