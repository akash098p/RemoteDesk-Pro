"""
===============================================================================
RemoteDesk Pro
File: core/config_manager.py

Thread-safe JSON configuration manager with singleton pattern.
Handles loading, saving, validation, and default fallbacks for application
configuration files.
===============================================================================
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

from core.constants import (
    CONFIG_FILE,
    SETTINGS_FILE,
    SHORTCUTS_FILE,
    USERS_FILE,
    JSON_INDENT,
    JSON_SORT_KEYS,
    DEFAULT_THEME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from core.logger import get_logger

# Initialize logger
logger = get_logger()

# Default configuration values for each file
_DEFAULTS: Dict[Path, Dict[str, Any]] = {
    CONFIG_FILE: {
        "theme": DEFAULT_THEME,
        "language": "en",
        "first_run": True,
        "app_id": "", # Will be generated on first run if empty
    },
    SETTINGS_FILE: {
        "window": {"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT, "maximized": False},
        "remember_window_size": True,
        "remember_window_position": True,
        "download_folder": str(Path.home() / "Downloads"),
        "notifications_enabled": True,
        "auto_start": False,
        "fps_limit": 30,
        "quality": 75,
        "audio_enabled": False,
    },
    USERS_FILE: {
        "recent_connections": [],
        "trusted_devices": {},
    },
    SHORTCUTS_FILE: {
        # Shortcuts are defined in constants.py and will be loaded from there
        # and potentially overridden here if user customizes them.
    },
}

class ConfigManager:
    """
    Singleton configuration manager for RemoteDesk Pro.

    Manages loading, saving, and providing access to JSON configuration files
    (config.json, settings.json, users.json, shortcuts.json).
    Ensures thread-safe access, provides default fallbacks, and logs errors.
    """

    _instance: Optional[ConfigManager] = None
    _initialized: bool = False

    def __new__(cls) -> ConfigManager:
        """Ensures a single instance of ConfigManager is used."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the ConfigManager.
        This constructor is called only once due to the singleton pattern.
        """
        if self._initialized:
            return

        self._lock = RLock()
        self._cache: Dict[Path, Dict[str, Any]] = {}
        self._config_files = {
            "config": CONFIG_FILE,
            "settings": SETTINGS_FILE,
            "users": USERS_FILE,
            "shortcuts": SHORTCUTS_FILE,
        }
        self._load_all_configs_on_startup()
        self._initialized = True
        logger.info("ConfigManager initialized.")

    def _load_all_configs_on_startup(self) -> None:
        """Loads all known configuration files during initialization."""
        for name, path in self._config_files.items():
            self._cache[path] = self._load_file(path)

    def _ensure_file_exists_with_defaults(self, path: Path) -> None:
        """
        Ensures a config file exists. If not, creates it with default content.
        """
        with self._lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                default_data = deepcopy(_DEFAULTS.get(path, {}))
                try:
                    with path.open("w", encoding="utf-8") as f:
                        json.dump(
                            default_data,
                            f,
                            indent=JSON_INDENT,
                            sort_keys=JSON_SORT_KEYS,
                            ensure_ascii=False,
                        )
                    logger.info(f"Created default config file: {path}")
                except IOError as e:
                    logger.error(f"Failed to create default config file {path}: {e}")

    def _load_file(self, path: Path) -> Dict[str, Any]:
        """
        Loads a single JSON configuration file.
        Returns default values if the file is missing or corrupted.
        """
        self._ensure_file_exists_with_defaults(path)
        with self._lock:
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Config file {path} content is not a dictionary.")
                logger.debug(f"Loaded config from {path}")
                return data
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error loading config file {path}: {e}. Reverting to defaults.")
                default_data = deepcopy(_DEFAULTS.get(path, {}))
                self._save_file(path, default_data) # Overwrite corrupted file with defaults
                return default_data
            except IOError as e:
                logger.error(f"IOError reading config file {path}: {e}. Using defaults.")
                return deepcopy(_DEFAULTS.get(path, {}))
            except Exception as e:
                logger.critical(f"Unexpected error loading config file {path}: {e}. Using defaults.", exc_info=True)
                return deepcopy(_DEFAULTS.get(path, {}))

    def _save_file(self, path: Path, data: Dict[str, Any]) -> None:
        """
        Saves a dictionary to a JSON configuration file.
        """
        with self._lock:
            try:
                path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent dir exists
                with path.open("w", encoding="utf-8") as f:
                    json.dump(
                        data,
                        f,
                        indent=JSON_INDENT,
                        sort_keys=JSON_SORT_KEYS,
                        ensure_ascii=False,
                    )
                self._cache[path] = deepcopy(data) # Update cache on successful save
                logger.debug(f"Saved config to {path}")
            except IOError as e:
                logger.error(f"Failed to save config to {path}: {e}")
            except Exception as e:
                logger.critical(f"Unexpected error saving config to {path}: {e}", exc_info=True)

    def get_config(self, file_key: str) -> Dict[str, Any]:
        """
        Retrieves the configuration dictionary for a given file key.
        The data is loaded from cache if available, otherwise from disk.

        Args:
            file_key: Key identifying the configuration file (e.g., "config", "settings").

        Returns:
            A deep copy of the configuration dictionary for the specified file.
            Returns an empty dict if the file_key is invalid.
        """
        path = self._config_files.get(file_key)
        if not path:
            logger.error(f"Attempted to get unknown config file key: {file_key}")
            return {}
        
        with self._lock:
            if path not in self._cache:
                self._cache[path] = self._load_file(path)
            return deepcopy(self._cache[path])

    def set_config(self, file_key: str, data: Dict[str, Any]) -> None:
        """
        Sets the entire configuration dictionary for a given file key and saves it.

        Args:
            file_key: Key identifying the configuration file.
            data: The new dictionary to save.
        """
        path = self._config_files.get(file_key)
        if not path:
            logger.error(f"Attempted to set unknown config file key: {file_key}")
            return
        
        if not isinstance(data, dict):
            logger.error(f"Attempted to save non-dictionary data to config file {file_key}.")
            return

        with self._lock:
            self._save_file(path, data)

    def get_value(self, file_key: str, key: str, default: Any = None) -> Any:
        """
        Retrieves a specific value from a configuration file.

        Args:
            file_key: Key identifying the configuration file.
            key: The key of the value to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value if not found.
        """
        config_data = self.get_config(file_key)
        return config_data.get(key, default)

    def set_value(self, file_key: str, key: str, value: Any) -> None:
        """
        Sets a specific value in a configuration file and saves the file.

        Args:
            file_key: Key identifying the configuration file.
            key: The key of the value to set.
            value: The new value to set.
        """
        with self._lock:
            config_data = self.get_config(file_key)
            if config_data:
                config_data[key] = value
                self._save_file(self._config_files[file_key], config_data)

    # Properties for easy access to specific config files
    @property
    def app_config(self) -> Dict[str, Any]:
        """Returns the main application configuration."""
        return self.get_config("config")

    @property
    def app_settings(self) -> Dict[str, Any]:
        """Returns the user settings configuration."""
        return self.get_config("settings")

    @property
    def user_data(self) -> Dict[str, Any]:
        """Returns the user data configuration."""
        return self.get_config("users")

    @property
    def app_shortcuts(self) -> Dict[str, Any]:
        """Returns the keyboard shortcuts configuration."""
        return self.get_config("shortcuts")

# Create a singleton instance for global access
_config_manager_instance = ConfigManager()

def get_config_manager() -> ConfigManager:
    """
    Provides global access to the singleton ConfigManager instance.
    """
    return _config_manager_instance
