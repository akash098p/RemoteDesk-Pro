"""
RemoteDesk Pro
File: core/constants.py

Central application constants for Phase 2.
"""

from __future__ import annotations

from pathlib import Path

# -----------------------------------------------------------------------------
# Application Information
# -----------------------------------------------------------------------------

APP_NAME = "RemoteDesk Pro"
APP_VERSION = "0.2.0"
APP_AUTHOR = "Akash Pramanik"
APP_DESCRIPTION = "Professional Cross-Platform Remote Collaboration Platform"
APP_LICENSE = "MIT"

# -----------------------------------------------------------------------------
# Project Paths
# -----------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = ROOT_DIR / "assets"
CONFIG_DIR = ROOT_DIR / "config"
CORE_DIR = ROOT_DIR / "core"
GUI_DIR = ROOT_DIR / "gui"
NETWORK_DIR = ROOT_DIR / "network"
STREAMING_DIR = ROOT_DIR / "streaming"
REMOTE_CONTROL_DIR = ROOT_DIR / "remote_control"
FILES_DIR = ROOT_DIR / "files"
CHAT_DIR = ROOT_DIR / "chat"
AUDIO_DIR = ROOT_DIR / "audio"
CLIPBOARD_DIR = ROOT_DIR / "clipboard"
STORAGE_DIR = ROOT_DIR / "storage"

CACHE_DIR = ROOT_DIR / "cache"
TEMP_DIR = ROOT_DIR / "temp"
LOGS_DIR = ROOT_DIR / "logs"
DOWNLOADS_DIR = ROOT_DIR / "downloads"
DOCS_DIR = ROOT_DIR / "docs"
TESTS_DIR = ROOT_DIR / "tests"

DOWNLOADS_RECEIVED_DIR = DOWNLOADS_DIR / "received"
DOWNLOADS_EXPORTS_DIR = DOWNLOADS_DIR / "exports"
DOWNLOADS_UPDATES_DIR = DOWNLOADS_DIR / "updates"

ICONS_DIR = ASSETS_DIR / "icons"
IMAGES_DIR = ASSETS_DIR / "images"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"
EMOJIS_DIR = ASSETS_DIR / "emojis"

GUI_COMPONENTS_DIR = GUI_DIR / "components"
GUI_PAGES_DIR = GUI_DIR / "pages"
GUI_THEMES_DIR = GUI_DIR / "themes"

# -----------------------------------------------------------------------------
# Config Files
# -----------------------------------------------------------------------------

CONFIG_FILE = CONFIG_DIR / "config.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
USERS_FILE = CONFIG_DIR / "users.json"
SHORTCUTS_FILE = CONFIG_DIR / "shortcuts.json"

# -----------------------------------------------------------------------------
# Log Files
# -----------------------------------------------------------------------------

APPLICATION_LOG_FILE = LOGS_DIR / "application.log"
ERROR_LOG_FILE = LOGS_DIR / "error.log"
DEBUG_LOG_FILE = LOGS_DIR / "debug.log"

# -----------------------------------------------------------------------------
# Window
# -----------------------------------------------------------------------------

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
MIN_WINDOW_WIDTH = 1100
MIN_WINDOW_HEIGHT = 700

SIDEBAR_WIDTH = 250
SIDEBAR_COLLAPSED_WIDTH = 70
TOOLBAR_HEIGHT = 50
STATUSBAR_HEIGHT = 28

# -----------------------------------------------------------------------------
# Themes
# -----------------------------------------------------------------------------

DEFAULT_THEME = "dark"

SUPPORTED_THEMES = (
    "dark",
    "light",
    "dracula",
    "nord",
    "amoled",
)

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_FILE_SIZE = 5 * 1024 * 1024
BACKUP_LOG_COUNT = 5

# -----------------------------------------------------------------------------
# Refresh Intervals (ms)
# -----------------------------------------------------------------------------

CPU_REFRESH_INTERVAL = 1000
RAM_REFRESH_INTERVAL = 1000
NOTIFICATION_DURATION = 3500

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------

UTF8 = "utf-8"
JSON_INDENT = 4
JSON_SORT_KEYS = False

REQUIRED_DIRECTORIES = (
    CACHE_DIR,
    TEMP_DIR,
    LOGS_DIR,
    DOWNLOADS_DIR,
    DOWNLOADS_RECEIVED_DIR,
    DOWNLOADS_EXPORTS_DIR,
    DOWNLOADS_UPDATES_DIR,
)
