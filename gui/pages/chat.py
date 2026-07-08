"""
===============================================================================
RemoteDesk Pro
File: gui/pages/chat.py

Chat page for RemoteDesk Pro - Phase 5 Communication Module.
Provides real-time messaging interface with emoji support.
===============================================================================
"""

from __future__ import annotations

import os
from typing import Any

import customtkinter as ctk

from chat.emoji import EmojiManager
from chat.history import ChatHistoryManager
from core.logger import get_logger


class ChatPage(ctk.CTkFrame):
    """
    Visual representation of the chat subsystem.

    Parameters
    ----------
    parent : ctk.CTk
        The parent window (usually `MainWindow`).
    app_controller : Any
        Reference to the top‑level application controller (holds `chat_manager`,
        ``username``, etc.).
    """

    def __init__(self, parent: ctk.CTk, app_controller: Any, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self.logger = get_logger()
        self.app_controller = app_controller

        # --- State --------------------------------------------------------- #
        self.username: str = getattr(app_controller, "username", "Local")
        self._emoji_manager = EmojiManager()
        self._history_manager = ChatHistoryManager()
        self._is_connected: bool = False

        # --- Widgets ------------------------------------------------------- #
        self._create_widgets()
        self._setup_layout()
        self._style_widgets()

        self.logger.info("ChatPage initialized.")

    # --------------------------------------------------------------------- #
    #   Widget creation
    # --------------------------------------------------------------------- #
    def _create_widgets(self) -> None:
        # Header ------------------------------------------------------------ #
        self.header_frame = ctk.CTkFrame(self, height=55, fg_color=("#222222", "#111111"))
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Chat",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            text_color="#E0E0E0",
        )
        self.title_label.pack(side="left", padx=10, pady=12)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Disconnected",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B",
            anchor="e",
        )
        self.status_label.pack(side="right", padx=10, pady=12)

        # Content ----------------------------------------------------------- #
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Message list (scrollable) ------------------------------------------- #
        self.scrollable_messages = ctk.CTkScrollableFrame(
            self.content_frame,
            label_text="Conversation",
            fg_color=("gray10", "gray90"),
        )
        self.scrollable_messages.pack(side="left", fill="both", expand=True)

        # Input area ----------------------------------------------------------- #
        self.input_frame = ctk.CTkFrame(self.content_frame)
        self.input_frame.pack(side="bottom", fill="x", pady=5)

        # Emoji button
        self.emoji_btn = ctk.CTkButton(
            self.input_frame,
            text="😊",
            width=40,
            command=self._toggle_emoji_picker,
        )
        self.emoji_btn.pack(side="left", padx=5, pady=5)

        # Attachment button (placeholder for Phase 6)
        self.attach_btn = ctk.CTkButton(
            self.input_frame,
            text="📎",
            width=40,
            command=self._open_file_dialog,
        )
        self.attach_btn.pack(side="left", padx=5, pady=5)

        # Message entry ------------------------------------------------------- #
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message…",
            height=38,
            fg_color=("#2B2B2B", "#333333"),
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.message_entry.bind("<Return>", self._on_send_message)

        # Send button ---------------------------------------------------------- #
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=80,
            command=self._on_send_message,
            fg_color="#1E90FF",
            hover_color="#1C7ED6",
        )
        self.send_btn.pack(side="right", padx=5, pady=5)

        # Emoji picker popup -------------------------------------------------- #
        self.emoji_frame = ctk.CTkFrame(self, fg_color="white")
        self.emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-150)
        self.emoji_frame.place_forget()
        self._populate_emoji_grid()

        # Right‑top notification placeholder ----------------------------------- #
        self.notification_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.notification_frame.place(relx=0.5, rely=0.0, anchor="n", y=10)
        self.notification_frame.place_forget()

    def _populate_emoji_grid(self) -> None:
        """Create a small grid of emoji buttons using `EmojiManager`."""
        emojis = self._emoji_manager.get_emoji_shortcodes()
        row, col = 0, 0
        for shortcode in emojis:
            emoji_char = self._emoji_manager.emoji_map.get(shortcode, shortcode)
            btn = ctk.CTkButton(
                self.emoji_frame,
                text=emoji_char,
                width=35,
                height=35,
                corner_radius=4,
                command=lambda s=shortcode: self._append_emoji(s),
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 7:  # wrap after 7 items
                col = 0
                row += 1

    # --------------------------------------------------------------------- #
    #   Layout & styling
    # --------------------------------------------------------------------- #
    def _setup_layout(self) -> None:
        pass  # Layout is handled by pack() calls in _create_widgets

    def _style_widgets(self) -> None:
        self.configure(fg_color=("#1E1E1E", "#0D0D0D"))
        self.scrollable_messages.configure(
            fg_color=("gray15", "gray20"),
        )

    # --------------------------------------------------------------------- #
    #   Emoji handling
    # --------------------------------------------------------------------- #
    def _append_emoji(self, shortcode: str) -> None:
        """Append a selected emoji to the message entry field."""
        current = self.message_entry.get()
        self.message_entry.delete(0, "end")
        self.message_entry.insert(0, current + self._emoji_manager.emoji_map.get(shortcode, shortcode))

    def _toggle_emoji_picker(self) -> None:
        """Show/hide the emoji picker popup."""
        if self.emoji_frame.winfo_ismapped():
            self.emoji_frame.place_forget()
        else:
            self.emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-150)

    # --------------------------------------------------------------------- #
    #   Message sending
    # --------------------------------------------------------------------- #
    def _on_send_message(self, event: Any = None) -> None:
        """Collect text from the entry field and dispatch via chat manager."""
        raw = self.message_entry.get().strip()
        if not raw:
            return

        # Convert any emoji shortcodes entered manually to real Unicode
        processed = self._emoji_manager.replace_shortcodes_with_emoji(raw)

        # Forward to the network layer (if available)
        if hasattr(self.app_controller, "chat_manager") and getattr(self.app_controller.chat_manager, "send_message", None):
            # The `send_message` method expects only the content; metadata could be added later.
            self.app_controller.chat_manager.send_message(processed)
        else:
            # Local fallback – useful during development or when network isn't ready.
            self.logger.warning("Chat manager not ready – falling back to local display.")
            # Import here to avoid circular imports
            try:
                from chat.message import ChatMessage
                msg = ChatMessage(sender=self.username, content=processed)
                self._display_message(msg)
            except ImportError:
                self.logger.error("Could not import ChatMessage for local fallback")

        # Clear entry and reset focus
        self.message_entry.delete(0, "end")
        self.message_entry.focus_set()

    # --------------------------------------------------------------------- #
    #   Receiving & displaying messages
    # --------------------------------------------------------------------- #
    def display_remote_message(self, sender: str, content: str) -> None:
        """Public method – call from outside to add a remote message."""
        try:
            from chat.message import ChatMessage
            msg = ChatMessage(sender=sender, content=content)
            self._display_message(msg)
        except ImportError:
            self.logger.error("Could not import ChatMessage for displaying remote message")

    def _display_message(self, message: Any) -> None:
        """Render a message inside the scrolling area."""
        # Frame that holds the message UI
        msg_frame = ctk.CTkFrame(
            self.scrollable_messages,
            fg_color=("gray25", "gray30"),
            corner_radius=6,
            border_width=1,
            border_color=("#444444", "#222222"),
        )
        msg_frame.pack(fill="x", padx=5, pady=3)

        # Timestamp -------------------------------------------------------- #
        time_str = message.timestamp.strftime("%H:%M") if hasattr(message, 'timestamp') else "00:00"
        sender_label = ctk.CTkLabel(
            msg_frame,
            text=f"{getattr(message, 'sender', 'Unknown')} ({time_str})",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#D0D0D0",
            anchor="w",
        )
        sender_label.pack(padx=8, pady=(6, 1))

        # Content ---------------------------------------------------------- #
        content_text = getattr(message, 'content', str(message))
        content_label = ctk.CTkLabel(
            msg_frame,
            text=content_text,
            font=ctk.CTkFont(size=14),
            justify="left",
            wraplength=380,
            anchor="w",
            text_color="#E0E0E0",
        )
        content_label.pack(padx=8, pady=(1, 6))

        # Auto-scroll to bottom ------------------------------------------------ #
        try:
            # Force update and scroll to bottom
            self.update_idletasks()
            # Try to access the canvas through the scrollable frame's internal structure
            if hasattr(self.scrollable_messages, '_parent_canvas'):
                self.scrollable_messages._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass  # Silently fail if auto-scroll isn't supported

    # --------------------------------------------------------------------- #
    #   Connection status helpers
    # --------------------------------------------------------------------- #
    def set_connection_status(self, connected: bool) -> None:
        """Update UI to reflect connection state."""
        self._is_connected = connected
        colour = "green" if connected else "red"
        self.status_label.configure(text="Connected" if connected else "Disconnected", text_color=colour)

    # --------------------------------------------------------------------- #
    #   Notification handling
    # --------------------------------------------------------------------- #
    def show_notification(self, text: str, duration: int = 3000) -> None:
        """Display a transient top-of-page banner."""
        self.notification_frame.configure(fg_color="#FFB74D")
        self.notification_frame.place(relx=0.5, rely=0.0, anchor="n", y=10)
        lbl = ctk.CTkLabel(
            self.notification_frame,
            text=text,
            fg_color="#FFB74D",
            corner_radius=6,
            padx=12,
            pady=6,
        )
        lbl.pack()
        # Auto-hide after `duration` ms
        self.after(duration, lambda: self.notification_frame.place_forget())

    # --------------------------------------------------------------------- #
    #   File attachment placeholder (Phase 6 ready)
    # --------------------------------------------------------------------- #
    def _open_file_dialog(self) -> None:
        """Open a file picker - currently just a stub for future implementation."""
        try:
            from tkinter import filedialog

            path = filedialog.askopenfilename(
                title="Select a file to send",
                filetypes=[("All files", "*.*"), ("Images", "*.png;*.jpg;*.jpeg;*.gif")],
            )
            if path:
                self.logger.debug(f"User selected attachment: {path}")
                # Future: construct an attachment packet and send it via chat_manager
                self.message_entry.insert(
                    "end",
                    f" (📎 {os.path.basename(path)}) ",
                )
        except Exception as exc:
            self.logger.error(f"Attachment dialog error: {exc}")

    # --------------------------------------------------------------------- #
    #   Misc UI callbacks
    # --------------------------------------------------------------------- #
    def clear_history(self) -> None:
        """Erase local message history and UI."""
        self._history_manager.clear()
        for widget in self.scrollable_messages._root.winfo_children():
            widget.destroy()