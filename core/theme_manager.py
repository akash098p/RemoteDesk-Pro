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
                return self._normalize_theme_data(data)
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
            return self._normalize_theme_data(DARK_THEME_COLORS)
        elif theme_name == "light":
            return self._normalize_theme_data(LIGHT_THEME_COLORS)
        else:
            # Fallback for unknown themes to dark theme defaults
            return self._normalize_theme_data(DARK_THEME_COLORS)

    def _normalize_theme_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize theme keys so legacy names and generic keys both work."""
        normalized = dict(data)

        def alias(key: str, fallback_keys: list[str]) -> None:
            if key not in normalized:
                for fallback_key in fallback_keys:
                    if fallback_key in normalized:
                        normalized[key] = normalized[fallback_key]
                        break

        alias("text_primary", ["text"])
        alias("text_secondary", ["secondary_text", "text"])
        alias("text_on_primary", ["text_primary", "text"])
        alias("text_on_error", ["text_primary", "text"])
        alias("card_bg", ["card"])
        alias("card_border", ["border"])
        alias("sidebar_button_bg", ["sidebar", "card", "background"])
        alias("sidebar_button_hover_bg", ["surface_hover", "sidebar", "background"])
        alias("sidebar_button_text", ["text_primary", "text"])
        alias("titlebar_bg", ["sidebar", "card", "background"])
        alias("titlebar_text", ["text_primary", "text"])
        alias("titlebar_minimize_bg", ["sidebar", "card", "background"])
        alias("titlebar_maximize_bg", ["sidebar", "card", "background"])
        alias("titlebar_close_bg", ["danger", "primary"])
        alias("titlebar_close_hover", ["danger", "primary"])
        alias("titlebar_control_hover", ["surface_hover", "sidebar"])
        alias("statusbar_bg", ["sidebar", "card", "background"])
        alias("statusbar_text", ["text_primary", "text"])
        alias("statusbar_secondary_text", ["text_secondary", "text_primary", "text"])
        alias("notification_bg", ["card", "sidebar", "background"])
        alias("notification_title", ["text_primary", "text"])
        alias("notification_message", ["text_secondary", "text_primary", "text"])
        alias("notification_badge", ["danger", "warning"])
        alias("notification_close_bg", ["danger", "primary"])
        alias("notification_close_hover", ["danger", "primary"])
        alias("dialog_bg", ["card", "sidebar", "background"])
        alias("dialog_title", ["text_primary", "text"])
        alias("dialog_text", ["text_secondary", "text_primary", "text"])
        alias("primary_hover", ["primary"])
        alias("secondary_hover", ["surface_hover", "sidebar", "background"])
        alias("secondary", ["card", "sidebar", "background"])
        alias("surface", ["card", "sidebar", "background"])
        alias("surface_hover", ["sidebar", "background"])
        alias("background", ["background"])

        return normalized

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

    def _build_customtk_theme(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build a CustomTkinter theme dictionary from our simple theme colors."""
        default_theme: Dict[str, Any] = {}
        if hasattr(customtkinter, "ThemeManager") and hasattr(customtkinter.ThemeManager, "theme"):
            default_theme = dict(customtkinter.ThemeManager.theme)

        primary = theme_data.get("primary", "#0084FF")
        primary_hover = theme_data.get("primary_hover", primary)
        background = theme_data.get("background", "#0D0D0D")
        card_bg = theme_data.get("card_bg", theme_data.get("card", "#252525"))
        surface = theme_data.get("surface", card_bg)
        surface_hover = theme_data.get("surface_hover", theme_data.get("sidebar", "#252525"))
        border = theme_data.get("border", "#333333")
        text_primary = theme_data.get("text_primary", theme_data.get("text", "#FFFFFF"))
        text_secondary = theme_data.get("text_secondary", theme_data.get("secondary_text", "#A0A0A0"))
        text_on_primary = theme_data.get("text_on_primary", text_primary)

        theme: Dict[str, Any] = dict(default_theme)
        theme["CTk"] = {
            **default_theme.get("CTk", {}),
            "fg_color": [background, background],
            "text_color": [text_primary, text_primary],
            "border_color": [border, border],
        }
        theme["CTkFrame"] = {
            **default_theme.get("CTkFrame", {}),
            "fg_color": [surface, surface],
            "border_color": [border, border],
            "border_width": 0,
            "corner_radius": default_theme.get("CTkFrame", {}).get("corner_radius", 10),
        }
        theme["CTkButton"] = {
            **default_theme.get("CTkButton", {}),
            "fg_color": [primary, primary],
            "hover_color": [primary_hover, primary_hover],
            "text_color": [text_on_primary, text_on_primary],
            "border_color": [border, border],
            "border_width": 0,
            "corner_radius": default_theme.get("CTkButton", {}).get("corner_radius", 8),
        }
        theme["CTkLabel"] = {
            **default_theme.get("CTkLabel", {}),
            "fg_color": "transparent",
            "text_color": [text_primary, text_primary],
            "border_color": [border, border],
            "border_width": default_theme.get("CTkLabel", {}).get("border_width", 0),
            "corner_radius": default_theme.get("CTkLabel", {}).get("corner_radius", 0),
        }
        theme["CTkEntry"] = {
            **default_theme.get("CTkEntry", {}),
            "fg_color": [surface, surface],
            "border_color": [border, border],
            "text_color": [text_primary, text_primary],
            "placeholder_text_color": [text_secondary, text_secondary],
            "border_width": default_theme.get("CTkEntry", {}).get("border_width", 1),
        }
        theme["CTkTextbox"] = {
            **default_theme.get("CTkTextbox", {}),
            "fg_color": [surface, surface],
            "border_color": [border, border],
            "text_color": [text_primary, text_primary],
            "border_width": default_theme.get("CTkTextbox", {}).get("border_width", 1),
        }
        theme["CTkOptionMenu"] = {
            **default_theme.get("CTkOptionMenu", {}),
            "fg_color": [surface, surface],
            "hover_color": [surface_hover, surface_hover],
            "text_color": [text_primary, text_primary],
            "border_color": [border, border],
            "border_width": default_theme.get("CTkOptionMenu", {}).get("border_width", 1),
        }
        theme["CTkSlider"] = {
            **default_theme.get("CTkSlider", {}),
            "button_color": [primary, primary],
            "progress_color": [primary, primary],
            "button_hover_color": [primary_hover, primary_hover],
        }

        return theme

    def _write_customtk_theme_file(self, theme_name: str, theme_data: Dict[str, Any]) -> Optional[Path]:
        """Write the generated CustomTkinter theme JSON to a file and return its path.
        
        Note: This method now uses an in-memory cache to avoid creating physical .ctk.json files.
        """
        # Create cache directory for temporary theme files
        cache_dir = THEMES_DIR / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        theme_file = cache_dir / f"{theme_name}.ctk.json"
        try:
            with theme_file.open("w", encoding="utf-8") as f:
                json.dump(theme_data, f, indent=2)
            logger.debug(f"Wrote temporary CustomTkinter theme file: {theme_file}")
        except Exception as e:
            logger.error(f"Failed to write CustomTkinter theme file {theme_file}: {e}")
            return None
        return theme_file

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
        appearance_mode = "light" if theme_name == "light" else "dark"
        try:
            if hasattr(customtkinter, "set_default_color_theme"):
                if theme_name in {"dark", "light"}:
                    try:
                        customtkinter.set_default_color_theme(theme_name)
                    except Exception as e:
                        logger.debug(f"Skipping default CTk theme for '{theme_name}': {e}")
                else:
                    ctk_theme_data = self._build_customtk_theme(self._current_theme_data)
                    try:
                        # Apply theme directly without writing to main themes directory
                        customtkinter.ThemeManager.theme = ctk_theme_data
                    except Exception as e:
                        logger.debug(f"Failed to apply custom theme in memory: {e}")
                        # Only write to cache directory as fallback
                        theme_file = self._write_customtk_theme_file(theme_name, ctk_theme_data)
                        if theme_file:
                            customtkinter.set_default_color_theme(str(theme_file))

            if hasattr(customtkinter, "set_appearance_mode"):
                customtkinter.set_appearance_mode(appearance_mode)

            logger.info(f"Successfully applied theme: {theme_name} (appearance mode: {appearance_mode})")
            
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
