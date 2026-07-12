"""
===============================================================================
RemoteDesk Pro
File: gui/pages/screen.py
Live screen sharing and remote control page.
===============================================================================
"""

from __future__ import annotations

import base64
import io
import threading
import time
from typing import Optional

import customtkinter as ctk
import mss
from PIL import Image

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY
from core.logger import get_logger

logger = get_logger()


class ScreenPage(ctk.CTkFrame):
    """Screen sharing page with live preview and remote control support."""

    STREAM_MAX_DIMENSION = 1920
    STREAM_FORMAT = "WEBP"

    def __init__(self, master):
        super().__init__(master)
        self._fps = DEFAULT_FPS
        self._quality = DEFAULT_QUALITY
        self._capturing = False
        self._capture_thread: Optional[threading.Thread] = None
        self._last_frame_metadata: dict = {}
        self._preview_image: Optional[ctk.CTkImage] = None
        self._control_enabled = False
        self._audio_capture = None
        self._remote_audio = None
        self._last_mouse_send = 0.0
        self._create_widgets()

    @property
    def _app(self):
        return getattr(self.master, "_app", None)

    @property
    def _connection_manager(self):
        return getattr(self.master, "_connection_manager", None)

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(12, 8))

        ctk.CTkLabel(
            header,
            text="Screen Session",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(side="left", padx=(6, 10))

        self.status_indicator = ctk.CTkLabel(
            header,
            text="Idle",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B6B",
        )
        self.status_indicator.pack(side="right", padx=8)

        self.preview_frame = ctk.CTkFrame(self, fg_color=("gray92", "#101820"), corner_radius=14)
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Connect to a device to view its screen, or start sharing your own screen to connected peers.",
            font=ctk.CTkFont(size=14),
            text_color=("#555555", "#A0A0A0"),
            wraplength=760,
            justify="center",
        )
        self.preview_label.pack(fill="both", expand=True, padx=20, pady=20)
        self.preview_label.bind("<Motion>", self._on_remote_mouse_move)
        self.preview_label.bind("<Button-1>", self._on_remote_click)
        self.preview_label.bind("<ButtonRelease-1>", self._on_remote_release)
        self.preview_label.bind("<MouseWheel>", self._on_remote_scroll)
        self.preview_label.bind("<Button-4>", self._on_remote_scroll)
        self.preview_label.bind("<Button-5>", self._on_remote_scroll)
        self.preview_label.bind("<KeyPress>", self._on_key_press)
        self.preview_label.bind("<KeyRelease>", self._on_key_release)

        controls = ctk.CTkFrame(self, fg_color=("gray95", "#1A1A1A"), corner_radius=12)
        controls.pack(fill="x", padx=20, pady=(0, 12))

        top_row = ctk.CTkFrame(controls, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 10))

        self.start_button = ctk.CTkButton(top_row, text="Start Sharing", width=140, command=self._start_sharing)
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = ctk.CTkButton(
            top_row,
            text="Stop Sharing",
            width=140,
            state="disabled",
            command=self._stop_sharing,
        )
        self.stop_button.pack(side="left", padx=(0, 8))

        self.remote_control_btn = ctk.CTkButton(
            top_row,
            text="Request Control",
            width=160,
            command=self._request_remote_control,
        )
        self.remote_control_btn.pack(side="left", padx=(0, 8))

        self.remote_audio_btn = ctk.CTkButton(
            top_row,
            text="Share Audio",
            width=140,
            command=self._toggle_audio_sharing,
        )
        self.remote_audio_btn.pack(side="left")

        options_row = ctk.CTkFrame(controls, fg_color="transparent")
        options_row.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(options_row, text="FPS", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 6))
        self.fps_combo = ctk.CTkComboBox(options_row, values=["15", "24", "30", "60"], width=86, command=self._on_fps_change)
        self.fps_combo.set(str(self._fps))
        self.fps_combo.pack(side="left", padx=(0, 18))

        ctk.CTkLabel(options_row, text="Quality", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 6))
        self.quality_slider = ctk.CTkSlider(
            options_row,
            from_=20,
            to=100,
            number_of_steps=80,
            command=self._on_quality_change,
        )
        self.quality_slider.set(self._quality)
        self.quality_slider.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.quality_value = ctk.CTkLabel(options_row, text=f"{self._quality}%", width=56)
        self.quality_value.pack(side="left")

        self.remote_status = ctk.CTkLabel(
            controls,
            text="Remote control inactive",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#AAAAAA"),
        )
        self.remote_status.pack(anchor="w", padx=18, pady=(0, 14))

    def _set_status(self, text: str, color: str) -> None:
        self.status_indicator.configure(text=text, text_color=color)

    def _on_fps_change(self, choice: str) -> None:
        try:
            self._fps = int(choice)
        except ValueError:
            pass

    def _on_quality_change(self, value: float) -> None:
        self._quality = int(value)
        self.quality_value.configure(text=f"{self._quality}%")

    def _start_sharing(self) -> None:
        if self._capturing:
            return
        manager = self._connection_manager
        if manager is None:
            return

        self._capturing = True
        self._set_status("Sharing", "#4CAF50")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        logger.info("Screen sharing started")

    def _stop_sharing(self) -> None:
        self._capturing = False
        self._set_status("Idle", "#FF6B6B")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self._stop_audio_sharing()
        logger.info("Screen sharing stopped")

    def _request_remote_control(self) -> None:
        manager = self._connection_manager
        if manager is None or not manager.has_active_session():
            self.remote_status.configure(text="Connect to a host first.", text_color="#FFAA33")
            return

        self._control_enabled = True
        manager.request_remote_control(self._app.username if self._app else "Remote User")
        self.preview_label.focus_set()
        self.remote_status.configure(
            text="Remote control requested. Click on the preview and use your mouse/keyboard there.",
            text_color="#4CAF50",
        )

    def _toggle_audio_sharing(self) -> None:
        if self._audio_capture and self._audio_capture.is_running():
            self._stop_audio_sharing()
            self.remote_audio_btn.configure(text="Share Audio")
        else:
            self._start_audio_sharing()
            self.remote_audio_btn.configure(text="Stop Audio")

    def _start_audio_sharing(self) -> None:
        try:
            from audio.audio_capture import create_audio_sender

            self._audio_capture = create_audio_sender(
                rate=16000,
                chunk=1024,
                channels=1,
                on_audio_data=lambda data: self._connection_manager and self._connection_manager.send_audio_frame(data),
            )
            self._audio_capture.start()
        except Exception as exc:
            logger.error(f"Failed to start audio capture: {exc}")

    def _stop_audio_sharing(self) -> None:
        if self._audio_capture:
            try:
                self._audio_capture.stop()
            except Exception:
                pass
            self._audio_capture = None
        self.remote_audio_btn.configure(text="Share Audio")

    def _capture_loop(self) -> None:
        with mss.mss() as mss_instance:
            monitor = mss_instance.monitors[0]
            while self._capturing:
                try:
                    start_time = time.time()
                    screenshot = mss_instance.grab(monitor)
                    image = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "BGR")
                    original_width, original_height = image.width, image.height
                    image = self._prepare_frame(image)
                    buffer = io.BytesIO()
                    image.save(
                        buffer,
                        format=self.STREAM_FORMAT,
                        quality=self._quality,
                        method=6,
                    )
                    if self._connection_manager:
                        self._connection_manager.send_screen_frame(
                            buffer.getvalue(),
                            metadata={
                                "width": image.width,
                                "height": image.height,
                                "original_width": original_width,
                                "original_height": original_height,
                                "format": self.STREAM_FORMAT.lower(),
                                "quality": self._quality,
                            },
                        )
                    elapsed = time.time() - start_time
                    delay = max(0.0, 1.0 / self._fps - elapsed)
                    if delay:
                        time.sleep(delay)
                except Exception as exc:
                    logger.error(f"Screen capture error: {exc}")
                    self.after(0, self._stop_sharing)
                    break

    def _prepare_frame(self, image: Image.Image) -> Image.Image:
        """Resize oversized frames before encoding to keep quality stable."""
        max_dimension = self.STREAM_MAX_DIMENSION
        width, height = image.size
        largest_side = max(width, height)
        if largest_side <= max_dimension:
            return image

        scale = max_dimension / float(largest_side)
        resized = image.resize(
            (max(1, int(width * scale)), max(1, int(height * scale))),
            Image.Resampling.LANCZOS,
        )
        return resized

    def handle_remote_frame(self, payload: dict) -> None:
        """Render a frame received from a connected device."""
        frame_data = payload.get("frame_data")
        if not frame_data:
            return

        try:
            decoded = base64.b64decode(frame_data)
            image = Image.open(io.BytesIO(decoded)).convert("RGB")
            self._last_frame_metadata = payload.get("metadata", {})

            max_width = max(self.preview_frame.winfo_width() - 40, 320)
            max_height = max(self.preview_frame.winfo_height() - 40, 240)
            resized = image.copy()
            resized.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(light_image=resized, dark_image=resized, size=resized.size)

            self._preview_image = ctk_image
            self.preview_label.configure(text="", image=ctk_image)
            self.preview_label.focus_set()
            self._set_status("Viewing Remote Screen", "#4CAF50")
        except Exception as exc:
            logger.error(f"Failed to render remote frame: {exc}")

    def handle_remote_audio(self, payload: dict) -> None:
        """Play an incoming audio chunk if playback dependencies are available."""
        encoded_audio = payload.get("audio_data")
        if not encoded_audio:
            return

        try:
            audio_bytes = base64.b64decode(encoded_audio)
            self._play_remote_audio(audio_bytes)
        except Exception as exc:
            logger.error(f"Failed to decode remote audio: {exc}")

    def _play_remote_audio(self, audio_bytes: bytes) -> None:
        try:
            import pyaudio

            if self._remote_audio is None:
                self._remote_audio = {
                    "driver": pyaudio.PyAudio(),
                    "stream": None,
                }

            if self._remote_audio["stream"] is None:
                self._remote_audio["stream"] = self._remote_audio["driver"].open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True,
                )

            self._remote_audio["stream"].write(audio_bytes)
        except Exception as exc:
            logger.debug(f"Remote audio playback unavailable: {exc}")

    def _map_event_to_remote(self, event) -> Optional[tuple[int, int]]:
        if not self._last_frame_metadata:
            return None

        frame_width = int(self._last_frame_metadata.get("width", 0))
        frame_height = int(self._last_frame_metadata.get("height", 0))
        if frame_width <= 0 or frame_height <= 0:
            return None

        label_width = max(self.preview_label.winfo_width(), 1)
        label_height = max(self.preview_label.winfo_height(), 1)
        x_ratio = min(max(event.x / label_width, 0.0), 1.0)
        y_ratio = min(max(event.y / label_height, 0.0), 1.0)
        return int(frame_width * x_ratio), int(frame_height * y_ratio)

    def _on_remote_mouse_move(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        now = time.time()
        if now - self._last_mouse_send < 0.015:
            return
        coords = self._map_event_to_remote(event)
        if coords is None:
            return
        self._last_mouse_send = now
        self._connection_manager.send_mouse_event(x=coords[0], y=coords[1], action="move")

    def _on_remote_click(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        coords = self._map_event_to_remote(event)
        if coords is None:
            return
        self._connection_manager.send_mouse_event(x=coords[0], y=coords[1], action="down", button="left")

    def _on_remote_release(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        coords = self._map_event_to_remote(event)
        if coords is None:
            return
        self._connection_manager.send_mouse_event(x=coords[0], y=coords[1], action="up", button="left")
        self._connection_manager.send_mouse_event(x=coords[0], y=coords[1], action="click", button="left")

    def _on_remote_scroll(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        delta = 0
        if hasattr(event, "delta") and event.delta:
            delta = int(event.delta / 120)
        elif getattr(event, "num", None) == 4:
            delta = 1
        elif getattr(event, "num", None) == 5:
            delta = -1
        if delta:
            self._connection_manager.send_mouse_event(action="scroll", delta=delta)

    def _on_key_press(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        key = event.keysym.lower()
        if len(key) == 1:
            self._connection_manager.send_keyboard_event(key=key, action="tap")
        else:
            self._connection_manager.send_keyboard_event(key=key, action="press")

    def _on_key_release(self, event) -> None:
        if not self._control_enabled or self._connection_manager is None:
            return
        key = event.keysym.lower()
        if len(key) > 1:
            self._connection_manager.send_keyboard_event(key=key, action="release")
