"""
===============================================================================
RemoteDesk Pro
File: gui/components/buttons.py

Reusable button components built on CustomTkinter.
===============================================================================
"""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk


class BaseButton(ctk.CTkButton):
    """Base reusable button."""

    def __init__(
        self,
        master,
        text: str = "",
        command: Callable | None = None,
        width: int = 140,
        height: int = 40,
        **kwargs,
    ) -> None:
        super().__init__(
            master=master,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            font=("Inter", 13),
            **kwargs,
        )


class PrimaryButton(BaseButton):
    """Primary action button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            **kwargs,
        )


class SecondaryButton(BaseButton):
    """Secondary action button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color="#374151",
            hover_color="#4B5563",
            text_color="white",
            **kwargs,
        )


class SuccessButton(BaseButton):
    """Success button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color="white",
            **kwargs,
        )


class DangerButton(BaseButton):
    """Danger button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            text_color="white",
            **kwargs,
        )


class SidebarButton(BaseButton):
    """Navigation sidebar button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            anchor="w",
            height=46,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#2D3748",
            text_color=("black", "white"),
            border_width=0,
            **kwargs,
        )


class IconButton(BaseButton):
    """Square icon button."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(
            master,
            text="",
            width=38,
            height=38,
            corner_radius=8,
            **kwargs,
        )
