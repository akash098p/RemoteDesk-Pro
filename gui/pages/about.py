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

import customtkinter as ctk
from PIL import Image

from core.constants import APP_VERSION

ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")


class AboutPage(ctk.CTkFrame):
    """About and support page."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._social_icons: list[ctk.CTkImage] = []
        self._create_widgets()

    def _create_widgets(self):
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=18, pady=(12, 10))

        hero = ctk.CTkFrame(scroll_frame, fg_color=("#F4F7FB", "#1D232B"), corner_radius=18)
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
            text_color=("#5B6574", "#AEB8C5"),
            wraplength=920,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 18))

        overview = ctk.CTkFrame(scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
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
                "Inspired by AnyDesk, TeamViewer, and Chrome Remote Desktop.",
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

        features_card = ctk.CTkFrame(scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        features_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            features_card,
            text="Feature Highlights",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(18, 10))

        for line in [
            "High-quality desktop streaming with adjustable FPS and quality.",
            "Permission-based remote control with keyboard and mouse support.",
            "Two-way chat and attachments during remote sessions.",
            "Clipboard and file workflows designed for collaboration.",
            "Cross-network access through public TCP tunneling.",
        ]:
            ctk.CTkLabel(
                features_card,
                text=f"- {line}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                justify="left",
                wraplength=920,
            ).pack(fill="x", padx=22, pady=4)

        creator = ctk.CTkFrame(scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        creator.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            creator,
            text="Maker",
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
            text_color=("#5B6574", "#AEB8C5"),
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

        support = ctk.CTkFrame(scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=18)
        support.pack(fill="x")

        ctk.CTkLabel(
            support,
            text="Support the Project",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=22, pady=(18, 10))

        for line in [
            "Star the repository if the project is useful to you.",
            "Report issues when you find a bug or session problem.",
            "Suggest new features to help shape the roadmap.",
        ]:
            ctk.CTkLabel(
                support,
                text=f"- {line}",
                font=ctk.CTkFont(size=13),
                anchor="w",
                justify="left",
                wraplength=920,
            ).pack(fill="x", padx=22, pady=4)

        ctk.CTkLabel(
            support,
            text="MIT License",
            font=ctk.CTkFont(size=12),
            text_color=("#5B6574", "#AEB8C5"),
        ).pack(anchor="w", padx=22, pady=(10, 18))

    def _info_block(self, parent, column: int, title: str, lines: list[str]) -> None:
        card = ctk.CTkFrame(parent, fg_color=("white", "#14191F"), corner_radius=14)
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
        card = ctk.CTkFrame(parent, fg_color=("white", "#14191F"), corner_radius=14)
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
            fg_color=("white", "#1D232B"),
            hover_color=("#E8EDF5", "#2A3440"),
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
            text_color=("#5B6574", "#AEB8C5"),
            wraplength=150,
            justify="center",
        ).pack(anchor="center", padx=10, pady=(4, 14))

    def _load_social_icon(self, icon_name: str) -> ctk.CTkImage | None:
        icon_path = os.path.join(ICONS_DIR, icon_name)
        if not os.path.exists(icon_path):
            return None

        image = Image.open(icon_path).convert("RGBA")
        icon = ctk.CTkImage(light_image=image, dark_image=image, size=(36, 36))
        self._social_icons.append(icon)
        return icon
