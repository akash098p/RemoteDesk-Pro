"""
===============================================================================
RemoteDesk Pro
File: app.py
Entry point for the RemoteDesk Pro application.
This file initializes the application with the configured settings.
===============================================================================
"""

import sys
import os
from tkinter import Tk

from core.config_manager import get_config_manager
from gui.main_window import create_main_window

def main() -> None:
    # Set up configuration
    config = get_config_manager()
    config.load_all()  # Load any existing settings
    
    # Create main window
    app = Tk()
    app.title(f"{APP_NAME} v{APP_VERSION}")  # Need to store version in config
    
    # Create and run the main window
    main_window = create_main_window(config)
    main_window.run()
    
    # Keep the window running
    app.mainloop()

if __name__ == "__main__":
    main()