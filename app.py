"""
===============================================================================
RemoteDesk Pro
File: app.py
Entry point for the RemoteDesk Pro application.
This file initializes the application with the configured settings.
===============================================================================
"""

import sys
import tkinter
from tkinter import TclError

from core.config_manager import get_config_manager
from gui.main_window import create_main_window

def main() -> None:
    try:
        # Set up configuration
        config = get_config_manager()

        # Create and run the main window
        main_window = create_main_window(config)
        main_window.run()
    except TclError as exc:
        print(f"Unable to start GUI: {exc}", file=sys.stderr)
        print(
            "Install a Python build with Tk/Tcl support enabled, or use a Python environment that includes tkinter.",
            file=sys.stderr,
        )
        sys.exit(1)

if __name__ == "__main__":
    main()