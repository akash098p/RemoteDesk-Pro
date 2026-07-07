
from typing import Any, List

import customtkinter as ctk
from core.logger import get_logger
from chat.message import ChatMessage
from chat.emoji import EmojiManager
from chat.history import ChatHistoryManager

# Assuming chat_manager and connection_manager will be injected or available from app.py
# For now, we'll initialize locally but this will be refactored when integrated with main app.

class ChatPage(ctk.CTkFrame):
    """
    GUI page for chat functionality, including message history, input,
    emoji picker, and attachment buttons.
    """
    def __init__(self, parent: ctk.CTk, app_controller: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = get_logger()
        self.app_controller = app_controller  # Reference to main app controller (holds chat_manager, etc.)
        self._username = getattr(app_controller, "username", "Local")

        # Initialize local components for display/tests until app_controller.chat_manager is set
        self.emoji_manager = EmojiManager()
        self.chat_history_manager = ChatHistoryManager()

        # Configuration
        self.MESSAGE_HEIGHT = 60  # Approximate height per message row
        self.MAX_VISIBLE_MESSAGES = 15

        # GUI Layout
        self._create_widgets()
        self._setup_layout()
        self._style_widgets()

        self.logger.info("ChatPage initialized.")

    def _create_widgets(self) -> None:
        """Creates all internal GUI widgets."""
        # Header
        self.header_frame = ctk.CTkFrame(self, height=50)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Chat",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Disconnected",
            font=ctk.CTkFont(size=12),
            text_color="red",
            anchor="e"
        )
        self.status_label.pack(side="right", padx=10, pady=10)

        # Main Content Area: Message History + Input Area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Message History Scrollable Frame
        self.messages_frame_container = ctk.CTkScrollableFrame(
            self.content_frame,
            label_text="Messages",
            label_fg_color=("gray75", "gray25"),
            fg_color=("gray90", "gray20")
        )
        self.messages_frame_container.pack(side="left", fill="both", expand=True)

        # Input Area
        self.input_frame = ctk.CTkFrame(self.content_frame)
        self.input_frame.pack(side="bottom", fill="x", pady=(5, 10))

        # Emoji Picker Button
        self.emoji_button = ctk.CTkButton(
            self.input_frame,
            text="😊",
            width=40,
            command=self._toggle_emoji_picker,
        )
        self.emoji_button.pack(side="left", padx=5, pady=5)

        # Attachment Button
        self.attachment_button = ctk.CTkButton(
            self.input_frame,
            text="📎",
            width=40,
            command=self._open_file_dialog,
        )
        self.attachment_button.pack(side="left", padx=5, pady=5)

        # Message Input Entry
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type a message...",
            height=40
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.message_entry.bind("<Return>", self._on_send_message)

        # Send Button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            width=80,
            command=self._on_send_message,
            fg_color=("#3B82F6", "#2563EB"),
            hover_color=("#2563EB", "#1D4ED8")
        )
        self.send_button.pack(side="right", padx=5, pady=5)

        # Emoji Picker Frame (hidden by default)
        self.emoji_frame = ctk.CTkFrame(self, fg_color=("white", "gray30"))
        self.emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-150) # Positioned below input area
        self.emoji_frame.place_forget()  # Initially hidden
        self._create_emoji_grid()

        # Notification widget for showing system messages (like connected/disconnected)
        self.notification_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.notification_frame.place(relx=0.5, rely=0.0, anchor="n", y=10)
        self.notification_frame.place_forget()

    def _setup_layout(self) -> None:
        """Configures the layout weights."""
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _style_widgets(self) -> None:
        """Applies consistent styling to widgets."""
        # Apply theme-aware styles if needed
        self.configure(fg_color=("gray95", "gray15"))
        self.header_frame.configure(fg_color=("gray90", "gray25"))
        self.input_frame.configure(fg_color=("gray95", "gray18"))

    def _create_emoji_grid(self) -> None:
        """Creates the emoji selection grid."""
        emojis = self.emoji_manager.get_emoji_shortcodes()
        # Simplified grid: row by row
        row = 0
        col = 0
        for shortcode in emojis:
            emoji_char = self.emoji_manager.emoji_map.get(shortcode, shortcode)
            btn = ctk.CTkButton(
                self.emoji_frame,
                text=emoji_char,
                width=40,
                height=30,
                command=lambda s=shortcode: self._insert_emoji(s)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 8: # 9 columns
                col = 0
                row += 1

    def _toggle_emoji_picker(self) -> None:
        """Toggles visibility of the emoji picker frame."""
        if self.emoji_frame.winfo_ismapped():
            self.emoji_frame.place_forget()
        else:
            self.emoji_frame.place(relx=0.5, rely=1.0, anchor="s", y=-150)

    def _insert_emoji(self, shortcode: str) -> None:
        """Inserts the selected emoji into the message entry."""
        emoji_char = self.emoji_manager.emoji_map.get(shortcode, shortcode)
        current_text = self.message_entry.get()
        self.message_entry.delete(0, "end")
        self.message_entry.insert(0, current_text + emoji_char)
        self._toggle_emoji_picker()

    def _open_file_dialog(self) -> None:
        """Opens file dialog to select an attachment (placeholder)."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if file_path:
            # For now, just append file name to message or show a notification
            self.logger.debug(f"Selected attachment: {file_path}")
            self.message_entry.insert("end", f" (attached: {file_path.split('/')[-1]}) ")

    def _on_send_message(self, event: Any = None) -> None:
        """
        Handles sending the message.
        This will be connected to app_controller.chat_manager.send_message()
        """
        content = self.message_entry.get().strip()
        if not content:
            return

        # Pre-process content: Replace emoji shortcodes
        content = self.emoji_manager.replace_shortcodes_with_emoji(content)

        # Send via app controller (which will use ChatManager)
        if self.app_controller and hasattr(self.app_controller, 'send_chat_message'):
            self.app_controller.send_chat_message(content)
        else:
            # Fallback to local component if not integrated yet
            self.logger.warning("App controller not fully set up. Using local ChatHistoryManager.")
            msg = ChatMessage(sender=getattr(self, '_username', 'Local'), content=content)
            self.chat_history_manager.add_message(msg)
            self._display_message(msg)

        self.message_entry.delete(0, "end")

    def update_message_display(self, message: ChatMessage) -> None:
        """
        Adds a message to the display.
        """
        self.chat_history_manager.add_message(message)
        self._display_message(message)

    def _display_message(self, message: ChatMessage) -> None:
        """
        Renders a message in the messages frame.
        """
        # Create a message frame
        msg_frame = ctk.CTkFrame(
            self.messages_frame_container,
            fg_color=("white", "gray25"),
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray40")
        )
        msg_frame.pack(fill="x", padx=10, pady=5)

        # Sender and Timestamp
        time_str = message.timestamp.strftime("%H:%M")
        sender_label = ctk.CTkLabel(
            msg_frame,
            text=f"{message.sender} ({time_str})",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
            fg_color="transparent"
        )
        sender_label.pack(fill="x", padx=10, pady=(5, 0))

        # Content (handle emoji rendering if stored as shortcode, else plain)
        # This is a simplified display; a real app would have advanced text wrapping.
        content_label = ctk.CTkLabel(
            msg_frame,
            text=message.content,
            font=ctk.CTkFont(size=14),
            anchor="w",
            justify="left",
            wraplength=400  # Fixed width for wrapping
        )
        content_label.pack(fill="x", padx=10, pady=(0, 5))

    def set_connection_status(self, is_connected: bool) -> None:
        """
        Updates the connection status label.
        """
        if is_connected:
            self.status_label.configure(text="Connected", text_color="green")
        else:
            self.status_label.configure(text="Disconnected", text_color="red")

    def show_notification(self, message: str, duration: int = 3000) -> None:
        """
        Displays a temporary notification at the top of the page.
        """
        self.notification_frame.place_forget()
        notification_label = ctk.CTkLabel(
            self.notification_frame,
            text=message,
            fg_color="orange",
            corner_radius=8,
            padx=15,
            pady=8
        )
        notification_label.pack()

        self.notification_frame.place(relx=0.5, rely=0.0, anchor="n", y=10)
        self.after(duration, lambda: self.notification_frame.place_forget())

    def clear_history(self) -> None:
        """Clears all message history from display."""
        for widget in self.messages_frame_container.winfo_children():
            widget.destroy()


# External dependencies for types
from typing import Any
