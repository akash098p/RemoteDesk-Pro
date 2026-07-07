
import threading
import time
from typing import Callable, Optional

from core.logger import Logger

# Try to import pyperclip, if not available, provide a mock or raise an error
try:
    import pyperclip
except ImportError:
    Logger.get_logger().warning("pyperclip not found. ClipboardWatcher will not function. Please install with 'pip install pyperclip'.")
    pyperclip = None

class ClipboardWatcher:
    """
    Monitors the local clipboard for changes and notifies a callback function.
    This is a platform-specific component.
    """
    def __init__(self, on_clipboard_change: Callable[[str], None], interval: float = 1.0):
        self.logger = Logger.get_logger()
        self.on_clipboard_change = on_clipboard_change
        self.interval = interval  # How often to check the clipboard in seconds
        self._stop_event = threading.Event()
        self._watcher_thread: Optional[threading.Thread] = None
        self.last_clipboard_content: Optional[str] = None

        if pyperclip is None:
            self.logger.error("ClipboardWatcher cannot be initialized without pyperclip. Please install it.")
            raise RuntimeError("pyperclip library is required for ClipboardWatcher.")

        self.logger.info("ClipboardWatcher initialized.")

    def start(self):
        """
        Starts the clipboard monitoring in a separate daemon thread.
        """
        if self._watcher_thread and self._watcher_thread.is_alive():
            self.logger.warning("Clipboard watcher already running.")
            return

        self._stop_event.clear()
        self.last_clipboard_content = pyperclip.paste() # Initialize with current content
        self._watcher_thread = threading.Thread(target=self._watch_clipboard_loop, daemon=True)
        self._watcher_thread.start()
        self.logger.info("ClipboardWatcher started.")

    def _watch_clipboard_loop(self):
        """
        The main loop for monitoring the clipboard. Runs in a separate thread.
        """
        self.logger.debug("Clipboard watcher loop started.")
        while not self._stop_event.is_set():
            try:
                current_content = pyperclip.paste()
                if current_content != self.last_clipboard_content:
                    self.logger.debug(f"Clipboard changed: {current_content[:50]}...")
                    self.last_clipboard_content = current_content
                    self.on_clipboard_change(current_content)
            except pyperclip.PyperclipException as e:
                self.logger.error(f"Error accessing clipboard: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error in clipboard watcher loop: {e}")

            time.sleep(self.interval)
        self.logger.info("Clipboard watcher loop stopped.")

    def stop(self):
        """
        Stops the clipboard monitoring thread.
        """
        if self._watcher_thread and self._watcher_thread.is_alive():
            self.logger.info("Stopping ClipboardWatcher...")
            self._stop_event.set()
            self._watcher_thread.join(timeout=self.interval * 2 + 1)
            if self._watcher_thread.is_alive():
                self.logger.warning("Clipboard watcher thread did not terminate gracefully.")
        self.logger.info("ClipboardWatcher stopped.")

    def update_clipboard(self, content: str):
        """
        Updates the local clipboard content and updates `last_clipboard_content`
        to prevent self-triggered change notifications.
        """
        try:
            pyperclip.copy(content)
            self.last_clipboard_content = content # Update to prevent re-triggering
            self.logger.debug(f"Local clipboard updated: {content[:50]}...")
        except pyperclip.PyperclipException as e:
            self.logger.error(f"Error setting clipboard content: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error updating clipboard: {e}")
