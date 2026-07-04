"""
===============================================================================
RemoteDesk Pro
File: gui/components/dialogs.py

Reusable dialog windows for RemoteDesk Pro.
===============================================================================
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class BaseDialog(ctk.CTkToplevel):
    """Base dialog window."""

    def __init__(
        self,
        master,
        title: str = "Dialog",
        width: int = 420,
        height: int = 220,
    ) -> None:
        super().__init__(master)

        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(
            self,
            text=title,
            font=("Inter", 18, "bold"),
        )
        self.header.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="w",
        )

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew",
        )

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="ew",
        )


class MessageDialog(BaseDialog):
    """Simple message dialog."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
    ) -> None:
        super().__init__(master, title)

        ctk.CTkLabel(
            self.body,
            text=message,
            justify="left",
            wraplength=360,
            anchor="w",
        ).pack(fill="both", expand=True)

        ctk.CTkButton(
            self.footer,
            text="OK",
            width=100,
            command=self.destroy,
        ).pack(side="right")


class ConfirmDialog(BaseDialog):
    """Confirmation dialog."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, title)

        self._confirm = on_confirm
        self._cancel = on_cancel

        ctk.CTkLabel(
            self.body,
            text=message,
            justify="left",
            wraplength=360,
        ).pack(fill="both", expand=True)

        ctk.CTkButton(
            self.footer,
            text="Cancel",
            width=100,
            command=self._cancel_clicked,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            self.footer,
            text="Confirm",
            width=100,
            command=self._confirm_clicked,
        ).pack(side="right")

    def _confirm_clicked(self) -> None:
        if self._confirm:
            self._confirm()
        self.destroy()

    def _cancel_clicked(self) -> None:
        if self._cancel:
            self._cancel()
        self.destroy()


class InputDialog(BaseDialog):
    """Single-line text input dialog."""

    def __init__(
        self,
        master,
        title: str,
        prompt: str,
        on_submit: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(master, title)

        self._submit = on_submit

        ctk.CTkLabel(
            self.body,
            text=prompt,
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        self.entry = ctk.CTkEntry(self.body)
        self.entry.pack(fill="x")
        self.entry.focus()

        ctk.CTkButton(
            self.footer,
            text="Submit",
            width=100,
            command=self._submit_clicked,
        ).pack(side="right")

    def _submit_clicked(self) -> None:
        if self._submit:
            self._submit(self.entry.get())
        self.destroy()
