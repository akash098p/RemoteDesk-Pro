"""
===============================================================================
RemoteDesk Pro
File: core/utils.py

Contains various utility functions for system monitoring, asset loading,
and general helper operations across the application.
===============================================================================
"""
from __future__ import annotations

import os
import sys
import platform
from pathlib import Path
from functools import lru_cache
from typing import Any, Callable, Tuple, TypeVar, Union

import psutil
import customtkinter
from PIL import Image

from core.constants import (
    ICONS_DIR,
    IMAGES_DIR,
    CACHE_ICON_SIZE,
    APP_VERSION,
    ensure_directories as _ensure_directories,
)
from core.logger import get_logger

logger = get_logger()

R = TypeVar('R') # Return type for decorator


def ensure_directories() -> None:
    """Compatibility wrapper for the directory-creation helper."""
    _ensure_directories()

def run_in_thread(func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator to run a function in a separate thread.
    Useful for preventing UI freezes during long-running operations.
    """
    from threading import Thread # Deferred import to avoid circular dependencies if used early
    def wrapper(*args: Any, **kwargs: Any) -> R:
        thread = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return None # TypeVar R expects a return, but thread does not return to caller directly
    return wrapper # type: ignore


@lru_cache(maxsize=128) # Cache loaded images to prevent repeated disk I/O
def load_image(image_name: str, path: Path = ICONS_DIR, size: Tuple[int, int] = CACHE_ICON_SIZE) -> Optional[customtkinter.CTkImage]:
    """
    Loads an image (SVG, PNG, JPG) and converts it to a CTkImage object.
    Images are cached to optimize performance.

    Args:
        image_name: The name of the image file (e.g., "dashboard.svg", "logo.png").
        path: The directory where the image is located (defaults to ICONS_DIR).
        size: A tuple (width, height) for resizing the image. Defaults to CACHE_ICON_SIZE.

    Returns:
        A CTkImage object if successful, None otherwise.
    """
    image_path = path / image_name

    if not image_path.exists():
        # If the requested image is SVG and a PNG replacement exists, try that first.
        if image_path.suffix.lower() == ".svg":
            png_fallback = image_path.with_suffix(".png")
            if png_fallback.exists():
                image_path = png_fallback
                logger.debug(f"Falling back to PNG icon for SVG reference: {png_fallback.name}")
            else:
                logger.warning(f"Image file not found: {image_path}")
                return None
        else:
            png_fallback = image_path.with_suffix(".png")
            if png_fallback.exists():
                image_path = png_fallback
                logger.debug(f"Falling back to PNG icon: {png_fallback.name}")
            else:
                logger.warning(f"Image file not found: {image_path}")
                return None

    try:
        if image_path.suffix.lower() == ".svg":
            png_fallback = image_path.with_suffix(".png")
            if png_fallback.exists():
                image_path = png_fallback
                logger.debug(f"Using PNG fallback for unsupported SVG image: {png_fallback.name}")
            else:
                logger.warning(f"Skipping SVG image loading for unsupported format: {image_path}")
                return None

        pil_image = Image.open(image_path)
        pil_image = pil_image.resize(size, Image.LANCZOS)
        image = customtkinter.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)

        logger.debug(f"Loaded image: {image_path.name} with size {size}")
        return image
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}", exc_info=True)
        return None

def get_cpu_usage() -> float:
    """
    Retrieves the current CPU usage percentage.

    Returns:
        A float representing the CPU usage percentage.
    """
    try:
        # interval=None means non-blocking (first call always 0.0 or requires previous call)
        # A short interval (e.g., 0.1) provides a more accurate immediate reading
        return psutil.cpu_percent(interval=0.1)
    except psutil.AccessDenied:
        logger.error("Access denied for CPU usage. Running as administrator might be required.")
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
    return 0.0

def get_ram_usage() -> Tuple[float, float, float]:
    """
    Retrieves the current RAM usage percentage and total/available memory in GB.

    Returns:
        A tuple (percentage, total_gb, available_gb).
    """
    try:
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024**3), 2)
        available_gb = round(mem.available / (1024**3), 2)
        return mem.percent, total_gb, available_gb
    except psutil.AccessDenied:
        logger.error("Access denied for RAM usage. Running as administrator might be required.")
    except Exception as e:
        logger.error(f"Error getting RAM usage: {e}")
    return 0.0, 0.0, 0.0

def get_app_version() -> str:
    """
    Returns the application version from constants.

    Returns:
        A string representing the application version.
    """
    return APP_VERSION

def get_system_info() -> Dict[str, str]:
    """
    Gathers basic system information.

    Returns:
        A dictionary containing system information.
    """
    info = {
        "Platform": platform.system(),
        "OS Version": platform.release(),
        "Architecture": platform.machine(),
        "Python Version": platform.python_version(),
        "CPU Cores": str(psutil.cpu_count(logical=True)),
        "RAM Total": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
    }
    return info

def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """
    Returns the absolute path for a resource, handling PyInstaller bundling.

    Args:
        relative_path: The path to the resource relative to the project root or asset directory.

    Returns:
        The absolute Path object for the resource.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        return bundle_dir / relative_path
    else:
        # Running in a regular Python environment
        return Path(relative_path)


def clamp(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """
    Clamps a value within a specified range.

    Args:
        value: The value to clamp.
        min_value: The minimum allowed value.
        max_value: The maximum allowed value.

    Returns:
        The clamped value.
    """
    return max(min_value, min(value, max_value))

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Converts a hexadecimal color string to an RGB tuple.

    Args:
        hex_color: The hex color string (e.g., "#RRGGBB" or "#RGB").

    Returns:
        An RGB tuple (R, G, B).
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

def rgb_to_hex(rgb_color: Tuple[int, int, int]) -> str:
    """
    Converts an RGB tuple to a hexadecimal color string.

    Args:
        rgb_color: An RGB tuple (R, G, B).

    Returns:
        The hex color string (e.g., "#RRGGBB").
    """
    return f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
