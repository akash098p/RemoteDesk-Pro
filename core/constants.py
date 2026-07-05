"""
RemoteDesk Pro - Application Constants (Phase 2)

This module defines all hardcoded constants used throughout the application.
Including paths, dimensions, colors, versions, and default values.

Author: Akash Pramanik
Version: 1.0.0
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Tuple

# ============================================================================
# APPLICATION INFORMATION
# ============================================================================

APP_NAME: str = "RemoteDesk Pro"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Akash Pramanik"
APP_DESCRIPTION: str = "A Modern Cross-Platform Remote Collaboration Platform"
APP_COPYRIGHT: str = "© 2024 Akash Pramanik. All rights reserved."
APP_GITHUB: str = "https://github.com/akash098p/RemoteDesk-Pro"
APP_LICENSE: str = "MIT"

# ============================================================================
# WINDOW SETTINGS
# ============================================================================

WINDOW_WIDTH: int = 1200
WINDOW_HEIGHT: int = 800
WINDOW_MIN_WIDTH: int = 800
WINDOW_MIN_HEIGHT: int = 600
WINDOW_RESIZABLE: bool = True

# Default window position (None = center screen)
WINDOW_DEFAULT_X: int | None = None
WINDOW_DEFAULT_Y: int | None = None

# ============================================================================
# SIDEBAR SETTINGS
# ============================================================================

SIDEBAR_WIDTH: int = 240
SIDEBAR_COLLAPSED_WIDTH: int = 60
SIDEBAR_ANIMATION_SPEED: int = 200  # milliseconds

# ============================================================================
# COMPONENT SIZES
# ============================================================================

CORNER_RADIUS: int = 8
PADDING: int = 12
BUTTON_HEIGHT: int = 40
BUTTON_WIDTH: int = 120
ICON_SIZE: int = 24
FONT_SIZE_BODY: int = 14
FONT_SIZE_LABEL: int = 12
FONT_SIZE_HEADER: int = 18
FONT_SIZE_SUBHEADER: int = 16
FONT_SIZE_LIGHT: int = 13

# ============================================================================
# FILE PATHS
# ============================================================================

# Get the project root directory
PROJECT_ROOT: Path = Path(__file__).parent.parent

# Configuration paths
CONFIG_DIR: Path = PROJECT_ROOT / "config"
CONFIG_FILE: Path = CONFIG_DIR / "config.json"
SETTINGS_FILE: Path = CONFIG_DIR / "settings.json"
SHORTCUTS_FILE: Path = CONFIG_DIR / "shortcuts.json"
USERS_FILE: Path = CONFIG_DIR / "users.json"

# Assets paths
ASSETS_DIR: Path = PROJECT_ROOT / "assets"
FONTS_DIR: Path = ASSETS_DIR / "fonts"
ICONS_DIR: Path = ASSETS_DIR / "icons"
IMAGES_DIR: Path = ASSETS_DIR / "images"
SOUNDS_DIR: Path = ASSETS_DIR / "sounds"
THEMES_DIR: Path = PROJECT_ROOT / "gui" / "themes"

# Logs paths
LOGS_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE: Path = LOGS_DIR / "remotedesk.log"

# Cache and temp paths
CACHE_DIR: Path = PROJECT_ROOT / "cache"
TEMP_DIR: Path = PROJECT_ROOT / "temp"
DOWNLOADS_DIR: Path = PROJECT_ROOT / "downloads"

# ============================================================================
# FONT PATHS
# ============================================================================

FONT_REGULAR: Path = FONTS_DIR / "Inter-Regular.ttf"
FONT_MEDIUM: Path = FONTS_DIR / "Inter-Medium.ttf"
FONT_BOLD: Path = FONTS_DIR / "Inter-Bold.ttf"
FONT_SEMIBOLD: Path = FONTS_DIR / "Inter-SemiBold.ttf"
FONT_LIGHT: Path = FONTS_DIR / "Inter-Light.ttf"

FONT_DISPLAY_REGULAR: Path = FONTS_DIR / "InterDisplay-Regular.ttf"
FONT_DISPLAY_BOLD: Path = FONTS_DIR / "InterDisplay-Bold.ttf"

# ============================================================================
# DEFAULT THEME COLORS
# ============================================================================

DEFAULT_THEME: str = "dark"

DARK_THEME_COLORS: Dict[str, str] = {
    "primary": "#0084FF",
    "secondary": "#1E1E1E",
    "background": "#0D0D0D",
    "surface": "#1A1A1A",
    "surface_hover": "#252525",
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A0A0",
    "accent": "#FF6B35",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336",
    "border": "#333333",
}

LIGHT_THEME_COLORS: Dict[str, str] = {
    "primary": "#0084FF",
    "secondary": "#F5F5F5",
    "background": "#FFFFFF",
    "surface": "#F0F0F0",
    "surface_hover": "#E8E8E8",
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "accent": "#FF6B35",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336",
    "border": "#CCCCCC",
}

# ============================================================================
# ANIMATION SETTINGS
# ============================================================================

ANIMATION_DURATION: int = 300  # milliseconds
FADE_IN_DURATION: int = 200
FADE_OUT_DURATION: int = 150
PAGE_TRANSITION_DURATION: int = 200

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_FORMAT: str = "[%(asctime)s] [%(levelname)s] - %(message)s"
LOG_FORMAT_CONSOLE: str = "[%(levelname)s] %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL: str = "DEBUG"
LOG_MAX_BYTES: int = 10485760  # 10 MB
LOG_BACKUP_COUNT: int = 7
LOG_BUFFER_SIZE: int = 500  # Max lines to keep in memory for GUI

# ============================================================================
# JSON SETTINGS
# ============================================================================

JSON_INDENT: int = 4
JSON_SORT_KEYS: bool = False

# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================

CPU_UPDATE_INTERVAL: int = 1000  # milliseconds
RAM_UPDATE_INTERVAL: int = 1000
STATUS_UPDATE_INTERVAL: int = 1000
LOG_DISPLAY_MAX_LINES: int = 100

# ============================================================================
# NOTIFICATION SETTINGS
# ============================================================================

NOTIFICATION_DURATION: int = 3000  # milliseconds
NOTIFICATION_POSITION: str = "top-right"  # top-right, top-left, bottom-right, bottom-left
NOTIFICATION_MAX_STACK: int = 5

# ============================================================================
# STATUS BAR SETTINGS
# ============================================================================

STATUS_BAR_HEIGHT: int = 30
STATUS_UPDATE_FREQUENCY: int = 1000  # milliseconds

# ============================================================================
# ICON MAPPINGS
# ============================================================================

ICONS: Dict[str, str] = {
    "dashboard": "dashboard.svg",
    "connection": "plug-zap.svg",
    "audio": "audio.svg",
    "screen": "monitor.svg",
    "chat": "chat.svg",
    "files": "folder.svg",
    "clipboard": "clipboard.svg",
    "settings": "settings.svg",
    "logs": "file-text.svg",
    "about": "info.svg",
    "notifications": "bell.svg",
    "theme": "moon-star.svg",
    "search": "search.svg",
    "download": "download.svg",
    "upload": "upload.svg",
    "refresh": "refresh-cw.svg",
    "close": "close.svg",
    "maximize": "maximize.svg",
    "minimize": "minimize.svg",
    "wifi": "wifi.svg",
    "user": "user-round.svg",
}

# ============================================================================
# PAGE NAMES
# ============================================================================

PAGE_DASHBOARD: str = "dashboard"
PAGE_CONNECTION: str = "connection"
PAGE_AUDIO: str = "audio"
PAGE_SCREEN: str = "screen"
PAGE_CHAT: str = "chat"
PAGE_FILES: str = "files"
PAGE_CLIPBOARD: str = "clipboard"
PAGE_SETTINGS: str = "settings"
PAGE_LOGS: str = "logs"
PAGE_ABOUT: str = "about"

PAGES_ORDER: Tuple[str, ...] = (
    PAGE_DASHBOARD,
    PAGE_CONNECTION,
    PAGE_AUDIO,
    PAGE_SCREEN,
    PAGE_CHAT,
    PAGE_FILES,
    PAGE_CLIPBOARD,
    PAGE_SETTINGS,
    PAGE_LOGS,
    PAGE_ABOUT,
)

# ============================================================================
# KEYBOARD SHORTCUTS
# ============================================================================

SHORTCUTS: Dict[str, str] = {
    "open_settings": "Ctrl+,",
    "open_dashboard": "Ctrl+Home",
    "open_logs": "Ctrl+L",
    "toggle_theme": "Ctrl+T",
    "minimize": "Ctrl+M",
    "maximize": "Ctrl+W",
    "quit": "Ctrl+Q",
}

# ============================================================================
# NETWORK SETTINGS (For Phase 3)
# ============================================================================

DEFAULT_HOST: str = "127.0.0.1"
DEFAULT_PORT: int = 5000
SOCKET_TIMEOUT: int = 10
HEARTBEAT_INTERVAL: int = 30  # seconds
HEARTBEAT_TIMEOUT: int = 60  # seconds

# ============================================================================
# STREAMING SETTINGS (For Phase 3)
# ============================================================================

DEFAULT_FPS: int = 30
DEFAULT_QUALITY: int = 75
MAX_FPS: int = 60
MIN_FPS: int = 5
MAX_QUALITY: int = 100
MIN_QUALITY: int = 20

# ============================================================================
# CACHE SETTINGS
# ============================================================================

CACHE_ICON_SIZE: Tuple[int, int] = (24, 24)
CACHE_THUMBNAIL_SIZE: Tuple[int, int] = (150, 150)

# ============================================================================
# ENVIRONMENT CHECKS
# ============================================================================

# Check if running from PyInstaller bundle
IS_FROZEN: bool = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

# Platform detection
PLATFORM: str = sys.platform
IS_WINDOWS: bool = sys.platform == "win32"
IS_LINUX: bool = sys.platform == "linux"
IS_MACOS: bool = sys.platform == "darwin"

# ============================================================================
# UTILITY FUNCTION
# ============================================================================


def ensure_directories() -> None:
    """
    Create all required directories if they don't exist.
    Called during application startup.

    Ensures the following directories are created:
    - CONFIG_DIR: Configuration files
    - LOGS_DIR: Log files
    - CACHE_DIR: Cache storage
    - TEMP_DIR: Temporary files
    - DOWNLOADS_DIR: Downloaded files
    """
    directories = [
        CONFIG_DIR,
        LOGS_DIR,
        CACHE_DIR,
        TEMP_DIR,
        DOWNLOADS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)