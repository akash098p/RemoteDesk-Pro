"""
===============================================================================
RemoteDesk Pro
File: gui/pages/connection.py
Connection management page with premium glassmorphism UI
===============================================================================
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
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Network Connections",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Manage and connect to remote devices securely",
            font=ctk.CTkFont(size=14),
            text_color=("#A0A0A0", "#666666")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Status bar
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(fill="x", padx=30, pady=10)
        
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="● Disconnected",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#EF4444"
        )
        self.status_indicator.pack(side="left")
        
        self.status_time = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=("#A0A0A0", "#666666")
        )
        self.status_time.pack(side="right")
        
        # Control bar
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=30, pady=15)
        
        self.scan_btn = ctk.CTkButton(
            controls_frame,
            image=ctk.CTkImage(light_image=load_icon("search.png", size=(20,20)),
                              dark_image=load_icon("search.png", size=(20,20)),
                              size=(20,20)),
            text="Scan Network",
            command=self.scan_network,
            width=180,
            height=40,
            corner_radius=12
        )
        self.scan_btn.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_connections,
            width=120,
            height=40,
            corner_radius=12
        )
        refresh_btn.pack(side="left", padx=(10, 0))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Search devices...",
            width=250,
            height=40,
            corner_radius=12
        )
        self.search_entry.pack(side="right", padx=(10, 0))
        
        # Devices section
        list_frame = ctk.CTkFrame(
            self,
            fg_color=("gray15", "gray85"),
            corner_radius=15,
            border_width=0
        )
        list_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # List header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Available Devices",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(anchor="w")
        
        # Scrollable content
        self.list_container = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        connect_all_btn = ctk.CTkButton(
            btn_frame,
            text="🔗 Connect Selected",
            command=self._connect_selected,
            width=180,
            height=45,
            corner_radius=12
        )
        connect_all_btn.pack(side="left")
        
        # Manual connection section
        manual_frame = ctk.CTkFrame(
            self,
            fg_color=("gray15", "gray85"),
            corner_radius=15,
            border_width=0
        )
        manual_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        manual_label = ctk.CTkLabel(
            manual_frame,
            text="Manual Connection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        manual_label.pack(anchor="w", padx=20, pady=(15, 10))
        
        manual_inputs = ctk.CTkFrame(manual_frame, fg_color="transparent")
        manual_inputs.pack(fill="x", padx=20, pady=(0, 20))
        
        self.manual_ip = ctk.CTkEntry(
            manual_inputs,
            placeholder_text="IP Address",
            width=200,
            height=40,
            corner_radius=12
        )
        self.manual_ip.pack(side="left", padx=(0, 10))
        
        self.manual_port = ctk.CTkEntry(
            manual_inputs,
            placeholder_text="Port",
            width=100,
            height=40,
            corner_radius=12
        )
        self.manual_port.pack(side="left", padx=(0, 10))
        
        manual_connect_btn = ctk.CTkButton(
            manual_inputs,
            text="Connect",
            width=100,
            height=40,
            corner_radius=12,
            command=self._manual_connect
        )
        manual_connect_btn.pack(side="left")
    
    def _update_status(self, message: str, color: str):
        """Update the status indicator."""
        self.status_indicator.configure(text=f"● {message}", text_color=color)
        self.status_time.configure(text=datetime.now().strftime("%H:%M:%S"))
    
    def scan_network(self):
        """Scan local network for devices."""
        if self._scanning:
            return
            
        self._scanning = True
        self._update_status("Scanning...", "#F59E0B")
        self.scan_btn.configure(text="Scanning...", state="disabled")
        
        def _scan():
            time.sleep(1.5)  # Simulate scan time
            self.after(0, self.refresh_connections)
        
        thread = threading.Thread(target=_scan, daemon=True)
        thread.start()
    
    def refresh_connections(self):
        """Refresh the connection list."""
        # Clear existing widgets
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        # Sample connections for demo
        sample_connections = [
            {"name": "John's Laptop", "ip": "192.168.1.10", "status": "online", "last_seen": "2 min ago"},
            {"name": "Sarah's Desktop", "ip": "192.168.1.15", "status": "offline", "last_seen": "1 hour ago"},
            {"name": "Office Workstation", "ip": "192.168.1.20", "status": "online", "last_seen": "Just now"},
            {"name": "Home Server", "ip": "192.168.1.50", "status": "online", "last_seen": "5 min ago"},
        ]
        
        for conn in sample_connections:
            self._add_connection_card(conn)
        
        self._scanning = False
        self.scan_btn.configure(text="🌐 Scan Network", state="normal")
        self._update_status("Ready", "#10B981")
    
    def _add_connection_card(self, connection: dict):
        """Add a connection card to the list."""
        # Card container
        card = ctk.CTkFrame(
            self.list_container,
            fg_color=("gray15", "gray85"),
            corner_radius=12,
            border_width=1,
            border_color=("#404040", "#DDDDDD")
        )
        card.pack(fill="x", pady=8)
        
        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Device info
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=connection["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        ip_label = ctk.CTkLabel(
            info_frame,
            text=f"{connection['ip']} • {connection['last_seen']}",
            font=ctk.CTkFont(size=11),
            text_color=("#A0A0A0", "#666666"),
            anchor="w"
        )
        ip_label.pack(anchor="w", pady=(2, 0))
        
        # Status badge
        status_color = "#10B981" if connection["status"] == "online" else "#EF4444"
        status_text = "● Online" if connection["status"] == "online" else "● Offline"
        
        status_badge = ctk.CTkLabel(
            content_frame,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color
        )
        status_badge.pack(side="right", padx=(10, 15))
        
        # Connect button
        connect_btn = ctk.CTkButton(
            content_frame,
            text="Connect",
            width=90,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            command=lambda: self._connect_device(connection)
        )
        connect_btn.pack(side="right", padx=(5, 15))
    
    def _connect_device(self, device: dict):
        """Connect to a device."""
        self._update_status(f"Connecting to {device['name']}...", "#F59E0B")
        
        if self.on_connect:
            self.on_connect(device)
        
        self._update_status(f"Connected to {device['name']}", "#10B981")
    
    def _connect_selected(self):
        """Connect to selected devices."""
        self._update_status("Connecting selected...", "#F59E0B")
        # Implementation for connecting to multiple devices
    
    def _manual_connect(self):
        """Manual IP/Port connection."""
        ip = self.manual_ip.get().strip()
        port = self.manual_port.get().strip() or "5000"
        
        if not ip:
            self._update_status("Enter IP address", "#EF4444")
            return
        
        self._update_status(f"Connecting to {ip}:{port}...", "#F59E0B")
        
        # Simulate connection
        self.after(1000, lambda: self._update_status(f"Connected to {ip}:{port}", "#10B981"))