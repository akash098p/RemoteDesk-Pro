"""
===============================================================================
RemoteDesk Pro
File: gui/components/dialogs.py
Reusable modal dialogs (info, confirmation, input, progress) for the application.
All dialogs are theme‑aware, block interaction with the parent window,
and return explicit results to the caller.
===============================================================================
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Optional, Tuple

import customtkinter
from PIL import ImageTk, Image

from core.constants import (
    ICONS_DIR,
    PADDING,
    CORNER_RADIUS,
    FONT_SIZE_BODY,
    FONT_SIZE_LABEL,
)
from core.theme_manager import get_theme_manager
from core.utils import load_image

theme_manager = get_theme_manager()


class _BaseDialog(customtkinter.CTkToplevel):
    """
    Base class for modal dialogs.
    Provides common layout, theme handling, and modal behavior.
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        icon_name: Optional[str] = None,
        width: int = 350,
        height: int = 150,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self.title(title)
        self.resizable(False, False)
        self.geometry(f"{width}x{height}+{self._center_x(master, width)}+{self._center_y(master, height)}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)  # Capture window close

        # Make the dialog modal
        self.transient(master)
        self.grab_set()

        # Theme integration
        self.configure(fg_color=theme_manager.get_color("dialog_bg", "#2D2D2D"))
        theme_manager.register_theme_change_callback(self._apply_theme)

        # Optional icon
        if icon_name:
            self._icon = load_image(icon_name, size=(32, 32))
            if self._icon:
                icon_label = customtkinter.CTkLabel(self, image=self._icon, text="")
                icon_label.pack(pady=(PADDING, 0))

        # Title label
        self._title_label = customtkinter.CTkLabel(
            self,
            text=title,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_LABEL, weight="bold"),
            text_color=theme_manager.get_color("dialog_title", "#FFFFFF"),
        )
        self._title_label.pack(pady=(PADDING // 2, PADDING))

        # Content placeholder – subclasses will fill this
        self._content_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self._content_frame.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

        # Footer placeholder for action buttons
        self._footer_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self._footer_frame.pack(fill="x", side="bottom", pady=(0, PADDING))

        self._result: Any = None

    # --------------------------------------------------------------------- #
    # Layout helpers
    # --------------------------------------------------------------------- #
    @staticmethod
    def _center_x(parent: customtkinter.CTk, width: int) -> int:
        parent_x = parent.winfo_rootx()
        parent_w = parent.winfo_width()
        return parent_x + (parent_w - width) // 2

    @staticmethod
    def _center_y(parent: customtkinter.CTk, height: int) -> int:
        parent_y = parent.winfo_rooty()
        parent_h = parent.winfo_height()
        return parent_y + (parent_h - height) // 2

    # --------------------------------------------------------------------- #
    # Theme handling
    # --------------------------------------------------------------------- #
    def _apply_theme(self, _: str) -> None:
        """Refresh colors when the theme changes."""
        self.configure(fg_color=theme_manager.get_color("dialog_bg", "#2D2D2D"))
        self._title_label.configure(
            text_color=theme_manager.get_color("dialog_title", "#FFFFFF")
        )

    # --------------------------------------------------------------------- #
    # Closing / result handling
    # --------------------------------------------------------------------- #
    def _on_close(self) -> None:
        """
        Called when the user clicks the window close button.
        Sub‑classes can override if they need special behaviour.
        """
        self._result = None
        self.destroy()

    def get_result(self) -> Any:
        """Return the value set by the dialog (or None if cancelled)."""
        return self._result

    def destroy(self) -> None:
        """Clean up callbacks before destroying."""
        theme_manager.unregister_theme_change_callback(self._apply_theme)
        super().destroy()


# ------------------------------------------------------------------------- #
# Concrete dialog implementations
# ------------------------------------------------------------------------- #
class InfoDialog(_BaseDialog):
    """Simple informational dialog with an OK button."""

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        message: str,
        icon_name: Optional[str] = "info.svg",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title, icon_name, **kwargs)

        # Message label
        msg_label = customtkinter.CTkLabel(
            self._content_frame,
            text=message,
            justify="center",
            wraplength=300,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=theme_manager.get_color("dialog_text", "#E0E0E0"),
        )
        msg_label.pack(expand=True, fill="both")

        # OK button
        ok_btn = customtkinter.CTkButton(
            self._footer_frame,
            text="OK",
            command=self._on_ok,
            width=80,
            corner_radius=CORNER_RADIUS,
        )
        ok_btn.pack(pady=(0, PADDING // 2))

    def _on_ok(self) -> None:
        self._result = True
        self.destroy()


class ConfirmDialog(_BaseDialog):
    """Confirmation dialog with Yes / No buttons."""

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        question: str,
        icon_name: Optional[str] = "question.svg",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title, icon_name, **kwargs)

        # Question label
        q_label = customtkinter.CTkLabel(
            self._content_frame,
            text=question,
            justify="center",
            wraplength=300,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=theme_manager.get_color("dialog_text", "#E0E0E0"),
        )
        q_label.pack(expand=True, fill="both")

        # Buttons
        btn_frame = customtkinter.CTkFrame(self._footer_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, PADDING // 2))

        yes_btn = customtkinter.CTkButton(
            btn_frame,
            text="Yes",
            command=self._on_yes,
            width=70,
            corner_radius=CORNER_RADIUS,
        )
        yes_btn.pack(side="left", padx=5)

        no_btn = customtkinter.CTkButton(
            btn_frame,
            text="No",
            command=self._on_no,
            width=70,
            corner_radius=CORNER_RADIUS,
        )
        no_btn.pack(side="left", padx=5)

    def _on_yes(self) -> None:
        self._result = True
        self.destroy()

    def _on_no(self) -> None:
        self._result = False
        self.destroy()


class InputDialog(_BaseDialog):
    """Dialog that asks the user for a free‑form text input."""

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        prompt: str,
        default: str = "",
        icon_name: Optional[str] = "pencil.svg",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title, icon_name, **kwargs)

        # Prompt
        prompt_label = customtkinter.CTkLabel(
            self._content_frame,
            text=prompt,
            justify="left",
            wraplength=300,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=theme_manager.get_color("dialog_text", "#E0E0E0"),
        )
        prompt_label.pack(anchor="w", pady=(0, PADDING // 2))

        # Entry field
        self._entry = customtkinter.CTkEntry(
            self._content_frame,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            justify="left",
            width=260,
            height=30,
        )
        self._entry.insert(0, default)
        self._entry.pack(pady=(0, PADDING // 2))
        self._entry.focus_set()

        # Buttons
        btn_frame = customtkinter.CTkFrame(self._footer_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, PADDING // 2))

        ok_btn = customtkinter.CTkButton(
            btn_frame,
            text="OK",
            command=self._on_ok,
            width=70,
            corner_radius=CORNER_RADIUS,
        )
        ok_btn.pack(side="left", padx=5)

        cancel_btn = customtkinter.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._on_cancel,
            width=70,
            corner_radius=CORNER_RADIUS,
        )
        cancel_btn.pack(side="left", padx=5)

        # Bind Enter / Escape keys
        self.bind("<Return>", lambda _: self._on_ok())
        self.bind("<Escape>", lambda _: self._on_cancel())

    def _on_ok(self) -> None:
        self._result = self._entry.get()
        self.destroy()

    def _on_cancel(self) -> None:
        self._result = None
        self.destroy()


class ProgressDialog(_BaseDialog):
    """
    Modal progress dialog with an optional cancel button.
    Call `set_progress(percent)` to update the bar (0‑100).
    Call `close()` when the operation finishes.
    """

    def __init__(
        self,
        master: customtkinter.CTk,
        title: str,
        message: str = "Processing...",
        cancellable: bool = False,
        icon_name: Optional[str] = "hourglass.svg",
        **kwargs: Any,
    ) -> None:
        super().__init__(master, title, icon_name, width=400, height=180, **kwargs)

        # Message
        self._msg_label = customtkinter.CTkLabel(
            self._content_frame,
            text=message,
            font=customtkinter.CTkFont(family="Inter", size=FONT_SIZE_BODY),
            text_color=theme_manager.get_color("dialog_text", "#E0E0E0"),
        )
        self._msg_label.pack(pady=(0, PADDING // 2))

        # Progress bar
        self._progress = customtkinter.CTkProgressBar(
            self._content_frame,
            width=340,
            height=20,
        )
        self._progress.set(0.0)
        self._progress.pack(pady=(0, PADDING // 2))

        # Cancel button (optional)
        self._cancellable = cancellable
        self._cancel_requested = False
        if cancellable:
            cancel_btn = customtkinter.CTkButton(
                self._footer_frame,
                text="Cancel",
                command=self._on_cancel,
                width=80,
                corner_radius=CORNER_RADIUS,
            )
            cancel_btn.pack(pady=(0, PADDING // 2))

    def set_message(self, message: str) -> None:
        """Update the status message shown above the progress bar."""
        self._msg_label.configure(text=message)

    def set_progress(self, percent: float) -> None:
        """
        Update progress bar.
        `percent` should be within 0‑100.
        """
        clamped = max(0.0, min(100.0, percent)) / 100.0
        self._progress.set(clamped)

    def _on_cancel(self) -> None:
        """User requested cancellation."""
        self._cancel_requested = True

    def was_cancelled(self) -> bool:
        """Return True if the user pressed the Cancel button."""
        return self._cancel_requested

    def close(self) -> None:
        """Close the dialog and release the grab."""
        self.destroy()


# ------------------------------------------------------------------------- #
# Helper functions – easy to call from anywhere in the codebase
# ------------------------------------------------------------------------- #
def show_info(
    master: customtkinter.CTk,
    title: str,
    message: str,
    icon_name: Optional[str] = "info.svg",
) -> bool:
    """Display an informational dialog and wait for the user to acknowledge."""
    dialog = InfoDialog(master, title, message, icon_name)
    master.wait_window(dialog)
    return bool(dialog.get_result())


def ask_confirm(
    master: customtkinter.CTk,
    title: str,
    question: str,
    icon_name: Optional[str] = "question.svg",
) -> bool:
    """Show a Yes/No confirmation dialog."""
    dialog = ConfirmDialog(master, title, question, icon_name)
    master.wait_window(dialog)
    return bool(dialog.get_result())


def ask_input(
    master: customtkinter.CTk,
    title: str,
    prompt: str,
    default: str = "",
    icon_name: Optional[str] = "pencil.svg",
) -> Optional[str]:
    """Show a modal input dialog and return the entered string (or None)."""
    dialog = InputDialog(master, title, prompt, default, icon_name)
    master.wait_window(dialog)
    return dialog.get_result()


def show_progress(
    master: customtkinter.CTk,
    title: str,
    message: str = "Processing...",
    cancellable: bool = False,
    icon_name: Optional[str] = "hourglass.svg",
) -> ProgressDialog:
    """
    Create and display a progress dialog.
    The caller is responsible for calling `set_progress`,
    `set_message`, and `close` when the operation finishes.
    """
    dialog = ProgressDialog(master, title, message, cancellable, icon_name)
    # The dialog is already modal because of `grab_set` in _BaseDialog.
    return dialog


# ------------------------------------------------------------------------- #
# Simple test harness (run this file directly)
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    root = customtkinter.CTk()
    root.geometry("600x400")
    root.title("Dialog Demo")

    def demo():
        show_info(root, "Information", "This is an info dialog.")
        r = ask_confirm(root, "Confirm", "Do you wish to continue?")
        print("Confirm result:", r)
        txt = ask_input(root, "Input needed", "Your name:", default="John Doe")
        print("Input result:", txt)
        prog = show_progress(root, "Loading", cancellable=True)
        for i in range(101):
            prog.set_progress(i)
            prog.set_message(f"Progress: {i}%")
            root.update()
            root.after(30)
            if prog.was_cancelled():
                break
        prog.close()

    btn = customtkinter.CTkButton(root, text="Run Dialog Demo", command=demo)
    btn.pack(pady=30)

    root.mainloop()