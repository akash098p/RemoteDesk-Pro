"""
===============================================================================
RemoteDesk Pro
File: gui/pages/about.py
Premium About page with modern glassmorphism UI
===============================================================================
"""

from __future__ import annotations

import customtkinter as ctk
import webbrowser
from typing import Callable


class AboutPage(ctk.CTkFrame):
    """
    Premium about/help page with detailed information and modern styling.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        """Create the premium about page layout."""
        # Main container with subtle padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=50, pady=30)

        # Header section with logo and title
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(30, 50))

        logo_label = ctk.CTkLabel(
            header_frame,
            text="🖥️",
            font=ctk.CTkFont(size=80, weight="bold"),
            text_color="#4A90E2"
        )
        logo_label.pack()

        title = ctk.CTkLabel(
            header_frame,
            text="RemoteDesk Pro",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        title.pack(pady=(15, 10))

        tagline = ctk.CTkLabel(
            header_frame,
            text="Professional Remote Desktop & Screen Sharing Solution",
            font=ctk.CTkFont(size=18),
            text_color=("#A0A0A0", "#CCCCCC")
        )
        tagline.pack(pady=10)

        # Version card with glass effect
        version_frame = ctk.CTkFrame(
            main_frame,
            fg_color=("#2A2A2A", "#F5F5F5"),
            corner_radius=20,
            border_width=0
        )
        version_frame.pack(fill="x", pady=30)

        version_title = ctk.CTkLabel(
            version_frame,
            text="Version",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#F5F5F5", "#111111")
        )
        version_title.pack(pady=(25, 5))

        version_num = ctk.CTkLabel(
            version_frame,
            text="2.0.0",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4A90E2"
        )
        version_num.pack(pady=(5, 25))

        # Features section
        features_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        features_frame.pack(fill="both", expand=True, pady=30)

        features = [
            ("🖥️", "Screen Sharing", "Share your desktop in real-time with high quality"),
            ("🎮", "Remote Control", "Control computers from anywhere securely"),
            ("💬", "Instant Chat", "Communicate with connected devices instantly"),
            ("📁", "File Transfer", "Drag-and-drop file transfers with resume support"),
            ("🎵", "Audio Sync", "Real-time microphone streaming during sessions"),
            ("🔒", "Security", "End-to-end encrypted connection protocol")
        ]

        # Create feature cards
        feature_cards = []
        for icon, title, description in features:
            card = self._create_feature_card(features_frame, icon, title, description)
            feature_cards.append(card)

        # Layout in grid
        for i, card in enumerate(feature_cards):
            row = i // 2
            col = i % 2
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        features_frame.columnconfigure(0, weight=1)
        features_frame.columnconfigure(1, weight=1)

        # Contact section
        contact_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        contact_frame.pack(fill="x", pady=30)

        ctk.CTkLabel(
            contact_frame,
            text="Contact & Support",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#E0E0E0", "#FFFFFF")
        ).pack(pady=(10, 20))

        contact_info = ["📧 support@remotedesk.pro", "🌐 www.remotedesk.pro", "🐙 GitHub: /remotedesk-pro"]

        for info in contact_info:
            label = ctk.CTkLabel(
                contact_frame,
                text=info,
                font=ctk.CTkFont(size=14),
                text_color=("#0880FF", "#E0E0E0")
            )
            label.pack(pady=5)

        # Quick links section
        links_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        links_frame.pack(fill="x", pady=30)

        link_title = ctk.CTkLabel(
            links_frame,
            text="Quick Links",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0880FF", "#E0E0E0")
        )
        link_title.pack(pady=(10, 15))

        link_buttons = [
            ("📚 Documentation", "https://remotedesk.pro/docs"),
            ("🚀 Getting Started", "https://remotedesk.pro/start"),
            ("❓ FAQ", "https://remotedesk.pro/faq")
        ]

        for link_text, url in link_buttons:
            link_btn = ctk.CTkButton(
                links_frame,
                text=link_text,
                font=ctk.CTkFont(size=14),
                height=35,
                width=200,
                fg_color=("#0880FF", "#2A4A6A"),
                command=lambda u=url: webbrowser.open(u)
            )
            link_btn.pack(pady=8)

        # Footer
        credits_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        credits_frame.pack(fill="x", pady=40)

        ctk.CTkLabel(
            credits_frame,
            text="© 2024 RemoteDesk Pro. All rights reserved.",
            font=ctk.CTkFont(size=12),
            text_color=("#888888", "#666666")
        ).pack()

    def _create_feature_card(self, parent, icon: str, title: str, description: str) -> ctk.CTkFrame:
        """Create a premium feature card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=("#2A2A2A", "#F5F5F5"),
            corner_radius=20,
            border_width=1,
            border_color=("#404040", "#DDDDDD")
        )
        card.pack_propagate(False)

        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=32))
        icon_label.pack(pady=(20, 10))

        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(0, 8))

        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=12),
            text_color=("#CCCCCC", "#666666"),
            wraplength=200
        )
        desc_label.pack(padx=20, pady=(0, 20))

        return card