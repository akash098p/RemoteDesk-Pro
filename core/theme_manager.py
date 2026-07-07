"""
===============================================================================
RemoteDesk Pro
File: core/theme_manager.py

Manages application themes, loading definitions from JSON files and applying
them to CustomTkinter widgets.
===============================================================================
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

import customtkinter

from core.constants import (
    DEFAULT_THEME,
    THEMES_DIR,
    FONTS_DIR,
    FONT_REGULAR,
    FONT_MEDIUM,
    FONT_BOLD,
    FONT_SEMIBOLD,
    FONT_LIGHT,
    FONT_DISPLAY_REGULAR,
    FONT_DISPLAY_BOLD,
)
from core.config_manager import get_config_manager
from core.logger import get_logger

logger = get_logger()
config_manager = get_config_manager()

class ThemeManager:
    """
    Singleton manager for handling application themes.

    Loads theme definitions from JSON files, applies them to CustomTkinter,
    and provides methods to access theme-specific colors and fonts.
    Supports dynamic theme switching and fallback to default themes.
    """

    _instance: Optional[ThemeManager] = None
    _initialized: bool = False

    def __new__(cls) -> ThemeManager:
        """Ensures a single instance of ThemeManager is used."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the ThemeManager.
        This constructor is called only once due to the singleton pattern.
        """
        if self._initialized:
            return

        self._available_themes: Dict[str, Path] = {}
        self._current_theme_name: str = ""
        self._current_theme_data: Dict[str, Any] = {}
        self._font_cache: Dict[Tuple[str, int, str], customtkinter.CTkFont] = {}
        self._theme_change_callbacks: List[Callable[[str], None]] = []

        self._load_available_themes()
        self._load_custom_fonts()

        # Get initial theme from config, or use default
        initial_theme = config_manager.get_value("config", "theme", DEFAULT_THEME)
        self.set_theme(initial_theme, initial_load=True)

        self._initialized = True
        logger.info(f"ThemeManager initialized with theme: {self.current_theme_name}")

    def _load_available_themes(self) -> None:
        """
        Scans the THEMES_DIR for JSON theme files and populates _available_themes.
        """
        THEMES_DIR.mkdir(parents=True, exist_ok=True)
        for theme_file in THEMES_DIR.glob("*.json"):
            theme_name = theme_file.stem  # Get filename without extension
            self._available_themes[theme_name] = theme_file
            logger.debug(f"Found theme file: {theme_name} at {theme_file}")

        if not self._available_themes:
            logger.warning(f"No theme files found in {THEMES_DIR}. Defaulting to hardcoded colors.")
            # Provide a fallback if no JSON files are found
            self._available_themes["dark"] = Path("__hardcoded_dark_theme__")
            self._available_themes["light"] = Path("__hardcoded_light_theme__")
            
        # Ensure default theme is always available even if not in file system
        if DEFAULT_THEME not in self._available_themes:
            logger.warning(f"Default theme '{DEFAULT_THEME}' not found as a file. Will use hardcoded defaults if necessary.")


    def _load_theme_data(self, theme_name: str) -> Dict[str, Any]:
        """
        Loads the JSON data for a specific theme.
        If file not found or corrupted, returns default hardcoded colors.
        """
        theme_file_path = self._available_themes.get(theme_name)
        if theme_file_path and theme_file_path.exists():
            try:
                with theme_file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Theme file {theme_name}.json content is not a dictionary.")
                logger.debug(f"Loaded theme data from {theme_file_path}")
                return data
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing theme file {theme_file_path}: {e}. Using hardcoded defaults.")
            except IOError as e:
                logger.error(f"IOError reading theme file {theme_file_path}: {e}. Using hardcoded defaults.")
            except Exception as e:
                logger.critical(f"Unexpected error loading theme file {theme_file_path}: {e}", exc_info=True)
        
        # Fallback to hardcoded defaults from constants
        logger.warning(f"Using hardcoded default colors for theme '{theme_name}'.")
        from core.constants import DARK_THEME_COLORS, LIGHT_THEME_COLORS # Deferred import to avoid circular dependency
        if theme_name == "dark":
            return DARK_THEME_COLORS
        elif theme_name == "light":
            return LIGHT_THEME_COLORS
        else:
            # Fallback for unknown themes to dark theme defaults
            return DARK_THEME_COLORS

    def _load_custom_fonts(self) -> None:
        """
        Loads custom fonts from the assets/fonts directory and registers them with CustomTkinter.
        """
        FONTS_DIR.mkdir(parents=True, exist_ok=True)
        fonts_to_load = [
            FONT_REGULAR,
            FONT_MEDIUM,
            FONT_BOLD,
            FONT_SEMIBOLD,
            FONT_LIGHT,
            FONT_DISPLAY_REGULAR,
            FONT_DISPLAY_BOLD,
        ]
        for font_path in fonts_to_load:
            if font_path.exists():
                try:
                    customtkinter.deactivate_automatic_dpi_awareness() # Prevents font issues on Windows
                    if hasattr(customtkinter, "load_font"):
                        customtkinter.load_font(str(font_path))
                        logger.debug(f"Loaded custom font: {font_path.name}")
                    else:
                        logger.debug(f"CustomTkinter version does not expose load_font; skipping {font_path.name}")
                except Exception as e:
                    logger.error(f"Failed to load font {font_path.name}: {e}")
            else:
                logger.warning(f"Custom font file not found: {font_path.name}")

    def set_theme(self, theme_name: str, initial_load: bool = False) -> None:
        """
        Sets the active application theme.

        Args:
            theme_name: The name of the theme to set (e.g., "dark", "light").
            initial_load: If True, this is the initial theme load, skips saving to config.
        """
        if theme_name not in self._available_themes:
            logger.warning(f"Theme '{theme_name}' not found. Falling back to default '{DEFAULT_THEME}'.")
            theme_name = DEFAULT_THEME
            
        if self._current_theme_name == theme_name and not initial_load:
            logger.debug(f"Theme '{theme_name}' is already active. No change needed.")
            return

        self._current_theme_name = theme_name
        self._current_theme_data = self._load_theme_data(theme_name)
        
        # Apply CustomTkinter theme settings
        # CustomTkinter expects 'colors' dict with specific keys
        ctk_theme = {"CTk": {"colors": self._current_theme_data}}
        try:
            if hasattr(customtkinter, "set_widget_style"):
                customtkinter.set_widget_style(ctk_theme)

            if hasattr(customtkinter, "set_default_color_theme") and theme_name not in {"dark", "light"}:
                try:
                    customtkinter.set_default_color_theme(theme_name)
                except Exception as e:
                    logger.debug(f"Skipping set_default_color_theme for theme '{theme_name}': {e}")

            if hasattr(customtkinter, "set_appearance_mode"):
                customtkinter.set_appearance_mode(theme_name)

            logger.info(f"Successfully applied theme: {theme_name}")
            
            if not initial_load:
                config_manager.set_value("config", "theme", theme_name)

            for callback in self._theme_change_callbacks:
                try:
                    callback(theme_name)
                except Exception as e:
                    logger.error(f"Error in theme change callback: {e}")

        except Exception as e:
            logger.error(f"Failed to apply CustomTkinter theme '{theme_name}': {e}", exc_info=True)

    def get_color(self, key: str, fallback_key: Optional[str] = None) -> str:
        """
        Retrieves a color value from the current theme.

        Args:
            key: The key for the color (e.g., "primary", "background").
            fallback_key: An optional fallback key if the primary key is not found.

        Returns:
            The color hex string. Defaults to a black color if not found.
        """
        color = self._current_theme_data.get(key)
        if color:
            return color
        
        if fallback_key:
            color = self._current_theme_data.get(fallback_key)
            if color:
                return color

        logger.warning(f"Color key '{key}' not found in theme '{self._current_theme_name}'. Using default '#000000'.")
        return "#000000" # Default fallback color

    def get_font(self, font_name: str, size: int, weight: str = "normal") -> customtkinter.CTkFont:
        """
        Retrieves a CustomTkinter font object.

        Args:
            font_name: The name of the font (e.g., "Inter", "InterDisplay").
            size: The font size.
            weight: The font weight ("normal", "bold", "light", etc.).

        Returns:
            A CTkFont object.
        """
        normalized_weight = weight if weight in {"normal", "bold"} else "normal"
        if weight != normalized_weight:
            logger.warning(f"Unsupported font weight '{weight}' for font '{font_name}', falling back to '{normalized_weight}'.")

        font_key = (font_name, size, normalized_weight)
        if font_key not in self._font_cache:
            try:
                # CustomTkinter automatically handles loaded fonts by name
                self._font_cache[font_key] = customtkinter.CTkFont(family=font_name, size=size, weight=normalized_weight)
            except Exception as e:
                logger.error(f"Failed to create font {font_name}, size {size}, weight {normalized_weight}: {e}")
                # Fallback to default CustomTkinter font
                self._font_cache[font_key] = customtkinter.CTkFont(size=size, weight=normalized_weight)
        return self._font_cache[font_key]

    @property
    def available_themes(self) -> List[str]:
        """Returns a list of names of all available themes."""
        return list(self._available_themes.keys())

    @property
    def current_theme_name(self) -> str:
        """Returns the name of the currently active theme."""
        return self._current_theme_name

    def register_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Registers a callback function to be called when the theme changes.
        The callback will receive the new theme name as an argument.
        """
        if callback not in self._theme_change_callbacks:
            self._theme_change_callbacks.append(callback)

    def unregister_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """
        Unregisters a callback function from theme change notifications.
        """
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)

# Create a singleton instance for global access
_theme_manager_instance = ThemeManager()

def get_theme_manager() -> ThemeManager:
    """
    Provides global access to the singleton ThemeManager instance.
    """
    return _theme_manager_instance
