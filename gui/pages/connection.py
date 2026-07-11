"""
=================================================================================
RemoteDesk Pro
File: gui/pages/connection.py
Connection management page with premium glassmorphism UI
=================================================================================
"""

from __future__ import annotations

import customtkinter as ctk
import socket
import threading
import time
import os
from datetime import datetime
from typing import Optional, Callable
from PIL import Image

# Icon helper
ICONS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons')
)

def load_icon(icon_name: str, size: tuple = (24, 24)) -> Image.Image:
    icon_path = os.path.join(ICONS_DIR, icon_name)
    if os.path.exists(icon_path):
        return Image.open(icon_path).resize(size, Image.Resampling.LANCZOS)
    return None


class ConnectionPage(ctk.CTkFrame):
    """
    Modern connection management page with premium glassmorphism UI.
    """

    def __init__(self, master, on_connect: Optional[Callable] = None):
        super().__init__(master)
        self.on_connect = on_connect
        self._connections = []
        self._scan_results = []
        self._scanning = False

        self._create_widgets()
        self.refresh_connections()

    def _create_widgets(self):
        """Create the connection page UI with glassmorphism styling."""
        # Header section
        header_frame = ctk.CTkFrame(
            self,
            fg_color=("#1E1E1E", "#252525"),
            corner_radius=8,
            border_width=1,
            border_color=("#333333", "#555555")
        )
        header_frame.pack(fill="x", padx=20, pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Network Connections",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Manage and connect to remote devices securely",
            font=ctk.CTkFont(size=14),
            text_color=("#CCCCCC", "#AAAAAA")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))

        # Device list section
        list_frame = ctk.CTkFrame(
            self,
            fg_color=("#1A1A1A", "#2A2A2A"),
            corner_radius=12,
            border_width=1,
            border_color=("#333333", "#555555")
        )
        list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Section header
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            list_header,
            text="Available Devices",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        ).pack(side="left")

        # Scan button - icon only
        controls_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        controls_frame.pack(side="right")

        scan_icon = load_icon("search.png", size=(20, 20))
        if scan_icon:
            scan_img = ctk.CTkImage(light_image=scan_icon, dark_image=scan_icon, size=(20, 20))
            self.scan_btn = ctk.CTkButton(
                controls_frame,
                image=scan_img,
                text="",
                command=self.scan_network,
                width=44,
                height=44,
                corner_radius=22,
                fg_color=("#0084FF", "#0084FF"),
                hover_color=("#0073E6", "#0073E6")
            )
        else:
            self.scan_btn = ctk.CTkButton(
                controls_frame,
                text="🔍",
                command=self.scan_network,
                width=44,
                height=44,
                corner_radius=22,
                fg_color=("#0084FF", "#0084FF"),
                hover_color=("#0073E6", "#0073E6")
            )
        self.scan_btn.pack(side="left", padx=5)

        # Device list
        self.device_scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            height=300
        )
        self.device_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Placeholder text
        self.placeholder = ctk.CTkLabel(
            self.device_scroll,
            text="No devices found. Click the search button to scan your network.",
            font=ctk.CTkFont(size=14),
            text_color=("#888888", "#888888")
        )
        self.placeholder.pack(pady=50)

        # Manual connection section
        manual_frame = ctk.CTkFrame(
            self,
            fg_color=("#1A1A1A", "#2A2A2A"),
            corner_radius=12,
            border_width=1,
            border_color=("#333333", "#555555")
        )
        manual_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(
            manual_frame,
            text="Manual Connection",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            manual_frame,
            text="Enter IP address to connect directly to a device",
            font=ctk.CTkFont(size=12),
            text_color=("#AAAAAA", "#888888")
        ).pack(anchor="w", padx=20, pady=(0, 15))

        input_frame = ctk.CTkFrame(manual_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.ip_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="IP Address (e.g., 192.168.1.100)",
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=10,
            width=300
        )
        self.ip_entry.pack(side="left", padx=(0, 10))

        self.port_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Port (default: 5555)",
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=10,
            width=120
        )
        self.port_entry.pack(side="left", padx=(0, 10))

        connect_btn = ctk.CTkButton(
            input_frame,
            text="Connect",
            command=self._manual_connect,
            width=140,
            height=44,
            corner_radius=10,
            fg_color=("#0084FF", "#0084FF"),
            hover_color=("#0073E6", "#0073E6")
        )
        connect_btn.pack(side="left")

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkFrame(self, fg_color="transparent", height=30)
        status_bar.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(
            status_bar,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color=("#AAAAAA", "#888888")
        ).pack(side="left")

    def scan_network(self):
        """Scan local network for devices running RemoteDesk Pro."""
        if self._scanning:
            return

        self._scanning = True
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_var.set("Scanning network...")

        # Clear previous results
        for widget in self.device_scroll.winfo_children():
            widget.destroy()

        self.placeholder = ctk.CTkLabel(
            self.device_scroll,
            text="Scanning network...",
            font=ctk.CTkFont(size=14),
            text_color=("#888888", "#888888")
        )
        self.placeholder.pack(pady=50)

        # Run scan in background thread
        threading.Thread(target=self._scan_network_thread, daemon=True).start()

    def _scan_network_thread(self):
        """Background thread for network scanning."""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Scan local subnet
            base_ip = ".".join(local_ip.split(".")[:3])
            found_devices = []

            def check_ip(ip):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)
                    result = sock.connect_ex((ip, 5555))
                    sock.close()
                    if result == 0:
                        found_devices.append(ip)
                except Exception:
                    pass

            threads = []
            for i in range(1, 255):
                ip = f"{base_ip}.{i}"
                if ip != local_ip:
                    t = threading.Thread(target=check_ip, args=(ip,))
                    threads.append(t)
                    t.start()

            for t in threads:
                t.join()

            # Update UI on main thread
            self.after(0, lambda: self._update_device_list(found_devices))

        except Exception as e:
            self.after(0, lambda: self._scan_error(str(e)))

    def _update_device_list(self, devices):
        """Update the device list with scan results."""
        for widget in self.device_scroll.winfo_children():
            widget.destroy()

        self._scan_results = devices
        self._scanning = False
        self.scan_btn.configure(state="normal", text="Scan Network")
        self.status_var.set(f"Scan complete. Found {len(devices)} device(s).")

        if not devices:
            self.placeholder = ctk.CTkLabel(
                self.device_scroll,
                text="No devices found on network. Ensure devices are running RemoteDesk Pro.",
                font=ctk.CTkFont(size=14),
                text_color=("#888888", "#888888")
            )
            self.placeholder.pack(pady=50)
            return

        for device_ip in devices:
            card = ctk.CTkFrame(
                self.device_scroll,
                fg_color=("#1E1E1E", "#2A2A2A"),
                corner_radius=10,
                border_width=1,
                border_color=("#333333", "#555555")
            )
            card.pack(fill="x", pady=8, padx=10)

            # Device info
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=12)

            ctk.CTkLabel(
                info_frame,
                text="🖥️",
                font=ctk.CTkFont(size=24)
            ).pack(side="left", padx=(0, 15))

            details = ctk.CTkFrame(info_frame, fg_color="transparent")
            details.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(
                details,
                text="RemoteDesk Pro Device",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#FFFFFF", "#FFFFFF")
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=f"IP: {device_ip} • Port: 5555",
                font=ctk.CTkFont(size=12),
                text_color=("#AAAAAA", "#888888")
            ).pack(anchor="w")

            # Connect button
            connect_btn = ctk.CTkButton(
                card,
                text="Connect",
                command=lambda ip=device_ip: self._connect_to_device(ip),
                width=120,
                height=36,
                corner_radius=8,
                fg_color=("#0084FF", "#0084FF"),
                hover_color=("#0073E6", "#0073E6")
            )
            connect_btn.pack(side="right", padx=15, pady=12)

    def _scan_error(self, error):
        """Handle scan errors."""
        self._scanning = False
        self.scan_btn.configure(state="normal")
        self.status_var.set(f"Scan error: {error}")

    def _connect_to_device(self, ip):
        """Connect to a scanned device."""
        if self.on_connect:
            self.on_connect(ip, 5555)
        self.status_var.set(f"Connecting to {ip}...")

    def _manual_connect(self):
        """Handle manual connection."""
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if not ip:
            self.status_var.set("Error: Please enter an IP address")
            return

        try:
            port_num = int(port) if port else 5555
        except ValueError:
            self.status_var.set("Error: Invalid port number")
            return

        if self.on_connect:
            self.on_connect(ip, port_num)
        self.status_var.set(f"Connecting to {ip}:{port_num}...")

    def refresh_connections(self):
        """Refresh the connection list."""
        self.scan_network()