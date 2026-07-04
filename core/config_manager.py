"""
===============================================================================
RemoteDesk Pro
File: core/config_manager.py

Thread-safe JSON configuration manager.
===============================================================================
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any

from core.constants import (
    CONFIG_FILE,
    JSON_INDENT,
    JSON_SORT_KEYS,
    SETTINGS_FILE,
    SHORTCUTS_FILE,
    USERS_FILE,
)

_DEFAULTS: dict[Path, dict[str, Any]] = {
    CONFIG_FILE: {
        "theme": "dark",
        "language": "en",
        "first_run": True,
    },
    SETTINGS_FILE: {
        "window": {"width": 1400, "height": 850, "maximized": False},
        "remember_window": True,
    },
    USERS_FILE: {"recent": []},
    SHORTCUTS_FILE: {},
}


class ConfigManager:
    """Loads, validates and persists JSON configuration files."""

    def __init__(self) -> None:
        self._lock = RLock()

    def _ensure(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            self.save(path, deepcopy(_DEFAULTS.get(path, {})))

    def load(self, path: Path) -> dict[str, Any]:
        with self._lock:
            self._ensure(path)
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError
                return data
            except Exception:
                data = deepcopy(_DEFAULTS.get(path, {}))
                self.save(path, data)
                return data

    def save(self, path: Path, data: dict[str, Any]) -> None:
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    indent=JSON_INDENT,
                    sort_keys=JSON_SORT_KEYS,
                    ensure_ascii=False,
                )

    def get(self, path: Path, key: str, default: Any = None) -> Any:
        return self.load(path).get(key, default)

    def set(self, path: Path, key: str, value: Any) -> None:
        data = self.load(path)
        data[key] = value
        self.save(path, data)

    @property
    def config(self) -> dict[str, Any]:
        return self.load(CONFIG_FILE)

    @property
    def settings(self) -> dict[str, Any]:
        return self.load(SETTINGS_FILE)

    @property
    def users(self) -> dict[str, Any]:
        return self.load(USERS_FILE)

    @property
    def shortcuts(self) -> dict[str, Any]:
        return self.load(SHORTCUTS_FILE)
