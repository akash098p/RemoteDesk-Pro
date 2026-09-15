"""
RemoteDesk Pro - File transfer support package.

Exposes the drag-and-drop helpers used by the file transfer page.
"""

from files.drag_drop import enable_file_drop, parse_dropped_data

__all__ = ["enable_file_drop", "parse_dropped_data"]