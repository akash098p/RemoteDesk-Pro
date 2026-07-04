"""
===============================================================================
RemoteDesk Pro
File: core/utils.py

Shared utility helpers used throughout the application.
===============================================================================
"""
from __future__ import annotations

import platform
import secrets
import shutil
import string
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable


def ensure_directory(path: Path) -> Path:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_directories(paths: Iterable[Path]) -> None:
    """Create multiple directories."""
    for path in paths:
        ensure_directory(path)


def timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current timestamp."""
    return datetime.now().strftime(fmt)


def generate_session_id() -> str:
    """Generate a unique session identifier."""
    return uuid.uuid4().hex


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def bytes_to_human(size: int) -> str:
    """Convert bytes into a human-readable string."""
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def get_disk_free(path: Path | str = ".") -> int:
    """Return free disk space in bytes."""
    return shutil.disk_usage(path).free


def get_disk_total(path: Path | str = ".") -> int:
    """Return total disk space in bytes."""
    return shutil.disk_usage(path).total


def get_platform() -> str:
    """Return the current operating system."""
    return platform.system()


def get_platform_version() -> str:
    """Return the operating system version."""
    return platform.version()


def get_machine() -> str:
    """Return machine architecture."""
    return platform.machine()


def safe_filename(name: str) -> str:
    """Sanitize a filename for cross-platform use."""
    invalid = '<>:"/\\\\|?*'
    cleaned = "".join("_" if c in invalid else c for c in name)
    return cleaned.strip().rstrip(".")


def is_json_file(path: Path | str) -> bool:
    """Check if the given path has a JSON extension."""
    return Path(path).suffix.lower() == ".json"
