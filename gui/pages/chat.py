"""
=================================================================================
RemoteDesk Pro
File: gui/pages/chat.py
WhatsApp/Telegram-like chat interface with emoji picker and file attachment
=================================================================================
"""

from __future__ import annotations

from typing import Optional
import os
import tkinter.filedialog as filedialog
from datetime import datetime
import re

import customtkinter as ctk
import emoji
from PIL import Image, ImageDraw, ImageFont

from core.logger import get_logger

logger = get_logger()

# Icons directory
ICON_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")
)
WINDOWS_EMOJI_FONT_PATH = r"C:\Windows\Fonts\seguiemj.ttf"

EMOJI_FONT_FAMILY = "Segoe UI Emoji"
EMOJI_COLUMNS = 6
EMOJI_CHOICES = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰",
    "😘", "😗", "😋", "😜", "🤪", "😝", "🤗", "🤔", "🤨", "😐", "😶", "🙄", "😏", "😴", "😪", "😎",
    "🥳", "😭", "😤", "😡", "🤯", "😱", "🥵", "🥶", "😳", "🤓", "🧐", "😈", "👍", "👎", "👌", "🤝",
    "✌️", "🤞", "👏", "🙌", "💪", "🔥", "💯", "✨", "⭐", "🌟", "💡", "❤️", "🧡", "💛", "💚", "💙",
    "💜", "🖤", "💔", "💕", "💖", "💗", "💓", "💞", "💘", "💝", "🌹", "🌺", "🌸", "🎉", "🎊", "🎁",
    "📱", "💻", "⌨️", "🖥️", "📷", "🎥", "📁", "📂", "🗂️", "📝", "📄", "📦", "🚀", "⚡", "☕", "🍕",
]


def load_icon(icon_name: str, size: tuple = (24, 24)) -> Optional[Image.Image]:
    icon_path = os.path.join(ICON_DIR, icon_name)
    if os.path.exists(icon_path):
        return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
    return None


def get_emoji_font(size: int, weight: str = "normal") -> ctk.CTkFont:
    """Return a font that can render Windows color emoji glyphs."""
    return ctk.CTkFont(family=EMOJI_FONT_FAMILY, size=size, weight=weight)


def load_emoji_pil(emoji_char: str, size: int = 28) -> Optional[Image.Image]:
    """Render a color emoji into a transparent image when supported by Pillow."""
    if not os.path.exists(WINDOWS_EMOJI_FONT_PATH):
        return None

    canvas_size = int(size * 2.2)
    padding = max(6, size // 3)
    try:
        font = ImageFont.truetype(WINDOWS_EMOJI_FONT_PATH, size)
        image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox((0, 0), emoji_char, font=font, embedded_color=True)
        x = (canvas_size - (bbox[2] - bbox[0])) // 2 - bbox[0]
        y = (canvas_size - (bbox[3] - bbox[1])) // 2 - bbox[1]
        draw.text((x, y), emoji_char, font=font, embedded_color=True)

        content_box = image.getbbox()
        if content_box is None:
            return image

        cropped = image.crop(content_box)
        result = Image.new(
            "RGBA",
            (cropped.width + padding * 2, cropped.height + padding * 2),
            (0, 0, 0, 0),
        )
        result.paste(cropped, (padding, padding))
        return result
    except Exception as exc:
        logger.debug(f"Failed to render emoji image for {emoji_char!r}: {exc}")
        return None


def extract_emojis(text: str) -> list[str]:
    """Return the emoji graphemes found in a string."""
    return [item["emoji"] for item in emoji.emoji_list(text)]


def is_emoji_only_text(text: str) -> bool:
    """Check whether a message contains only emoji and whitespace."""
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return False
    emoji_chars = "".join(extract_emojis(compact))
    return compact == emoji_chars


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
        self._emoji_image_cache: dict[tuple[str, int], ctk.CTkImage] = {}
        self._create_widgets()

    def _get_emoji_image(self, emoji_char: str, size: int = 28) -> Optional[ctk.CTkImage]:
        """Cache rendered emoji images so picker and bubbles stay fast."""
        cache_key = (emoji_char, size)
        if cache_key in self._emoji_image_cache:
            return self._emoji_image_cache[cache_key]

        emoji_pil = load_emoji_pil(emoji_char, size=size)
        if emoji_pil is None:
            return None

        ctk_image = ctk.CTkImage(light_image=emoji_pil, dark_image=emoji_pil, size=emoji_pil.size)
        self._emoji_image_cache[cache_key] = ctk_image
        return ctk_image

    def _create_widgets(self):
        """Create the chat interface layout."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color=("#0084FF", "#1E1E1E"),
            corner_radius=0,
            height=60,
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        chat_icon = load_icon("chat.png", size=(24, 24))
        if chat_icon:
            chat_img = ctk.CTkImage(light_image=chat_icon, dark_image=chat_icon, size=(24, 24))
            avatar = ctk.CTkLabel(header_frame, image=chat_img, text="")
        else:
            avatar = ctk.CTkLabel(header_frame, text="💬", font=get_emoji_font(24))
        avatar.pack(side="left", padx=(20, 10), pady=10)

        header_label = ctk.CTkLabel(
            header_frame,
            text="Chat",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF",
        )
        header_label.pack(side="left", pady=15)

        chat_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        chat_container.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        self.conversation_area = ctk.CTkScrollableFrame(
            chat_container,
            fg_color=("#F0F2F5", "#0B141A"),
            corner_radius=10,
        )
        self.conversation_area.pack(fill="both", expand=True)

        input_frame = ctk.CTkFrame(
            main_frame,
            fg_color=("#FFFFFF", "#1F2C34"),
            corner_radius=0,
            height=70,
        )
        input_frame.pack(fill="x", side="bottom")
        input_frame.pack_propagate(False)

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
                hover_color=("#E3E3E3", "#2A3942"),
            )
        else:
            self.attach_btn = ctk.CTkButton(
                input_frame,
                text="📎",
                command=self._open_file_dialog,
                width=44,
                height=44,
                corner_radius=22,
                font=get_emoji_font(20),
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942"),
            )
        self.attach_btn.pack(side="left", padx=(15, 5), pady=13)

        self.msg_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message",
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=22,
            border_width=0,
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(5, 10), pady=13)
        self.msg_entry.bind("<Return>", self._send_message)

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
                hover_color=("#E3E3E3", "#2A3942"),
            )
        else:
            self.emoji_btn = ctk.CTkButton(
                input_frame,
                text="😊",
                command=self._toggle_emoji_picker,
                width=44,
                height=44,
                corner_radius=22,
                font=get_emoji_font(20),
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942"),
            )
        self.emoji_btn.pack(side="left", padx=5, pady=13)

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
                hover_color=("#0073E6", "#0073E6"),
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
                hover_color=("#0073E6", "#0073E6"),
            )
        self.send_btn.pack(side="right", padx=(5, 15), pady=13)

        self.emoji_frame = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", "#1F2C34"),
            corner_radius=15,
            width=360,
            height=240,
            border_width=1,
            border_color=("#E0E0E0", "#2A3942"),
        )
        self.emoji_frame.place_forget()

        self._create_emoji_picker()

    def _create_emoji_picker(self):
        """Create the emoji picker panel with real colorful emojis."""
        header = ctk.CTkLabel(
            self.emoji_frame,
            text="Emojis",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#666666", "#AAAAAA"),
        )
        header.pack(pady=(10, 5))

        emoji_scroll = ctk.CTkScrollableFrame(
            self.emoji_frame,
            fg_color="transparent",
            height=180,
            width=340,
        )
        emoji_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        for column in range(EMOJI_COLUMNS):
            emoji_scroll.grid_columnconfigure(column, weight=1, uniform="emoji")

        for i, emo in enumerate(EMOJI_CHOICES):
            row = i // EMOJI_COLUMNS
            column = i % EMOJI_COLUMNS
            emoji_image = self._get_emoji_image(emo, size=24)
            btn = ctk.CTkButton(
                emoji_scroll,
                text="" if emoji_image else emo,
                image=emoji_image,
                font=get_emoji_font(20),
                width=44,
                height=44,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("#E3E3E3", "#2A3942"),
                command=lambda e=emo: self._add_emoji(e),
            )
            btn.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")

    def _toggle_emoji_picker(self):
        """Toggle the emoji picker as a popup above the input bar, inside chat panel."""
        if self.emoji_visible:
            self.emoji_frame.place_forget()
        else:
            self.emoji_frame.place(relx=0.02, rely=0.98, anchor="sw")
        self.emoji_visible = not self.emoji_visible

    def _add_emoji(self, emo: str):
        """Add selected emoji to message input."""
        self.msg_entry.insert("end", emo)

    def _open_file_dialog(self):
        """Open file selection dialog and send file as attachment."""
        filetypes = [
            ("All files", "*.*"),
            ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("Documents", "*.pdf *.doc *.docx *.txt"),
            ("Videos", "*.mp4 *.avi *.mkv *.mov"),
        ]
        filepath = filedialog.askopenfilename(title="Select file", filetypes=filetypes)
        if filepath:
            filename = os.path.basename(filepath)
            self._add_message(f"📎 {filename}", is_outgoing=True, attachment=filepath)

    def _add_message(self, text: str, is_outgoing: bool = True, attachment: Optional[str] = None):
        """Add a message bubble to the conversation (WhatsApp/Telegram style)."""
        align_frame = ctk.CTkFrame(self.conversation_area, fg_color="transparent")
        align_frame.pack(fill="x", pady=4, padx=10, anchor="e" if is_outgoing else "w")

        bubble_color = ("#DCF8C6", "#005C4B") if is_outgoing else ("#E5E5E5", "#3A3A3A")
        bubble = ctk.CTkFrame(
            align_frame,
            fg_color=bubble_color,
            corner_radius=15,
            border_width=0,
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
            except Exception as exc:
                logger.error(f"Failed to load attachment: {exc}")
                file_label = ctk.CTkLabel(
                    bubble,
                    text=f"📄 {fname}",
                    font=get_emoji_font(13, weight="bold"),
                    text_color=("#000000", "#E9EDEF"),
                )
                file_label.pack(padx=12, pady=10)

        if text:
            display_text = emoji.emojize(text, language="alias")
            if is_emoji_only_text(display_text):
                emoji_row = ctk.CTkFrame(bubble, fg_color="transparent")
                emoji_row.pack(padx=12, pady=(10, 4), anchor="w")
                for emoji_char in extract_emojis(display_text):
                    emoji_image = self._get_emoji_image(emoji_char, size=26)
                    if emoji_image:
                        emoji_label = ctk.CTkLabel(emoji_row, text="", image=emoji_image)
                        emoji_label.pack(side="left", padx=1)
                    else:
                        emoji_label = ctk.CTkLabel(
                            emoji_row,
                            text=emoji_char,
                            font=get_emoji_font(20),
                            text_color=("#000000", "#E9EDEF"),
                        )
                        emoji_label.pack(side="left", padx=1)
            else:
                msg_label = ctk.CTkLabel(
                    bubble,
                    text=display_text,
                    font=get_emoji_font(13),
                    text_color=("#000000", "#E9EDEF"),
                    wraplength=280,
                    justify="left",
                )
                msg_label.pack(padx=12, pady=(8, 2))

        time_str = datetime.now().strftime("%H:%M")
        meta = ctk.CTkFrame(bubble, fg_color="transparent")
        meta.pack(padx=12, pady=(0, 6), anchor="e")

        time_label = ctk.CTkLabel(
            meta,
            text=time_str,
            font=ctk.CTkFont(size=9),
            text_color=("#888888", "#8696A0"),
        )
        time_label.pack(side="left", padx=(0, 4))

        if is_outgoing:
            status = ctk.CTkLabel(
                meta,
                text="✓✓",
                font=ctk.CTkFont(size=10),
                text_color=("#34B7F1", "#53BDEB"),
            )
            status.pack(side="left")

        self.conversation_area._parent_canvas.yview_moveto(1.0)

    def _send_message(self, event=None):
        """Send a chat message."""
        text = self.msg_entry.get().strip()
        if not text:
            return
        self.msg_entry.delete(0, ctk.END)
        self._add_message(text, is_outgoing=True)
