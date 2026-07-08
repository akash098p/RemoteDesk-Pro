"""
===============================================================================
RemoteDesk Pro
File: gui/pages/screen.py

Screen sharing page with capture controls, viewer display, and quality tuning.
Supports local screen capture and stream receiver integration for Phase 4.
===============================================================================
"""

from __future__ import annotations

import base64
import customtkinter
from typing import Optional, Any

from core.constants import DEFAULT_FPS, DEFAULT_QUALITY, DEFAULT_PORT, MAX_FPS, MIN_FPS, MAX_QUALITY, MIN_QUALITY
from core.logger import logger
from core.theme_manager import get_theme_manager
from network.connection_manager import ConnectionManager
from network.protocol import MessageFactory, MessageType, RemoteDeskMessage
from screen_capture.capture import create_screen_capture, ScreenCapture
from screen_capture.streaming_client import create_streaming_client, StreamingClient

theme_manager = get_theme_manager()


class ScreenPage(customtkinter.CTkFrame):
    """Screen sharing and viewing page."""

    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self._theme = theme_manager

        self._capture: Optional[ScreenCapture] = None
        self._stream_client: Optional[StreamingClient] = None
        self._connection_manager: Optional[ConnectionManager] = None
        self._viewer_label: Optional[customtkinter.CTkLabel] = None

        self._host_value = customtkinter.StringVar(value="0.0.0.0")
        self._port_value = customtkinter.IntVar(value=DEFAULT_PORT)
        self._remote_host_value = customtkinter.StringVar(value="127.0.0.1")
        self._remote_port_value = customtkinter.IntVar(value=DEFAULT_PORT)
        self._network_status_label: Optional[customtkinter.CTkLabel] = None

        self._fps_value = customtkinter.IntVar(value=DEFAULT_FPS)
        self._quality_value = customtkinter.IntVar(value=DEFAULT_QUALITY)
        self._is_sharing = False
        self._is_receiving = False

        self._create_widgets()

    def _create_widgets(self) -> None:
        header = customtkinter.CTkLabel(
            self,
            text="Screen Sharing",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
            anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        controls_frame = customtkinter.CTkFrame(self, fg_color=self._theme.get_color("card_bg", "#252525"))
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))

        self._share_btn = customtkinter.CTkButton(
            controls_frame,
            text="Start Sharing",
            command=self._toggle_sharing,
            width=180,
        )
        self._share_btn.grid(row=0, column=0, padx=10, pady=10)

        self._receive_btn = customtkinter.CTkButton(
            controls_frame,
            text="Start Receiving",
            command=self._toggle_receiving,
            width=180,
        )
        self._receive_btn.grid(row=0, column=1, padx=10, pady=10)

        self._fullscreen_btn = customtkinter.CTkButton(
            controls_frame,
            text="Fullscreen Preview",
            command=self._toggle_fullscreen,
            width=180,
        )
        self._fullscreen_btn.grid(row=0, column=2, padx=10, pady=10)

        network_frame = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        network_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))

        host_label = customtkinter.CTkLabel(
            network_frame,
            text="Host:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        host_label.grid(row=0, column=0, padx=(0, 8), pady=2, sticky="w")

        self._host_entry = customtkinter.CTkEntry(
            network_frame,
            width=140,
            textvariable=self._host_value,
        )
        self._host_entry.grid(row=0, column=1, padx=(0, 8), pady=2, sticky="w")

        port_label = customtkinter.CTkLabel(
            network_frame,
            text="Port:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        port_label.grid(row=0, column=2, padx=(0, 8), pady=2, sticky="w")

        self._port_entry = customtkinter.CTkEntry(
            network_frame,
            width=90,
            textvariable=self._port_value,
        )
        self._port_entry.grid(row=0, column=3, padx=(0, 8), pady=2, sticky="w")

        remote_host_label = customtkinter.CTkLabel(
            network_frame,
            text="Remote Host:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        remote_host_label.grid(row=1, column=0, padx=(0, 8), pady=2, sticky="w")

        self._remote_host_entry = customtkinter.CTkEntry(
            network_frame,
            width=140,
            textvariable=self._remote_host_value,
        )
        self._remote_host_entry.grid(row=1, column=1, padx=(0, 8), pady=2, sticky="w")

        remote_port_label = customtkinter.CTkLabel(
            network_frame,
            text="Remote Port:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        remote_port_label.grid(row=1, column=2, padx=(0, 8), pady=2, sticky="w")

        self._remote_port_entry = customtkinter.CTkEntry(
            network_frame,
            width=90,
            textvariable=self._remote_port_value,
        )
        self._remote_port_entry.grid(row=1, column=3, padx=(0, 8), pady=2, sticky="w")

        self._network_status_label = customtkinter.CTkLabel(
            network_frame,
            text="Network status: idle",
            text_color=self._theme.get_color("text_secondary", "#A0A0A0"),
            anchor="w",
        )
        self._network_status_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        fps_frame = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        fps_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        fps_label = customtkinter.CTkLabel(
            fps_frame,
            text="FPS:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        fps_label.pack(side="left", padx=(0, 8))

        self._fps_slider = customtkinter.CTkSlider(
            fps_frame,
            from_=MIN_FPS,
            to=MAX_FPS,
            number_of_steps=MAX_FPS - MIN_FPS,
            variable=self._fps_value,
            command=lambda v: self._update_fps(int(v)),
            width=300,
        )
        self._fps_slider.pack(side="left", padx=(0, 8), fill="x", expand=True)

        self._fps_value_label = customtkinter.CTkLabel(
            fps_frame,
            text=str(DEFAULT_FPS),
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
            width=60,
        )
        self._fps_value_label.pack(side="left")

        quality_frame = customtkinter.CTkFrame(controls_frame, fg_color="transparent")
        quality_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        quality_label = customtkinter.CTkLabel(
            quality_frame,
            text="Quality:",
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
        )
        quality_label.pack(side="left", padx=(0, 8))

        self._quality_slider = customtkinter.CTkSlider(
            quality_frame,
            from_=MIN_QUALITY,
            to=MAX_QUALITY,
            number_of_steps=MAX_QUALITY - MIN_QUALITY,
            variable=self._quality_value,
            command=lambda v: self._update_quality(int(v)),
            width=300,
        )
        self._quality_slider.pack(side="left", padx=(0, 8), fill="x", expand=True)

        self._quality_value_label = customtkinter.CTkLabel(
            quality_frame,
            text=str(DEFAULT_QUALITY),
            text_color=self._theme.get_color("text_primary", "#FFFFFF"),
            width=60,
        )
        self._quality_value_label.pack(side="left")

        viewer_wrapper = customtkinter.CTkFrame(self, fg_color=self._theme.get_color("background", "#0D0D0D"))
        viewer_wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._viewer_label = customtkinter.CTkLabel(
            viewer_wrapper,
            text="Viewer / shared screen preview",
            width=800,
            height=400,
            fg_color=self._theme.get_color("surface", "#1A1A1A"),
            corner_radius=10,
            text_color=self._theme.get_color("text_secondary", "#A0A0A0"),
        )
        self._viewer_label.pack(fill="both", expand=True, padx=10, pady=10)

    def _toggle_sharing(self) -> None:
        if self._is_sharing:
            self._stop_sharing()
        else:
            self._start_sharing()

    def _toggle_receiving(self) -> None:
        if self._is_receiving:
            self._stop_receiving()
        else:
            self._start_receiving()

    def _toggle_fullscreen(self) -> None:
        if self._viewer_label:
            self.parent.attributes("-fullscreen", not self.parent.attributes("-fullscreen"))

    def _update_fps(self, value: int) -> None:
        self._fps_value_label.configure(text=str(value))
        if self._capture:
            self._capture.set_fps(value)

    def _update_quality(self, value: int) -> None:
        self._quality_value_label.configure(text=str(value))
        if self._capture:
            self._capture.set_quality(value)

    def _start_sharing(self) -> None:
        host = self._host_value.get().strip() or "0.0.0.0"
        port = self._port_value.get()

        self._connection_manager = ConnectionManager(
            server_port=port,
            server_callback=self._on_network_event,
        )
        if not self._connection_manager.initialize(is_server=True, host=host, port=port):
            if self._network_status_label:
                self._network_status_label.configure(
                    text="Network status: failed to host",
                    text_color=self._theme.get_color("error", "#F44336"),
                )
            return

        self._capture = create_screen_capture(
            fps=self._fps_value.get(),
            quality=self._quality_value.get(),
            on_frame=self._on_frame_captured,
        )

        if self._capture.start():
            self._is_sharing = True
            self._share_btn.configure(text="Stop Sharing")
            self._viewer_label.configure(text="Sharing your screen...", text_color=self._theme.get_color("text_primary", "#FFFFFF"))
            if self._network_status_label:
                self._network_status_label.configure(
                    text=f"Hosting on {host}:{port}",
                    text_color=self._theme.get_color("success", "#4CAF50"),
                )
        else:
            if self._connection_manager:
                self._connection_manager.stop()
                self._connection_manager = None

    def _stop_sharing(self) -> None:
        if self._capture:
            self._capture.stop()
            self._capture.destroy()
            self._capture = None
        if self._connection_manager:
            self._connection_manager.stop()
            self._connection_manager = None

        self._is_sharing = False
        self._share_btn.configure(text="Start Sharing")
        self._viewer_label.configure(text="Viewer / shared screen preview", text_color=self._theme.get_color("text_secondary", "#A0A0A0"))
        if self._network_status_label:
            self._network_status_label.configure(text="Network status: idle", text_color=self._theme.get_color("text_secondary", "#A0A0A0"))

    def _start_receiving(self) -> None:
        if self._viewer_label is None:
            return

        host = self._remote_host_value.get().strip()
        port = self._remote_port_value.get()

        self._connection_manager = ConnectionManager(
            server_port=port,
            client_callback=self._on_network_event,
        )
        if not self._connection_manager.initialize(is_server=False, host=host, port=port):
            if self._network_status_label:
                self._network_status_label.configure(
                    text="Network status: failed to connect",
                    text_color=self._theme.get_color("error", "#F44336"),
                )
            return

        self._stream_client = create_streaming_client(
            display_widget=self._viewer_label,
        )
        self._stream_client.start()
        self._is_receiving = True
        self._receive_btn.configure(text="Stop Receiving")
        self._viewer_label.configure(text="Receiving remote screen...", text_color=self._theme.get_color("text_primary", "#FFFFFF"))
        if self._network_status_label:
            self._network_status_label.configure(
                text=f"Connected to {host}:{port}",
                text_color=self._theme.get_color("success", "#4CAF50"),
            )

    def _stop_receiving(self) -> None:
        if self._stream_client:
            self._stream_client.stop()
            self._stream_client.destroy()
            self._stream_client = None
        if self._connection_manager:
            self._connection_manager.stop()
            self._connection_manager = None

        self._is_receiving = False
        self._receive_btn.configure(text="Start Receiving")
        if self._viewer_label:
            self._viewer_label.configure(text="Viewer / shared screen preview", text_color=self._theme.get_color("text_secondary", "#A0A0A0"))
        if self._network_status_label:
            self._network_status_label.configure(text="Network status: idle", text_color=self._theme.get_color("text_secondary", "#A0A0A0"))

    def _on_frame_captured(self, frame_bytes: bytes) -> None:
        """Handle locally captured screen frames, update the preview, and send remote frames."""
        if self._viewer_label:
            self._viewer_label.after(0, lambda: self._update_preview_image(frame_bytes))

        if self._is_sharing and self._connection_manager:
            try:
                frame_message = MessageFactory.create_screen_frame(frame_bytes)
                self._connection_manager.send_message(frame_message)
            except Exception as e:
                logger.error(f"Failed to send screen frame: {e}")

    def _update_preview_image(self, frame_bytes: bytes) -> None:
        try:
            try:
                img = customtkinter.CTkImage(
                    light_image=customtkinter.CTkImage._from_pil_image_bytes(frame_bytes),
                    dark_image=customtkinter.CTkImage._from_pil_image_bytes(frame_bytes),
                    size=(self._viewer_label.winfo_width() or 640, self._viewer_label.winfo_height() or 360),
                )
            except Exception:
                import io
                from PIL import Image

                buffer = io.BytesIO(frame_bytes)
                pil_image = Image.open(buffer)
                pil_image.thumbnail(
                    (self._viewer_label.winfo_width() or 640, self._viewer_label.winfo_height() or 360),
                    Image.LANCZOS,
                )
                img = customtkinter.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)

            if self._viewer_label:
                self._viewer_label.configure(image=img, text="")
                self._viewer_label._current_image = img
        except Exception as e:
            logger.error(f"Failed to update preview image: {e}")

    def _on_network_event(self, event_type: str, payload: Any) -> None:
        if event_type == "connection":
            if self._network_status_label:
                self._network_status_label.configure(
                    text="Network status: connected",
                    text_color=self._theme.get_color("success", "#4CAF50"),
                )
        elif event_type == "disconnection":
            if self._network_status_label:
                self._network_status_label.configure(
                    text="Network status: disconnected",
                    text_color=self._theme.get_color("text_secondary", "#A0A0A"),
                )
        elif event_type == "message" and isinstance(payload, RemoteDeskMessage):
            if payload.message_type == MessageType.SCREEN_FRAME.value:
                self._handle_remote_frame(payload)

    def _handle_remote_frame(self, message: RemoteDeskMessage) -> None:
        try:
            frame_data = message.payload.get("frame_data")
            if not frame_data:
                return

            frame_bytes = base64.b64decode(frame_data)
            if self._stream_client:
                self._stream_client.receive_frame(frame_bytes)
        except Exception as e:
            logger.error(f"Failed to decode remote screen frame: {e}")

    def destroy(self) -> None:
        self._stop_sharing()
        self._stop_receiving()
        super().destroy()