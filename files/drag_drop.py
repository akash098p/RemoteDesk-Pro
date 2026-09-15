"""
RemoteDesk Pro
File: files/drag_drop.py

Cross-platform file drag-and-drop support for Tk widgets.

Uses the TkDnD extension (via ``tkinterdnd2``) when available. When the
extension is missing, :func:`enable_file_drop` returns ``None`` so callers
can fall back to file-picker dialogs instead of crashing.
"""

from __future__ import annotations

import os
import re
from typing import Any, Callable, List, Optional

from core.logger import get_logger

logger = get_logger()

# None = not probed yet, True/False after the first attempt.
_EXTENSION_STATE: Optional[bool] = None


def _load_tkdnd(root: Any) -> bool:
    """Load the TkDnD extension into the given Tk interpreter (once per app)."""
    global _EXTENSION_STATE
    if _EXTENSION_STATE is not None:
        return _EXTENSION_STATE

    try:
        import tkinterdnd2  # noqa: F401 - patches BaseWidget with dnd_* helpers
        from tkinterdnd2 import TkinterDnD

        TkinterDnD._require(root)
        _EXTENSION_STATE = True
        logger.info("TkDnD drag-and-drop extension loaded.")
    except Exception as exc:
        _EXTENSION_STATE = False
        logger.info(
            f"Drag-and-drop unavailable ({exc}); use the Send Files/Folder buttons instead."
        )
    return _EXTENSION_STATE


def parse_dropped_data(data: str) -> List[str]:
    """Parse a TkDnD data string into a list of existing file/folder paths."""
    if not data:
        return []

    text = data.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]

    paths: List[str] = []
    for part in re.split(r"\}\s*\{", text):
        candidate = part.strip().strip("{}").strip()
        if not candidate:
            continue
        if "{{" in candidate or "}}" in candidate:
            # tkdnd escapes literal braces inside paths by doubling them.
            candidate = candidate.replace("{{", "{").replace("}}", "}")
        paths.append(os.path.normpath(candidate))
    return [p for p in paths if os.path.exists(p)]


def enable_file_drop(
    widget: Any,
    on_files: Callable[[List[str]], None],
    on_enter: Optional[Callable[[], None]] = None,
    on_leave: Optional[Callable[[], None]] = None,
) -> Optional[Any]:
    """
    Register ``widget`` as a drag-and-drop target for files.

    Args:
        widget: The Tk widget that should accept drops.
        on_files: Called with a list of dropped paths.
        on_enter: Optional highlight callback when a drag enters the widget.
        on_leave: Optional callback when the drag leaves or a drop finishes.

    Returns:
        A handle exposing ``unregister()`` when drag-and-drop is available,
        or ``None`` when the TkDnD extension is missing.
    """
    root = widget.winfo_toplevel()
    if not _load_tkdnd(root):
        return None

    try:
        widget.drop_target_register("DND_Files")
    except Exception as exc:
        logger.warning(f"Unable to register drop target: {exc}")
        return None

    def _handle_enter(event) -> str:
        if on_enter:
            try:
                on_enter()
            except Exception as exc:
                logger.debug(f"drop-enter callback failed: {exc}")
        return "copy"

    def _handle_leave(event) -> str:
        if on_leave:
            try:
                on_leave()
            except Exception as exc:
                logger.debug(f"drop-leave callback failed: {exc}")
        return "copy"

    def _handle_drop(event) -> str:
        if on_leave:
            try:
                on_leave()
            except Exception as exc:
                logger.debug(f"drop-leave callback failed: {exc}")
        paths = parse_dropped_data(getattr(event, "data", ""))
        if paths:
            try:
                on_files(paths)
            except Exception as exc:
                logger.error(f"Drop handler failed: {exc}")
        return "copy"

    handlers = {
        "<<DropEnter>>": _handle_enter,
        "<<DropLeave>>": _handle_leave,
        "<<Drop>>": _handle_drop,
    }
    try:
        for sequence, handler in handlers.items():
            widget.dnd_bind(sequence, handler)
    except Exception as exc:
        logger.warning(f"Unable to bind drop events: {exc}")
        try:
            widget.drop_target_unregister()
        except Exception:
            pass
        return None

    widget_ref = widget

    class _DropTarget:
        """Handle that keeps the registration alive and allows undoing it."""

        widget = widget_ref

        def unregister(self) -> None:
            for sequence in handlers:
                try:
                    widget.unbind(sequence)
                except Exception:
                    pass
            try:
                widget.drop_target_unregister()
            except Exception:
                pass

    return _DropTarget()