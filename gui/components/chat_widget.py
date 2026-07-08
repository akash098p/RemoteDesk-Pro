"""
===============================================================================𝐂𝐇𝐀𝐓 𝐌𝐎𝐃𝐔𝐋𝐄

File: gui/components/chat_widget.py

Custom chat widget for RemoteDesk Pro - Phase 5 Communication Module.
Provides a compact, reusable chat interface within applications.
===============================================================================
"""

from __future__ import annotations

import threading
from typing import Any, List, Optional

import customtkinter as ctk

from chat.message import ChatMessage
from chat.emoji import EmojiManager
from core.logger import get_logger

class ChatWidget(ctk.CTkFrame):
    """
    Compact chat widget for use in larger applications.

    Features:
    - Sending messages with Enter key
    - Emoji support (with picker)
    - Message history (limited buffer)
    - Attachment placeholder
    - Real-time message display
    """

    def __init__(
        self,
        parent: ctk.CTk | ctk.CTkFrame | ctk.CTkChild,
        username: str = "User",
        height: int = 300,
        width: int = 400,
        **kwargs,
    ) -> None:
        """
        Initialize the chat widget.

        Parameters
        ----------
        parent : ctk.CTk | ctk.CTkFrame | ctk.CTkChild
            Parent widget.
        username : str, optional
            Username to display in chat messages, by default "User".
        height : int, optional
            Height in pixels, by default 300.
        width : int, optional
            Width in pixels, by default 400.
        **kwargs : Any
            Additional keyword arguments for customtkinter.CTkFrame.
        """
        super().__init__(parent, height=height, width=width, **kwargs)
        self.logger = get_logger()
        self.username = username

        # --- State management --------------------------------------------- #
        self._messages: List[ChatMessage] = []
        self._emoji_manager = EmojiManager()
        self._is_connected = False

        # --- Thread control ----------------------------------------------- #
        self._receive_thread: Optional[threading.Thread] = None

        # --- GUI setup ----------------------------------------------------- #
        self._setup_ui()
        self.logger.info("ChatWidget initialized.")

    def _setup_ui(self) -> None:
        """Create the chat widget's user interface elements."""
        # Configure widget appearance
        self.configure(fg_color=("#1E1E1E", "#2A2A2A"), corner_radius=10)

        # Header section with title and connection status
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text="💬 Chat",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(side="left")

        self._status_label = ctk.CTkLabel(
            header_frame,
            text="Offline",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B",
            anchor="e",
        )
        self._status_label.pack(side="right")

        # Message display area
        self._messages_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Messages",
            label_fg_color=("#333333", "#444444"),
            fg_color=("#1A1A1A", "#262626"),
        )
        self._messages_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Input section
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Attachment button (placeholder for future)
        ctk.CTkButton(
            input_frame,
            text="📎",
            width=35,
            command=self._open_attachment_picker,
        ).pack(side="left", padx=(0, 8))

        # Message entry
        self._message_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message…",
            height=38,
            fg_color=("#2B2B2B", "#333333"),
        )
        self._message_entry.pack(side="left", fill="x", expand=True, padx=5)
        self._message_entry.bind("<Return>", self._on_send_message)

        # Send button
        ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            command=self._on_send_message,
            fg_color="#1E90FF",
            hover_color="#1C7ED6",
        ).pack(side="right", padx=(8, 0))

        # Emoji picker (hidden initially)
        self._emoji_frame = ctk.CTkFrame(self, fg_color="white")
        self._emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-160)
        self._emoji_frame.place_forget()
        self._populate_emoji_grid()

        # Emoji button
        ctk.CTkButton(
            self,
            text="😊",
            width=35,
            command=self._toggle_emoji_picker,
        ).place(relx=1.0, x=-15, y=-15, anchor="ne")

    def _populate_emoji_grid(self) -> None:
        """Populate the emoji picker grid with available emojis."""
        emojis = self._emoji_manager.get_emoji_shortcodes()
        row, col = 0, 0

        for shortcode in emojis:
            emoji_char = self._emoji_manager.emoji_map.get(shortcode, shortcode)
            ctk.CTkButton(
                self._emoji_frame,
                text=emoji_char,
                width=35,
                height=35,
                corner_radius=4,
                command=lambda s=shortcode: self._append_emoji(s),
            ).grid(row=row, column=col, padx=2, pady=2)

            col += 1
            if col > 7:  # Wrap after 8 columns
                col = 0
                row += 1

    def _append_emoji(self, shortcode: str) -> None:
        """Insert the selected emoji into the message entry field."""
        current = self._message_entry.get()
        self._message_entry.delete(0, "end")
        self._message_entry.insert(0, current + self._emoji_manager.emoji_map.get(shortcode, shortcode))

    def _toggle_emoji_picker(self) -> None:
        """Show or hide the emoji picker panel."""
        if self._emoji_frame.winfo_ismapped():
            self._emoji_frame.place_forget()
        else:
            self._emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-160)

    def _on_send_message(self, event: Any = None) -> None:
        """Handle sending a message from the input field."""
        content = self._message_entry.get().strip()
        if not content:
            return

        processed_content = self._emoji_manager.replace_shortcodes_with_emoji(content)

        # Create message object
        try:
            from chat.message import ChatMessage
            msg = ChatMessage(
                sender=self.username,
                content=processed_content,
            )
            self._display_message(msg)
            self.logger.debug(f"Message sent by {self.username}: {processed_content[:50]}")
        except ImportError:
            self.logger.error("ChatMessage not available for sending")
            return

        # Clear input
        self._message_entry.delete(0, "end")

    def _display_message(self, message: ChatMessage) -> None:
        """Render a chat message in the widget's message area."""
        self._messages.append(message)

        # Create message container
        msg_frame = ctk.CTkFrame(
            self._messages_frame,
            fg_color=("gray25", "gray30"),
            corner_radius=6,
        )
        msg_frame.pack(fill="x", padx=8, pady=4)

        # Sender and timestamp
        time_str = message.timestamp.strftime("%H:%M")
        header = ctk.CTkLabel(
            msg_frame,
            text=f"{message.sender} ({time_str})",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#E0E0E0",
            anchor="w",
        )
        header.pack(padx=8, pady=(6, 2))

        # Message content
        ctk.CTkLabel(
            msg_frame,
            text=message.content,
            font=ctk.CTkFont(size=14),
            wraplength=300,
            justify="left",
            text_color="#FFFFFF",
            anchor="w",
        ).pack(padx=8, pady=(2, 6))

        # Auto-scroll to bottom of messages
        try:
            self._messages_frame._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def set_connection_status(self, connected: bool) -> None:
        """Update the widget's connection status indicator."""
        self._is_connected = connected

        if connected:
            self._status_label.configure(text="Online", text_color="#4CAF50")
        else:
            self._status_label.configure(text="Offline", text_color="#FF6B6B")

    def open_with_app_controller(self, app_controller: Any) -> None:
        """Initialize this widget with a reference to the main app controller."""
        self.app_controller = app_controller

    # ------------------------------------------------------------------- #
    #   Placeholder functionality for Phase 6
    # ------------------------------------------------------------------- #
    def _open_attachment_picker(self) -> None:
        """Future implementation: open file picker for attachments."""
        self.logger.info("Attachment picker not yet implemented - Phase 6 feature.")
        self.show_notification("Attachment picker coming in Phase 6")

    def show_notification(self, text: str, duration: int = 3000) -> None:
        """Display a temporary notification within the widget."""
        # Simple notification overlay
        overlay = ctk.CTkFrame(self, fg_color="#FFB74D", bg_color="#FFB74D")
        overlay.place(relx=0.5, rely=0.0, anchor="n", y=10, relwidth=0.8, height=40)

        ctk.CTkLabel(
            overlay,
            text=text,
            fg_color="#FFB74D",
            bg_color="#FFB74D",
        ).pack(expand=True, fill="both")

        # Auto-hide
        self.after(duration, overlay.destroy)

    def load_message_history(self, history: List[ChatMessage]) -> None:
        """Load existing chat messages from a history list."""
        for msg in history:
            self._display_message(msg)

    def connect(self, receiver: Any) -> None:
        """
        Connect this chat widget to a network receiver.

        This method is called by ChatManager to start receiving messages
        from the network layer.
        """
        if self._receive_thread and self._receive_thread.is_alive():
            self.logger.warning("ChatWidget already connected to a receiver.")
            return

        self._receiver = receiver

        self._receive_thread = threading.Thread(
            target=self._receive_messages_loop,
            daemon=True,
        )
        self._receive_thread.start()

    def _receive_messages_loop(self) -> None:
        """
        Background thread that continuously checks for incoming messages
        from the network receiver (if any).
        """
        while getattr(self, "_is_connected", False):
            if hasattr(self, "_receiver") and hasattr(self._receiver, "receive_message"):
                try:
                    # Blocking call with timeout for graceful shutdown
                    message = self._receiver.receive_message()
                    if message:
                        self._display_message(message)
                except (ConnectionError, TimeoutError):
                    pass
            threading.Event().wait(1.0)  # Sleep for 1 second before checking again

    def stop(self) -> None:
        """Stop any background network threads and cleanup."""
        self._is_connected = False
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=2.0)

    # ------------------------------------------------------------------- #
    #   Static utility methods
    # ------------------------------------------------------------------- #
    @staticmethod
    def create_with_emojis(
        parent: ctk.CTk | ctk.CTkFrame,
        username: str = "User",
        title: str = "Chat",
        height: int = 300,
        width: int = 400,
        **kwargs,
    ) -> "ChatWidget":
        """
        Factory method that creates and returns a configured ChatWidget.

        Parameters
        ----------
        parent : ctk.CTk | ctk.CTkFrame
            The parent container.
        username : str, optional
            Username for the chat participant.
        title : str, optional
            Window title (not used by ChatWidget, but reserved for future).
        height : int, optional
            Height in pixels.
        width : int, optional
            Width in pixels.
        **kwargs : Any
            Additional arguments for ChatWidget constructor.

        Returns
        -------
        ChatWidget
            Configured chat widget instance.
        """
        return ChatWidget(parent, username, height, width, **kwargs)