"""
===============================================================================
RemoteDesk Pro
File: gui/pages/screen.py
Screen sharing page with premium glassmorphism UI
===============================================================================
"""

from __future__ import annotations

import threading
import time
import logging
from typing import Optional

import customtkinter as ctk
import mss
from PIL import Image
import io

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger

logger = get_logger()

class ScreenPage(ctk.CTkFrame):
    """
    Screen sharing page for RemoteDesk Pro with premium glassmorphism UI.
    """
    
    def __init__(self, master):
        super().__init__(master)
        self._fps = DEFAULT_FPS
        self._quality = DEFAULT_QUALITY
        self._capturing = False
        self._capture_thread = None
        self._monitor = None
        self._connection_manager = None
        self._audio_sender = None
        self._audio_receiver = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout the UI elements with glassmorphism styling."""
        # Header with glass effect
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Screen Sharing",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left", padx=10)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame,
            text="● Idle",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_indicator.pack(side="right", padx=10)
        
        # Main content frame with glass effect
        content_frame = ctk.CTkFrame(self, fg_color=("gray15", "gray85"))
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # FPS Control Section
        fps_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        fps_section.pack(fill="x", pady=(15, 10))
        
        fps_label = ctk.CTkLabel(
            fps_section,
            text="FPS:",
            font=ctk.CTkFont(size=14)
        )
        fps_label.pack(side="left", padx=(20, 5))
        
        self.fps_combo = ctk.CTkComboBox(
            fps_section,
            values=["15", "24", "30", "60"],
            state="readonly",
            width=80
        )
        self.fps_combo.set(str(self._fps))
        self.fps_combo.pack(side="left", padx=5)
        self.fps_combo.bind("<<ComboboxSelected>>", self._on_fps_change)
        
        # Quality Control Section
        quality_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        quality_section.pack(fill="x", padx=20, pady=10)
        
        quality_label = ctk.CTkLabel(
            quality_section,
            text="Quality:",
            font=ctk.CTkFont(size=14)
        )
        quality_label.pack(side="left", padx=(20, 5))
        
        self.quality_slider = ctk.CTkSlider(
            quality_section,
            from_=1,
            to=100,
            number_of_steps=100,
            command=self._on_quality_change
        )
        self.quality_slider.set(self._quality)
        self.quality_slider.pack(side="left", fill="x", expand=True, padx=5)
        
        self.quality_value = ctk.CTkLabel(
            quality_section,
            text=f"{self._quality}%",
            font=ctk.CTkFont(size=14)
        )
        self.quality_value.pack(side="right", padx=(5, 20))
        
        # Control Buttons Section
        buttons_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_section.pack(fill="x", padx=20, pady=20)
        
        self.start_button = ctk.CTkButton(
            buttons_section,
            text="Start Sharing",
            width=140,
            height=40,
            command=self._start_sharing
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(
            buttons_section,
            text="Stop Sharing",
            width=140,
            height=40,
            command=self._stop_sharing,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        # Remote Control Section
        remote_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        remote_section.pack(fill="x", padx=20, pady=(10, 20))
        
        remote_label = ctk.CTkLabel(
            remote_section,
            text="Remote Control",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        remote_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.remote_status = ctk.CTkLabel(
            remote_section,
            text="● Disconnected",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF6B6B"
        )
        self.remote_status.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Control buttons
        remote_buttons = ctk.CTkFrame(remote_section, fg_color="transparent")
        remote_buttons.pack(fill="x", padx=20, pady=(0, 20))
        
        self.remote_control_btn = ctk.CTkButton(
            remote_buttons,
            text="Request Control",
            width=160,
            height=35,
            command=self._request_remote_control
        )
        self.remote_control_btn.pack(side="left", padx=10)
        
        self.remote_audio_btn = ctk.CTkButton(
            remote_buttons,
            text="Share Audio",
            width=160,
            height=35,
            command=self._toggle_audio_sharing
        )
        self.remote_audio_btn.pack(side="left", padx=10)
        
        # Info Section
        info_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_section.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        info_label = ctk.CTkLabel(
            info_section,
            text="Instructions:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        instructions = [
            "1. Set desired FPS and Quality for optimal performance",
            "2. Click 'Start Sharing' to begin screen transmission",
            "3. Remote device can request control via 'Request Control'",
            "4. Enable audio sharing for real-time voice communication",
            "5. Connection status indicators show current state"
        ]
        
        for instruction in instructions:
            instr_label = ctk.CTkLabel(
                info_section,
                text=f"• {instruction}",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            instr_label.pack(anchor="w", padx=30, pady=2)
    
    def _on_fps_change(self, choice):
        """Handle FPS dropdown change."""
        try:
            self._fps = int(choice)
            logger.debug(f"FPS changed to {self._fps}")
        except ValueError:
            pass
    
    def _on_quality_change(self, value):
        """Handle quality slider change."""
        self._quality = int(value)
        self.quality_value.configure(text=f"{self._quality}%")
        logger.debug(f"Quality changed to {self._quality}")
    
    def _start_sharing(self):
        """Start screen sharing session."""
        if self._capturing:
            return
        
        self._capturing = True
        self.status_indicator.configure(text="● Sharing", text_color="#4CAF50")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.remote_status.configure(text="● Available", text_color="#4CAF50")
        
        # Initialize connection manager if not set
        if not self._connection_manager:
            from core.constants import DEFAULT_PORT
            from network.connection_manager import ConnectionManager
            self._connection_manager = ConnectionManager(server_port=DEFAULT_PORT)
        
        # Initialize audio sharing
        self._start_audio_sharing()
        
        # Start capture thread
        self._capture_thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self._capture_thread.start()
        
        logger.info("Screen sharing started with audio")
    
    def _stop_sharing(self):
        """Stop screen sharing session."""
        self._capturing = False
        self.status_indicator.configure(text="● Idle", text_color="#FF6B6B")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.remote_status.configure(text="● Disconnected", text_color="#FF6B6B")
        self._stop_audio_sharing()
        
        logger.info("Screen sharing stopped")
    
    def _start_audio_sharing(self):
        """Start audio sharing session."""
        try:
            from audio.audio_capture import create_audio_capture
            self._audio_capture = create_audio_capture(
                rate=16000,
                chunk=1024,
                on_audio_data=self._send_audio_frame
            )
            self._audio_capture.start()
            logger.info("Audio sharing started")
        except Exception as e:
            logger.error(f"Failed to start audio sharing: {e}")
    
    def _stop_audio_sharing(self):
        """Stop audio sharing session."""
        if hasattr(self, '_audio_capture') and self._audio_capture:
            try:
                self._audio_capture.stop()
                logger.info("Audio sharing stopped")
            except Exception as e:
                logger.error(f"Error stopping audio: {e}")
    
    def _send_audio_frame(self, audio_data: bytes):
        """Send audio frame to remote device."""
        if self._connection_manager:
            self._connection_manager.send_audio_frame(audio_data)
    
    def _request_remote_control(self):
        """Request remote control permissions."""
        logger.info("Remote control requested")
        # Would normally send request to remote device
        self.remote_status.configure(text="● Requesting...", text_color="#FFA500")
        self.after(2000, lambda: self.remote_status.configure(text="● Granted", text_color="#4CAF50"))
    
    def _toggle_audio_sharing(self):
        """Toggle audio sharing on/off."""
        if hasattr(self, '_audio_capture') and self._audio_capture:
            if self._audio_capture.is_running():
                self._stop_audio_sharing()
                self.remote_audio_btn.configure(text="Share Audio")
            else:
                self._start_audio_sharing()
                self.remote_audio_btn.configure(text="Stop Audio")
        else:
            self._start_audio_sharing()
            self.remote_audio_btn.configure(text="Stop Audio")
    
    def _capture_loop(self):
        """Main screen capture loop."""
        mss_instance = mss.mss()
        self._monitor = mss_instance.monitors[0]  # Primary monitor
        
        while self._capturing:
            try:
                start_time = time.time()
                
                # Capture screen
                screenshot = mss_instance.grab(self._monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "BGR")
                
                # Compress to JPEG
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=self._quality)
                frame_data = buf.getvalue()
                
                # Send frame
                if self._connection_manager:
                    self._connection_manager.send_screen_frame(frame_data)
                
                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0.0, 1.0 / self._fps - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Screen capture error: {e}")
                self._stop_sharing()