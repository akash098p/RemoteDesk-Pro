"""
=================================================================================
RemoteDesk Pro
File: gui/pages/connection.py
Connection management page for LAN and optional public sessions.
=================================================================================
"""

from __future__ import annotations

import socket
import threading
from typing import Callable, Optional

import customtkinter as ctk

from core.constants import DEFAULT_PORT
from core.logger import get_logger

logger = get_logger()


class ConnectionPage(ctk.CTkFrame):
    """Connection page for hosting, scanning, and joining sessions."""

    def __init__(self, master, on_connect: Optional[Callable[[str, int], bool]] = None):
        super().__init__(master, fg_color="transparent")
        self.on_connect = on_connect
        self._scan_results: list[str] = []
        self._scanning = False
        self._scan_thread: Optional[threading.Thread] = None
        self._create_widgets()
        self.after(200, self._refresh_host_info)
        self.after(350, self.refresh_connections)

    @property
    def _app(self):
        return getattr(self.master, "_app", None)

    @property
    def _connection_manager(self):
        return getattr(self.master, "_connection_manager", None)

    def _create_widgets(self) -> None:
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=18, pady=(12, 8))

        header = ctk.CTkFrame(self.scroll_frame, fg_color=("gray92", "#202020"), corner_radius=16)
        header.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            header,
            text="Connections",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#111111", "#FFFFFF"),
        ).pack(anchor="w", padx=20, pady=(16, 4))

        ctk.CTkLabel(
            header,
            text="Host this device, scan your LAN, or connect manually using a local IP or public endpoint.",
            font=ctk.CTkFont(size=13),
            text_color=("#666666", "#BBBBBB"),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        host_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=16)
        host_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            host_frame,
            text="This Device",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(16, 10))

        info_grid = ctk.CTkFrame(host_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 8))
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)

        self.host_ip_label = ctk.CTkLabel(info_grid, text="LAN IP: --", font=ctk.CTkFont(size=14), anchor="w")
        self.host_ip_label.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=4)

        self.host_port_label = ctk.CTkLabel(
            info_grid,
            text=f"Port: {DEFAULT_PORT}",
            font=ctk.CTkFont(size=14),
            anchor="w",
        )
        self.host_port_label.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        self.public_link_label = ctk.CTkLabel(
            host_frame,
            text="Public Link: Not enabled",
            font=ctk.CTkFont(size=13),
            wraplength=900,
            justify="left",
            anchor="w",
        )
        self.public_link_label.pack(fill="x", padx=20, pady=(0, 8))

        self.public_help_label = ctk.CTkLabel(
            host_frame,
            text="For internet access, create a public TCP link and share that exact endpoint with the other device.",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#AAAAAA"),
            wraplength=900,
            justify="left",
            anchor="w",
        )
        self.public_help_label.pack(fill="x", padx=20, pady=(0, 12))

        ngrok_row = ctk.CTkFrame(host_frame, fg_color="transparent")
        ngrok_row.pack(fill="x", padx=20, pady=(0, 10))

        self.ngrok_token_entry = ctk.CTkEntry(
            ngrok_row,
            placeholder_text="Ngrok auth token",
            height=38,
        )
        self.ngrok_token_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        saved_token = ""
        if self._app is not None:
            try:
                saved_token = self._app.config_manager.get_value("config", "ngrok_token", "")
            except Exception:
                saved_token = ""
        if saved_token:
            self.ngrok_token_entry.insert(0, saved_token)

        self.region_combo = ctk.CTkComboBox(
            ngrok_row,
            values=["us", "eu", "ap", "au", "sa", "jp", "in"],
            width=100,
            state="readonly",
        )
        self.region_combo.set("us")
        if self._app is not None:
            try:
                self.region_combo.set(self._app.config_manager.get_value("config", "ngrok_region", "us"))
            except Exception:
                pass
        self.region_combo.pack(side="left")

        host_buttons = ctk.CTkFrame(host_frame, fg_color="transparent")
        host_buttons.pack(fill="x", padx=20, pady=(0, 16))

        self.refresh_info_btn = ctk.CTkButton(
            host_buttons,
            text="Refresh Info",
            width=140,
            height=40,
            command=self._refresh_host_info,
        )
        self.refresh_info_btn.pack(side="left", padx=(0, 10), pady=4)

        self.public_link_btn = ctk.CTkButton(
            host_buttons,
            text="Create Public Link",
            width=170,
            height=40,
            command=self._enable_public_link,
        )
        self.public_link_btn.pack(side="left", padx=(0, 10), pady=4)

        self.disconnect_btn = ctk.CTkButton(
            host_buttons,
            text="Disconnect Session",
            width=170,
            height=40,
            command=self._disconnect_session,
        )
        self.disconnect_btn.pack(side="left", pady=4)

        manual_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=16)
        manual_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            manual_frame,
            text="Manual Connect",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            manual_frame,
            text="Use a LAN IP like 192.168.x.x for same-network sessions, or paste a public endpoint like tcp://0.tcp.in.ngrok.io:12345 for internet sessions.",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#AAAAAA"),
            wraplength=900,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        input_row = ctk.CTkFrame(manual_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=20, pady=(0, 16))

        self.ip_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Host, IP, or public endpoint",
            height=42,
        )
        self.ip_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.port_entry = ctk.CTkEntry(
            input_row,
            placeholder_text=f"Port ({DEFAULT_PORT})",
            width=150,
            height=42,
        )
        self.port_entry.pack(side="left", padx=(0, 10))

        self.connect_btn = ctk.CTkButton(
            input_row,
            text="Connect",
            width=140,
            height=42,
            command=self._manual_connect,
        )
        self.connect_btn.pack(side="left")

        list_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray95", "#1A1A1A"), corner_radius=16)
        list_frame.pack(fill="x", pady=(0, 8))

        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill="x", padx=18, pady=(15, 10))

        ctk.CTkLabel(
            list_header,
            text="LAN Devices",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        self.scan_btn = ctk.CTkButton(
            list_header,
            text="Scan Network",
            width=130,
            height=38,
            command=self.scan_network,
        )
        self.scan_btn.pack(side="right")

        self.device_scroll = ctk.CTkScrollableFrame(list_frame, fg_color="transparent", height=260)
        self.device_scroll.pack(fill="x", padx=16, pady=(0, 16))

        self.placeholder = ctk.CTkLabel(
            self.device_scroll,
            text="No devices found yet. Start the app on another device and scan the local network.",
            font=ctk.CTkFont(size=13),
            text_color=("#777777", "#999999"),
            wraplength=760,
            justify="left",
        )
        self.placeholder.pack(pady=40)

        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#AAAAAA"),
        ).pack(anchor="w", padx=24, pady=(0, 10))

    def _refresh_host_info(self) -> None:
        manager = self._connection_manager
        if manager is None:
            return
        self.host_ip_label.configure(text=f"LAN IP: {manager.get_local_ip()}")
        self.host_port_label.configure(text=f"Port: {manager.server_port}")
        public_endpoint = manager.get_public_endpoint()
        if public_endpoint:
            self.public_link_label.configure(text=f"Public Link: {public_endpoint}")
        else:
            self.public_link_label.configure(text="Public Link: Not enabled")
        self.status_var.set(manager.get_session_summary())

    def _disconnect_session(self) -> None:
        manager = self._connection_manager
        if manager is None:
            return
        manager.disconnect_active_session()
        self.status_var.set("Session disconnected.")
        self._refresh_host_info()

    def _enable_public_link(self) -> None:
        manager = self._connection_manager
        if manager is None:
            return

        self.status_var.set("Creating public link...")
        token = self.ngrok_token_entry.get().strip() or None
        region = self.region_combo.get().strip() or "us"
        if self._app is not None:
            try:
                self._app.config_manager.set_value("config", "ngrok_token", token or "")
                self._app.config_manager.set_value("config", "ngrok_region", region)
            except Exception:
                pass

        public_url = manager.enable_public_tunnel(auth_token=token, region=region)
        if public_url:
            self.public_link_label.configure(text=f"Public Link: {public_url}")
            self.status_var.set("Public link ready. Share that exact TCP endpoint with the other device.")
        else:
            self.status_var.set("Public link unavailable. Install pyngrok and configure an ngrok token if needed.")

    def scan_network(self) -> None:
        """Scan local network for hosts listening on the RemoteDesk port."""
        if self._scanning:
            return

        self._scanning = True
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_var.set("Scanning local network...")

        for widget in self.device_scroll.winfo_children():
            widget.destroy()

        self.placeholder = ctk.CTkLabel(
            self.device_scroll,
            text="Scanning for available RemoteDesk hosts...",
            font=ctk.CTkFont(size=13),
            text_color=("#777777", "#999999"),
        )
        self.placeholder.pack(pady=40)

        self._scan_thread = threading.Thread(target=self._scan_network_thread, daemon=True)
        self._scan_thread.start()

    def _scan_network_thread(self) -> None:
        try:
            probe_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe_socket.connect(("8.8.8.8", 80))
            local_ip = probe_socket.getsockname()[0]
            probe_socket.close()

            base_ip = ".".join(local_ip.split(".")[:3])
            found_devices: list[str] = []
            found_lock = threading.Lock()

            def check_ip(ip: str) -> None:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.15)
                    result = sock.connect_ex((ip, DEFAULT_PORT))
                    sock.close()
                    if result == 0:
                        with found_lock:
                            found_devices.append(ip)
                except Exception:
                    pass

            workers = []
            for i in range(1, 255):
                ip = f"{base_ip}.{i}"
                if ip == local_ip:
                    continue
                worker = threading.Thread(target=check_ip, args=(ip,), daemon=True)
                workers.append(worker)
                worker.start()

            for worker in workers:
                worker.join()

            self.after(0, lambda: self._update_device_list(sorted(found_devices)))
        except Exception as exc:
            self.after(0, lambda: self._scan_error(str(exc)))

    def _update_device_list(self, devices: list[str]) -> None:
        for widget in self.device_scroll.winfo_children():
            widget.destroy()

        self._scan_results = devices
        self._scanning = False
        self.scan_btn.configure(state="normal", text="Scan Network")
        self.status_var.set(f"Scan complete. Found {len(devices)} host(s).")

        if not devices:
            self.placeholder = ctk.CTkLabel(
                self.device_scroll,
                text=f"No hosts found on port {DEFAULT_PORT}. Make sure the other device is running RemoteDesk Pro.",
                font=ctk.CTkFont(size=13),
                text_color=("#777777", "#999999"),
                wraplength=760,
                justify="left",
            )
            self.placeholder.pack(pady=40)
            return

        for device_ip in devices:
            card = ctk.CTkFrame(self.device_scroll, fg_color=("white", "#232323"), corner_radius=12)
            card.pack(fill="x", padx=4, pady=6)

            details = ctk.CTkFrame(card, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True, padx=15, pady=12)

            ctk.CTkLabel(
                details,
                text="RemoteDesk Pro Host",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=f"{device_ip}:{DEFAULT_PORT}",
                font=ctk.CTkFont(size=12),
                text_color=("#666666", "#AAAAAA"),
            ).pack(anchor="w")

            ctk.CTkButton(
                card,
                text="Connect",
                width=120,
                height=36,
                command=lambda ip=device_ip: self._connect_to_host(ip, DEFAULT_PORT),
            ).pack(side="right", padx=15, pady=12)

    def _scan_error(self, error: str) -> None:
        self._scanning = False
        self.scan_btn.configure(state="normal", text="Scan Network")
        self.status_var.set(f"Scan failed: {error}")

    def _connect_to_host(self, ip: str, port: int) -> None:
        connected = False
        if self.on_connect:
            connected = self.on_connect(ip, port)
        elif self._connection_manager is not None:
            connected = self._connection_manager.connect_to_host(ip, port)

        self.status_var.set(f"Connected to {ip}:{port}" if connected else f"Connection failed to {ip}:{port}")

    def _manual_connect(self) -> None:
        host = self.ip_entry.get().strip()
        port_text = self.port_entry.get().strip()

        if not host:
            self.status_var.set("Enter a host or IP address first.")
            return

        try:
            port = int(port_text) if port_text else DEFAULT_PORT
        except ValueError:
            self.status_var.set("Port must be a number.")
            return

        self._connect_to_host(host, port)

    def refresh_connections(self) -> None:
        self._refresh_host_info()
        self.scan_network()
