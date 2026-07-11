"""
=================================================================================
RemoteDesk Pro
File: gui/pages/chat.py
WhatsApp/Telegram-like chat interface with emoji picker and file attachment
=================================================================================
"""

from __future__ import annotations

from typing import Callable, Optional
import os
import tkinter.filedialog as filedialog
from datetime import datetime

import customtkinter as ctk
import emoji
from PIL import Image

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger

logger = get_logger()

# Icons directory
ICON_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons')
)

def load_icon(icon_name: str, size: tuple = (24, 24)) -> Optional[Image.Image]:
    icon_path = os.path.join(ICON_DIR, icon_name)
    if os.path.exists(icon_path):
        return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
    return None


class ChatPage(ctk.CTkFrame):
    """
    Modern chat interface with WhatsApp/Telegram-like design:
    - Message bubbles with timestamps
    - Emoji picker with real colorful emojis
    - File attachment with original aspect ratio
    - Smooth scrolling
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.emoji_visible = False
        self._create_widgets()

    def _create_widgets(self):
        """Create the chat interface layout"""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Header with chat icon
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color=("#0084FF", "#1E1E1E"),
            corner_radius=0,
            height=60
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        chat_icon = load_icon("chat.png", size=(24, 24))
        if chat_icon:
            chat_img = ctk.CTkImage(light_image=chat_icon, dark_image=chat_icon, size=(24, 24))
            avatar = ctk.CTkLabel(header_frame, image=chat_img, text="")
        else:
            avatar = ctk.CTkLabel(header_frame, text="💬", font=ctk.CTkFont(size=24))
        avatar.pack(side="left", padx=(20, 10), pady=10)

        header_label = ctk.CTkLabel(
            header_frame,
            text="Chat",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        header_label.pack(side="left", pady=15)

        # Conversation area with scrollbar
        chat_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        self.conversation_area = ctk.CTkScrollableFrame(
            chat_container,
            fg_color=("#F0F2F5", "#0B141A"),
            corner_radius=10
        )
        self.conversation_area.pack(fill="both", expand=True)

        # Input area (bottom bar)
        input_frame = ctk.CTkFrame(
            main_frame,
            fg_color=("#FFFFFF", "#1F2C34"),
            corner_radius=0,
            height=70
        )
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)

        # Attachment button
        attach_icon = load_icon("attach.png", size=(24, 24))
        if attach_icon:
            attach_img = ctk.CTkImage(light_image=attach_icon, dark_image=attach_icon, size=(24, 24))
            self.attach_btn = ctk.CTkButton(
                input_frame,
                image=attach_img,
                text="",
                command=self._open_file_dialog,
                width=44,
                height=44,
                corner_radius=22,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942")
            )
        else:
            self.attach_btn = ctk.CTkButton(
                input_frame,
                text="📎",
                command=self._open_file_dialog,
                width=44,
                height=44,
                corner_radius=22,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942")
            )
        self.attach_btn.pack(side="left", padx=(15, 5), pady=13)

        # Message entry
        self.msg_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message",
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=22,
            border_width=0
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=13)
        self.msg_entry.bind("<Return>", self._send_message)

        # Emoji button
        emoji_icon = load_icon("smile-plus.png", size=(24, 24))
        if emoji_icon:
            emoji_img = ctk.CTkImage(light_image=emoji_icon, dark_image=emoji_icon, size=(24, 24))
            self.emoji_btn = ctk.CTkButton(
                input_frame,
                image=emoji_img,
                text="",
                command=self._toggle_emoji_picker,
                width=44,
                height=44,
                corner_radius=22,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942")
            )
        else:
            self.emoji_btn = ctk.CTkButton(
                input_frame,
                text="😊",
                command=self._toggle_emoji_picker,
                width=44,
                height=44,
                corner_radius=22,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942")
            )
        self.emoji_btn.pack(side="left", padx=5, pady=13)

        # Send button
        send_icon = load_icon("send.png", size=(24, 24))
        if send_icon:
            send_img = ctk.CTkImage(light_image=send_icon, dark_image=send_icon, size=(24, 24))
            self.send_btn = ctk.CTkButton(
                input_frame,
                image=send_img,
                text="",
                command=self._send_message,
                width=44,
                height=44,
                corner_radius=22,
                fg_color=("#0084FF", "#0084FF"),
                hover_color=("#0073E6", "#0073E6")
            )
        else:
            self.send_btn = ctk.CTkButton(
                input_frame,
                text="➤",
                command=self._send_message,
                width=44,
                height=44,
                corner_radius=22,
                fg_color=("#0084FF", "#0084FF"),
                hover_color=("#0073E6", "#0073E6")
            )
        self.send_btn.pack(side="right", padx=(5, 15), pady=13)

        # Emoji picker (hidden by default) - placed as overlay over chat panel
        self.emoji_frame = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", "#1F2C34"),
            corner_radius=15,
            width=360,
            height=240,
            border_width=1,
            border_color=("#E0E0E0", "#2A3942")
        )
        self.emoji_frame.place_forget()

        # Emoji picker
        self._create_emoji_picker()

    def _create_emoji_picker(self):
        """Create the emoji picker panel with real colorful emojis"""
        header = ctk.CTkLabel(
            self.emoji_frame,
            text="Emojis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#666666", "#AAAAAA")
        )
        header.pack(pady=(10, 5))

        emoji_scroll = ctk.CTkScrollableFrame(
            self.emoji_frame,
            fg_color="transparent",
            height=180,
            width=340
        )
        emoji_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        emojis = [
            "😀","😃","😄","😁","😆","😅","😂","🤣","😊","😇","🙂","🙃","😉","😌","😍","🥰",
            "😘","😗","😋","😜","🤪","😝","🤗","🤔","🤨","😐","😶","🙄","😏","😴","😪","😎",
            "🥳","😭","😤","😡","🤯","😱","🥵","🥶","😳","🤓","🧐","😈","👍","👎","👌","🤝",
            "✌️","🤞","👏","🙌","💪","🔥","💯","✨","⭐","🌟","💡","❤️","🧡","💛","💚","💙",
            "💜","🖤","💔","💕","💖","💗","💓","💞","💘","💝","🌹","🌺","🌸","🎉","🎊","🎁",
            "📱","💻","⌨️","🖥️","📷","🎥","📁","📂","🗂️","📝","📄","📦","🚀","⚡","☕","🍕"
        ]

        row_frame = None
        for i, emo in enumerate(emojis):
            if i % 8 == 0:
                row_frame = ctk.CTkFrame(emoji_scroll, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
            btn = ctk.CTkButton(
                row_frame,
                text=emo,
                font=ctk.CTkFont(size=20),
                width=36,
                height=36,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942"),
                command=lambda e=emo: self._add_emoji(e)
            )
            btn.pack(side="left", padx=2, pady=2)

    def _toggle_emoji_picker(self):
        """Toggle the emoji picker as a popup above the input bar, inside chat panel."""
        if self.emoji_visible:
            self.emoji_frame.place_forget()
        else:
            # Position near bottom-left, above the input bar
            self.emoji_frame.place(relx=0.02, rely=0.98, anchor="sw")
        self.emoji_visible = not self.emoji_visible

    def _add_emoji(self, emo: str):
        """Add selected emoji to message input"""
        self.msg_entry.insert("end", emo)

    def _open_file_dialog(self):
        """Open file selection dialog and send file as attachment"""
        filetypes = [
            ("All files", "*.*"),
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Documents", "*.pdf *.doc *.docx *.txt"),
            ("Videos", "*.mp4 *.avi *.mkv *.mov")
        ]
        filepath = filedialog.askopenfilename(title="Select file", filetypes=filetypes)
        if filepath:
            filename = os.path.basename(filepath)
            self._add_message(f"📎 {filename}", is_outgoing=True, attachment=filepath)

    def _add_message(self, text: str, is_outgoing: bool = True, attachment: Optional[str] = None):
        """Add a message bubble to the conversation (WhatsApp/Telegram style)"""
        align_frame = ctk.CTkFrame(self.conversation_area, fg_color="transparent")
        align_frame.pack(fill="x", pady=4, padx=10, anchor="e" if is_outgoing else "w")

        bubble_color = ("#DCF8C6", "#005C4B") if is_outgoing else ("#E5E5E5", "#3A3A3A")
        bubble = ctk.CTkFrame(
            align_frame,
            fg_color=bubble_color,
            corner_radius=15,
            border_width=0
        )
        bubble.pack(side="right" if is_outgoing else "left")

        if attachment:
            fname = os.path.basename(attachment)
            try:
                img = Image.open(attachment)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                img_label = ctk.CTkLabel(bubble, image=photo, text="")
                img_label.image = photo
                img_label.pack(padx=10, pady=10)
            except Exception as e:
                logger.error(f"Failed to load attachment: {e}")
                file_label = ctk.CTkLabel(
                    bubble,
                    text=f"📄 {fname}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=("#000000", "#E9EDEF")
                )
                file_label.pack(padx=12, pady=10)

        if text:
            display_text = emoji.emojize(text, language='alias')
            msg_label = ctk.CTkLabel(
                bubble,
                text=display_text,
                font=ctk.CTkFont(size=13),
                text_color=("#000000", "#E9EDEF"),
                wraplength=280,
                justify="left"
            )
            msg_label.pack(padx=12, pady=(8, 2))

        time_str = datetime.now().strftime("%H:%M")
        meta = ctk.CTkFrame(bubble, fg_color="transparent")
        meta.pack(padx=12, pady=(0, 6), anchor="e")

        time_label = ctk.CTkLabel(
            meta,
            text=time_str,
            font=ctk.CTkFont(size=9),
            text_color=("#888888", "#8696A0")
        )
        time_label.pack(side="left", padx=(0, 4))

        if is_outgoing:
            status = ctk.CTkLabel(
                meta,
                text="✓✓",
                font=ctk.CTkFont(size=10),
                text_color=("#34B7F1", "#53BDEB")
            )
            status.pack(side="left")

        self.conversation_area._parent_canvas.yview_moveto(1.0)

    def _send_message(self, event=None):
        """Send a chat message"""
        text = self.msg_entry.get().strip()
        if not text:
            return
        self.msg_entry.delete(0, ctk.END)
        self._add_message(text, is_outgoing=True)
