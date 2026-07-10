"""
===============================================================================
RemoteDesk Pro
File: gui/pages/chat.py
Premium chat page with colorful emojis, timestamps, and modern UI
===============================================================================
"""

from __future__ import annotations

import customtkinter as ctk
import emoji
from datetime import datetime
from typing import Optional

class ChatPage(ctk.CTkFrame):
    """
    Premium chat page with colorful emojis, message bubbles, timestamps, and modern UI.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self._messages = []
        self._emoji_categories = {
            "Smileys": ["😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃", "😉", "😊", "😇", "🥰", "😍", "🤩"],
            "Animals": ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐔"],
            "Food": ["🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈", "🍒", "🍑", "🥭", "🍍", "🥝", "🍅"],
            "Activities": ["⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱", "🔮", "🏓", "🏸", "🏒", "🏑", "🏏"],
            "Travel": ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎️", "🚓", "🚑", "🚒", "🚐", "🛻", "🚚", "🚛", "🚜", "🛴", "🚲"]
        }
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the premium chat UI with glassmorphism styling"""
        # Main container with glass effect
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            header,
            text="Chat",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title.pack(side="left", padx=10)
        
        # Chat area - scrollable with glass effect
        chat_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        chat_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Scrollable conversation area
        self.conversation_area = ctk.CTkScrollableFrame(
            chat_frame,
            fg_color="transparent",
            label_text="Conversation",
            corner_radius=15
        )
        self.conversation_area.pack(fill="both", expand=True)
        
        # Input area with emoji picker
        input_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        input_frame.pack(fill="x")
        
        # Emoji picker button
        self.emoji_btn = ctk.CTkButton(
            input_frame,
            text="😊",
            width=45,
            height=45,
            corner_radius=22,
            font=ctk.CTkFont(size=20),
            command=self._toggle_emoji_picker
        )
        self.emoji_btn.pack(side="left", padx=(0, 10))
        
        # Message entry with glass styling
        self.msg_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type a message...",
            height=45,
            corner_radius=22,
            font=ctk.CTkFont(size=14),
            border_width=1,
            border_color=("#CCCCCC", "#444444")
        )
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self._send_message)
        
        # Send button
        send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=80,
            height=45,
            corner_radius=22,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._send_message
        )
        send_btn.pack(side="right")
        
        # Emoji picker (initially hidden)
        self._create_emoji_picker()
        self.emoji_picker_visible = False
    
    def _create_emoji_picker(self):
        """Create the emoji picker panel"""
        self.emoji_frame = ctk.CTkFrame(
            self, 
            fg_color=("#F5F5F5", "#2A2A2A"), 
            corner_radius=15,
            width=350,
            height=200
        )
        self.emoji_frame.place(in_=self.emoji_btn, relx=0, rely=1, x=0, y=5, anchor="nw")
        self.emoji_frame.lower()  # Start hidden
        
        # Category tabs
        tab_frame = ctk.CTkFrame(self.emoji_frame, fg_color="transparent")
        tab_frame.pack(fill="x", padx=10, pady=10)
        
        self.emoji_tabs = {}
        for i, category in enumerate(self._emoji_categories.keys()):
            btn = ctk.CTkButton(
                tab_frame,
                text=category,
                width=70,
                height=30,
                corner_radius=8,
                font=ctk.CTkFont(size=12),
                command=lambda c=category: self._show_emoji_category(c)
            )
            btn.pack(side="left", padx=2)
            self.emoji_tabs[category] = btn
        
        # Emoji grid
        self.emoji_grid = ctk.CTkScrollableFrame(self.emoji_frame, fg_color="transparent")
        self.emoji_grid.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Show first category by default
        if self._emoji_categories:
            self._show_emoji_category(list(self._emoji_categories.keys())[0])
    
    def _show_emoji_category(self, category: str):
        """Display emojis for a specific category"""
        # Clear existing emojis
        for widget in self.emoji_grid.winfo_children():
            widget.destroy()
        
        # Create emoji buttons
        emojis = self._emoji_categories[category]
        for i, emoji_char in enumerate(emojis):
            btn = ctk.CTkButton(
                self.emoji_grid,
                text=emoji_char,
                width=40,
                height=40,
                corner_radius=10,
                font=ctk.CTkFont(size=20),
                fg_color="transparent",
                hover_color=("#E0E0E0", "#444444"),
                command=lambda e=emoji_char: self._insert_emoji(e)
            )
            btn.grid(row=i // 7, column=i % 7, padx=2, pady=2)
    
    def _insert_emoji(self, emoji_char: str):
        """Insert emoji at cursor position"""
        current_text = self.msg_entry.get()
        cursor_pos = self.msg_entry.index(ctk.INSERT)
        new_text = current_text[:cursor_pos] + emoji_char + current_text[cursor_pos:]
        self.msg_entry.delete(0, ctk.END)
        self.msg_entry.insert(0, new_text)
    
    def _toggle_emoji_picker(self):
        """Show/hide emoji picker"""
        self.emoji_picker_visible = not self.emoji_picker_visible
        if self.emoji_picker_visible:
            self.emoji_frame.lift()
        else:
            self.emoji_frame.lower()
    
    def _send_message(self, event=None):
        """Send a chat message"""
        text = self.msg_entry.get().strip()
        if not text:
            return
        
        self.msg_entry.delete(0, ctk.END)
        
        # Add message to conversation
        self._add_message(text, is_outgoing=True)
        
        # Simulate incoming response (replace with actual network call)
        self.after(1000, lambda: self._add_message(f"Echo: {text}", is_outgoing=False))
    
    def _add_message(self, text: str, is_outgoing: bool = True):
        """Add a message bubble to the conversation"""
        # Create message container
        msg_frame = ctk.CTkFrame(
            self.conversation_area,
            fg_color=("#0078D7", "#2A2A2A") if is_outgoing else ("#E5E5E5", "#3A3A3A"),
            corner_radius=18
        )
        
        # Message bubble
        bubble = ctk.CTkFrame(msg_frame, fg_color="transparent")
        bubble.pack(padx=15, pady=8)
        
        # Time stamp
        time_str = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            bubble,
            text=time_str,
            font=ctk.CTkFont(size=10),
            text_color=("#888888", "#AAAAAA")
        )
        time_label.pack(anchor="e" if is_outgoing else "w", pady=(2, 0))
        
        # Message text with colored emojis
        msg_label = ctk.CTkLabel(
            bubble,
            text=emoji.emojize(text, language='alias'),
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF" if is_outgoing else "#000000",
            wraplength=300,
            justify="right" if is_outgoing else "left"
        )
        msg_label.pack(padx=10, pady=5, anchor="e" if is_outgoing else "w")
        
        # Pack message frame
        msg_frame.pack(fill="x", pady=5, padx=10, anchor="e" if is_outgoing else "w")
        
        # Scroll to bottom
        self.conversation_area._parent_canvas.yview_moveto(1.0)