"""
===============================================================================
RemoteDesk Pro
File: core/theme_manager.py

Runtime theme manager for RemoteDesk Pro.
===============================================================================
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.config_manager import ConfigManager
from core.constants import (
    CONFIG_FILE,
    DEFAULT_THEME,
    GUI_THEMES_DIR,
    SUPPORTED_THEMES,
)


class ThemeManager:
    """Loads theme JSON files and manages runtime theme switching."""

    def __init__(self) -> None:
        self._config = ConfigManager()
        self._theme_name = self._config.get(
            self._config.__class__.__dict__.get("__dummy__", Path()),  # unused
            "theme",
            DEFAULT_THEME,
        )
        # Read directly from config.json
        cfg = self._config.config
        self._theme_name = cfg.get("theme", DEFAULT_THEME)
        self._theme: dict[str, Any] = {}
        self._listeners: list[Any] = []
        self.load_theme(self._theme_name)

    @property
    def current_theme(self) -> str:
        return self._theme_name

    @property
    def colors(self) -> dict[str, Any]:
        return self._theme

    def register(self, widget: Any) -> None:
        """Register an object implementing apply_theme(theme_dict)."""
        if widget not in self._listeners:
            self._listeners.append(widget)

    def unregister(self, widget: Any) -> None:
        if widget in self._listeners:
            self._listeners.remove(widget)

    def load_theme(self, name: str) -> dict[str, Any]:
        """Load a theme by name."""
        if name not in SUPPORTED_THEMES:
            name = DEFAULT_THEME

        theme_file = GUI_THEMES_DIR / f"{name}.json"
        if not theme_file.exists():
            raise FileNotFoundError(theme_file)

        with theme_file.open("r", encoding="utf-8") as fp:
            self._theme = json.load(fp)

        self._theme_name = name
        cfg = self._config.config
        cfg["theme"] = name
        self._config.save(Path(self._config.CONFIG_FILE) if hasattr(self._config,"CONFIG_FILE") else CONFIG_FILE, cfg)
        self._notify()
        return self._theme

    def color(self, key: str, default: Any = None) -> Any:
        return self._theme.get(key, default)

    def _notify(self) -> None:
        dead = []
        for listener in self._listeners:
            try:
                listener.apply_theme(self._theme)
            except Exception:
                dead.append(listener)
        for listener in dead:
            self.unregister(listener)
