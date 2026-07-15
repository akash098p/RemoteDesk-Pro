"""
===============================================================================
RemoteDesk Pro
File: gui/pages/about.py
About page with project information and creator links.
===============================================================================
"""

from __future__ import annotations

import os
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from core.constants import APP_VERSION
from core.theme_manager import get_theme_manager

IMAGES_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"
theme_manager = get_theme_manager()


class AboutPage(ctk.CTkFrame):
    """About and support page."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._social_icons: list[ctk.CTkImage] = []
        self._theme_callback_registered = False
        self._create_widgets()
        theme_manager.register_theme_change_callback(self._on_theme_change)
        self._theme_callback_registered = True

    def _create_widgets(self):
        hero_bg = theme_manager.get_color("glass_overlay", theme_manager.get_color("card_bg", "#162235"))
        section_bg = theme_manager.get_color("surface", "#1A2940")
        tile_bg = theme_manager.get_color("glass_overlay_alt", theme_manager.get_color("card_bg", "#162235"))
        border = theme_manager.get_color("border", "#31435F")
        text_secondary = theme_manager.get_color("text_secondary", "#AEB8C5")

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=18, pady=(12, 10))

        hero = ctk.CTkFrame(scroll_frame, fg_color=hero_bg, corner_radius=18, border_width=1, border_color=border)
        hero.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            hero,
            text="About RemoteDesk Pro",
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            hero,
            text="A modern Python desktop app for remote access, live screen sharing, chat, file transfer, clipboard sync, and future audio collaboration.",
            font=ctk.CTkFont(size=13),
            text_color=text_secondary,
            wraplength=920,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 18))

        overview = ctk.CTkFrame(scroll_frame, fg_color=section_bg, corner_radius=18, border_width=1, border_color=border)
        overview.pack(fill="x", pady=(0, 12))
        overview.grid_columnconfigure(0, weight=1)
        overview.grid_columnconfigure(1, weight=1)

        self._info_block(
            overview,
            0,
            "Project",
            [
                "RemoteDesk Pro",
                f"Version {APP_VERSION}",
            ],
        )
        self._info_block(
            overview,
            1,
            "Core Capabilities",
            [
                "Screen sharing and remote control",
                "Chat, clipboard sync, and file transfer",
                "LAN and public endpoint connectivity",
            ],
        )


        creator = ctk.CTkFrame(scroll_frame, fg_color=section_bg, corner_radius=18, border_width=1, border_color=border)
        creator.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            creator,
            text="Developer",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(18, 8))

        ctk.CTkLabel(
            creator,
            text="Akash Pramanik",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(0, 4))

        ctk.CTkLabel(
            creator,
            text="Open-source developer building RemoteDesk Pro as a modern remote collaboration platform.",
            font=ctk.CTkFont(size=13),
            text_color=text_secondary,
            wraplength=920,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(0, 14))

        links_row = ctk.CTkFrame(creator, fg_color="transparent")
        links_row.pack(fill="x", padx=22, pady=(0, 18))

        for title, label, url, icon_name in [
            ("GitHub", "akash098p/RemoteDesk-Pro", "https://github.com/akash098p/RemoteDesk-Pro", "GitHub-logo.png"),
            ("Instagram", "@akash.098p", "https://instagram.com/akash.098p", "Instagram-Logo.png"),
            ("Gmail", "akashpramanik098@gmail.com", "mailto:akashpramanik098@gmail.com", "Gmail-Logo.png"),
        ]:
            self._create_social_link(links_row, title, label, url, icon_name)

        

    def _info_block(self, parent, column: int, title: str, lines: list[str]) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=theme_manager.get_color("glass_overlay_alt", theme_manager.get_color("card_bg", "#162235")),
            corner_radius=14,
            border_width=1,
            border_color=theme_manager.get_color("border", "#31435F"),
        )
        card.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(16, 10))

        for line in lines:
            ctk.CTkLabel(
                card,
                text=line,
                font=ctk.CTkFont(size=13),
                justify="left",
                anchor="w",
                wraplength=360,
            ).pack(fill="x", padx=18, pady=3)

        ctk.CTkLabel(card, text="").pack(pady=(0, 10))

    def _create_social_link(
        self,
        parent,
        title: str,
        label: str,
        url: str,
        icon_name: str,
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            fg_color=theme_manager.get_color("glass_overlay_alt", theme_manager.get_color("card_bg", "#162235")),
            corner_radius=14,
            border_width=1,
            border_color=theme_manager.get_color("border", "#31435F"),
        )
        card.pack(side="left", fill="y", padx=(0, 12))

        icon = self._load_social_icon(icon_name)

        ctk.CTkButton(
            card,
            text="",
            image=icon,
            width=54,
            height=54,
            corner_radius=14,
            command=lambda link=url: webbrowser.open(link),
            fg_color=theme_manager.get_color("surface", "#1A2940"),
            hover_color=theme_manager.get_color("surface_hover", "#223653"),
        ).pack(padx=14, pady=(14, 10))

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="center", padx=14)

        ctk.CTkLabel(
            card,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=theme_manager.get_color("text_secondary", "#AEB8C5"),
            wraplength=150,
            justify="center",
        ).pack(anchor="center", padx=10, pady=(4, 14))

    def _on_theme_change(self, theme_name: str) -> None:
        for child in self.winfo_children():
            child.destroy()
        self._social_icons.clear()
        self._create_widgets()

    def _load_social_icon(self, icon_name: str) -> ctk.CTkImage | None:
        icon_path = IMAGES_DIR / icon_name
        if not icon_path.exists():
            return None

        image = Image.open(icon_path).convert("RGBA")
        icon = ctk.CTkImage(light_image=image, dark_image=image, size=(36, 36))
        self._social_icons.append(icon)
        return icon

    def destroy(self) -> None:
        if self._theme_callback_registered:
            theme_manager.unregister_theme_change_callback(self._on_theme_change)
        super().destroy()
