"""
RemoteDesk Pro - Application Logger (Phase 2)

Comprehensive logging system with file and console logging.
Supports multiple log levels and maintains in-memory buffer for GUI.

Author: Akash Pramanik
Version: 1.0.0
"""

from __future__ import annotations

import logging
import logging.handlers
from typing import Callable, List, Optional
from pathlib import Path

from core.constants import (
    LOG_FILE,
    LOGS_DIR,
    LOG_FORMAT,
    LOG_FORMAT_CONSOLE,
    LOG_DATE_FORMAT,
    LOG_LEVEL,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
    LOG_BUFFER_SIZE,
)


class LogBuffer:
    """
    In-memory circular buffer for storing recent log messages.
    Used by GUI to display logs without reading from disk.
    """

    def __init__(self, max_size: int = LOG_BUFFER_SIZE) -> None:
        """
        Initialize the log buffer.

        Args:
            max_size: Maximum number of log entries to keep in memory
        """
        self.max_size: int = max_size
        self.buffer: List[str] = []

    def add(self, message: str) -> None:
        """
        Add a message to the buffer, removing oldest if full.

        Args:
            message: Formatted log message to add
        """
        self.buffer.append(message)
        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_all(self) -> List[str]:
        """
        Get all messages from buffer.

        Returns:
            List of all log messages
        """
        return self.buffer.copy()

    def clear(self) -> None:
        """Clear all messages from buffer."""
        self.buffer.clear()


class BufferHandler(logging.Handler):
    """
    Custom logging handler that stores logs in an in-memory buffer.
    """

    def __init__(self, buffer: LogBuffer) -> None:
        """
        Initialize the buffer handler.

        Args:
            buffer: LogBuffer instance to store logs in
        """
        super().__init__()
        self.buffer = buffer

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the buffer.

        Args:
            record: LogRecord to emit
        """
        try:
            msg = self.format(record)
            self.buffer.add(msg)
        except Exception:
            self.handleError(record)


class Logger:
    """
    Singleton logger for the entire application.
    
    Manages:
    - File logging with rotation
    - Console logging
    - In-memory buffer for GUI
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Callbacks for real-time log monitoring
    
    Usage:
        logger = Logger()
        logger.info("Application started")
        logger.error("Something went wrong", exc_info=True)
    """

    _instance: Optional[Logger] = None

    def __new__(cls) -> Logger:
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger (only once due to singleton pattern)."""
        if self._initialized:
            return

        self._initialized = True
        self.log_buffer = LogBuffer(max_size=LOG_BUFFER_SIZE)
        self.callbacks: List[Callable[[str, str], None]] = []

        # Create logger instance
        self._logger = logging.getLogger("RemoteDesk-Pro")
        self._logger.setLevel(LOG_LEVEL)

        # Clear existing handlers
        self._logger.handlers.clear()

        # Ensure log directory exists
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # Set up file logging with rotation
        self._setup_file_logging()

        # Set up console logging
        self._setup_console_logging()

        # Set up buffer logging for GUI
        self._setup_buffer_logging()

        # Log startup message
        self._logger.info("=" * 70)
        self._logger.info(f"RemoteDesk Pro Logger Initialized")
        self._logger.info("=" * 70)

    def _setup_file_logging(self) -> None:
        """
        Set up file logging with automatic rotation.
        
        Creates rotating file handler that:
        - Writes to logs/remotedesk.log
        - Rotates when file reaches LOG_MAX_BYTES
        - Keeps LOG_BACKUP_COUNT backup files
        """
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(LOG_LEVEL)

        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def _setup_console_logging(self) -> None:
        """
        Set up console logging.
        
        Outputs to stderr with simplified format.
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt=LOG_FORMAT_CONSOLE,
            datefmt=LOG_DATE_FORMAT,
        )
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def _setup_buffer_logging(self) -> None:
        """
        Set up in-memory buffer logging for GUI.
        
        Stores recent logs in memory for display in Logs page.
        """
        buffer_handler = BufferHandler(self.log_buffer)
        buffer_handler.setLevel(LOG_LEVEL)

        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
        )
        buffer_handler.setFormatter(formatter)
        self._logger.addHandler(buffer_handler)

    def debug(self, message: str, *args: any, **kwargs: any) -> None:
        """
        Log a debug message.

        Args:
            message: Log message
            *args: Arguments for string formatting
            **kwargs: Additional keyword arguments (exc_info, etc.)
        """
        self._logger.debug(message, *args, **kwargs)
        self._trigger_callbacks(message, "DEBUG")

    def info(self, message: str, *args: any, **kwargs: any) -> None:
        """
        Log an info message.

        Args:
            message: Log message
            *args: Arguments for string formatting
            **kwargs: Additional keyword arguments (exc_info, etc.)
        """
        self._logger.info(message, *args, **kwargs)
        self._trigger_callbacks(message, "INFO")

    def warning(self, message: str, *args: any, **kwargs: any) -> None:
        """
        Log a warning message.

        Args:
            message: Log message
            *args: Arguments for string formatting
            **kwargs: Additional keyword arguments (exc_info, etc.)
        """
        self._logger.warning(message, *args, **kwargs)
        self._trigger_callbacks(message, "WARNING")

    def error(self, message: str, *args: any, **kwargs: any) -> None:
        """
        Log an error message.

        Args:
            message: Log message
            *args: Arguments for string formatting
            **kwargs: Additional keyword arguments (exc_info, etc.)
        """
        self._logger.error(message, *args, **kwargs)
        self._trigger_callbacks(message, "ERROR")

    def critical(self, message: str, *args: any, **kwargs: any) -> None:
        """
        Log a critical message.

        Args:
            message: Log message
            *args: Arguments for string formatting
            **kwargs: Additional keyword arguments (exc_info, etc.)
        """
        self._logger.critical(message, *args, **kwargs)
        self._trigger_callbacks(message, "CRITICAL")

    def _trigger_callbacks(self, message: str, level: str) -> None:
        """
        Trigger all registered callbacks with log info.

        Args:
            message: Log message
            level: Log level
        """
        for callback in self.callbacks:
            try:
                callback(message, level)
            except Exception as e:
                self._logger.error(f"Error in log callback: {e}")

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback to be called on every log event.

        Callbacks are called with (message, level) arguments.
        Useful for GUI components that need to react to logs.

        Args:
            callback: Callable that takes (message: str, level: str)
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[str, str], None]) -> None:
        """
        Unregister a previously registered callback.

        Args:
            callback: Callable to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def get_recent_logs(self, limit: Optional[int] = None) -> List[str]:
        """
        Get recent log entries from buffer.

        Args:
            limit: Maximum number of logs to return (None = all)

        Returns:
            List of log entries
        """
        logs = self.log_buffer.get_all()
        if limit is not None:
            return logs[-limit:]
        return logs

    def clear_buffer(self) -> None:
        """Clear the in-memory log buffer."""
        self.log_buffer.clear()

    def get_log_file_path(self) -> Path:
        """
        Get the path to the main log file.

        Returns:
            Path to remotedesk.log
        """
        return LOG_FILE

    def get_log_directory(self) -> Path:
        """
        Get the path to the logs directory.

        Returns:
            Path to logs directory
        """
        return LOGS_DIR


# Create singleton instance
_logger_instance: Logger = Logger()


def get_logger() -> Logger:
    """
    Get the singleton logger instance.

    Returns:
        Logger instance
    """
    return _logger_instance


# Convenience module-level logger alias for legacy imports
logger = _logger_instance
