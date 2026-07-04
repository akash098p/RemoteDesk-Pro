"""
===============================================================================
RemoteDesk Pro
File: app.py

Application entry point.
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from core.config_manager import ConfigManager
from core.constants import DEFAULT_THEME
from core.logger import Logger
from core.theme_manager import ThemeManager
from gui.main_window import MainWindow


def bootstrap() -> None:
    """Initialize application services."""
    Logger.configure()

    config = ConfigManager()

    theme_name = config.config.get("theme", DEFAULT_THEME)

    try:
        ThemeManager().load_theme(theme_name)
    except Exception:
        Logger.get_logger(__name__).warning(
            "Unable to load theme '%s'. Falling back to default.",
            theme_name,
        )
        ThemeManager().load_theme(DEFAULT_THEME)

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")


def main() -> None:
    """Start RemoteDesk Pro."""
    bootstrap()

    logger = Logger.get_logger(__name__)
    logger.info("Starting RemoteDesk Pro...")

    app = MainWindow()

    logger.info("Main window initialized.")

    app.mainloop()

    logger.info("Application closed.")


if __name__ == "__main__":
    main()
