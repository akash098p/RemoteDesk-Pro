"""
===============================================================================
RemoteDesk Pro
File: core/logger.py

Central logging utility for the application.
===============================================================================
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.constants import (
    APPLICATION_LOG_FILE,
    BACKUP_LOG_COUNT,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
    LOG_LEVEL,
    LOGS_DIR,
    MAX_LOG_FILE_SIZE,
    REQUIRED_DIRECTORIES,
)


class Logger:
    """Application-wide logger factory."""

    _configured = False

    @classmethod
    def configure(cls) -> None:
        """Configure the root logger once."""
        if cls._configured:
            return

        for directory in REQUIRED_DIRECTORIES:
            Path(directory).mkdir(parents=True, exist_ok=True)

        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        root = logging.getLogger()
        root.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
        )

        file_handler = RotatingFileHandler(
            APPLICATION_LOG_FILE,
            maxBytes=MAX_LOG_FILE_SIZE,
            backupCount=BACKUP_LOG_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        root.handlers.clear()
        root.addHandler(file_handler)
        root.addHandler(console_handler)

        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Return a configured logger."""
        cls.configure()
        return logging.getLogger(name)
