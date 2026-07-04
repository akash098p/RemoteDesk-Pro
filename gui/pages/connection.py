"""
===============================================================================
RemoteDesk Pro
File: gui/pages/connection.py

Connection page (Phase 2 UI Foundation)
===============================================================================
"""
from __future__ import annotations

import customtkinter as ctk

from gui.components.buttons import PrimaryButton, SecondaryButton
from gui.components.cards import InfoCard, PageCard
from gui.components.widgets import LabeledEntry, PageHeader


class ConnectionPage(ctk.CTkFrame):
    """Connection management page."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = PageHeader(
            self,
            title="Connection",
            subtitle="Prepare remote sessions (Networking arrives in Phase 3)",
        )
        header.grid(row=0, column=0, columnspan=2,
                    sticky="ew", padx=20, pady=(20, 10))

        left = PageCard(self)
        left.grid(row=1, column=0, sticky="nsew",
                  padx=(20, 10), pady=(0, 20))
        left.grid_columnconfigure(0, weight=1)

        self.remote_id = LabeledEntry(
            left,
            label="Remote ID",
            placeholder="Enter remote device ID",
        )
        self.remote_id.grid(row=0, column=0, sticky="ew",
                            padx=20, pady=(20, 12))

        self.password = LabeledEntry(
            left,
            label="Password",
            placeholder="Enter session password",
            show="•",
        )
        self.password.grid(row=1, column=0, sticky="ew",
                           padx=20, pady=12)

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="e", padx=20, pady=20)

        PrimaryButton(
            btns,
            text="Connect",
            width=120,
            command=self.connect,
        ).pack(side="left", padx=(0, 8))

        SecondaryButton(
            btns,
            text="Clear",
            width=120,
            command=self.clear,
        ).pack(side="left")

        self.status = ctk.CTkLabel(
            left,
            text="Ready",
            anchor="w",
            font=("Inter", 11),
        )
        self.status.grid(row=3, column=0, sticky="ew",
                         padx=20, pady=(0, 20))

        right = InfoCard(
            self,
            title="Phase 2",
            content=(
                "This page provides the complete connection UI.\n\n"
                "Networking, authentication, encrypted transport, "
                "session negotiation and remote desktop streaming "
                "will be implemented during Phase 3."
            ),
        )
        right.grid(row=1, column=1, sticky="nsew",
                   padx=(10, 20), pady=(0, 20))

    def connect(self) -> None:
        """Placeholder UI action for Phase 2."""
        self.status.configure(
            text=f"Prepared connection to: {self.remote_id.get() or 'Unknown'}"
        )

    def clear(self) -> None:
        """Clear all fields."""
        self.remote_id.clear()
        self.password.clear()
        self.status.configure(text="Ready")
