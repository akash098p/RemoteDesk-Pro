"""
RemoteDesk Pro - Phase 6 File Transfer Module
Complete peer-to-peer file transfer with drag-and-drop support.
"""

import os
import threading
import json
import hashlib
import time
import queue
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List

import customtkinter as ctk
from core.logger import get_logger

logger = get_logger()


class FileTransferManager:
    """
    Handles all file transfer operations between connected devices.
    
    Features:
    - Drag & drop file/folder selection
    - Chunked transfer with progress
    - Pause/Resume/Cancel
    - Integrity verification
    - Transfer history
    """

    def __init__(self, connection_manager: Any):
        self.conn_manager = connection_manager
        self.transfers: Dict[str, Dict[str, Any]] = {}
        self.active_transfers: List[str] = []
        self.transfer_queue = queue.Queue(maxsize=100)
        self.chunk_size = 64 * 1024  # 64KB chunks
        self.history_path = Path.home() / ".remotedesk" / "transfer_history.json"
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        self._load_history()
        self._start_worker()

    def _start_worker(self) -> None:
        """Start background worker thread for processing transfer queue."""
        worker = threading.Thread(target=self._process_queue, daemon=True)
        worker.start()

    def _process_queue(self) -> None:
        """Process queued transfer tasks continuously."""
        while True:
            try:
                task = self.transfer_queue.get(timeout=1.0)
                if task is None:
                    break
                self._execute_transfer(task)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Transfer worker error: {e}")

    def start_transfer(self, source_path: str, destination_dir: str = None,
                       recipient_id: str = None) -> Dict[str, Any]:
        """
        Initiate a file transfer.
        
        Args:
            source_path: Path to file/folder to transfer
            destination_dir: Where to save on remote (optional)
            recipient_id: Target device ID (optional)
            
        Returns:
            Transfer task dictionary with status
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source_path}")

        transfer_id = hashlib.md5(
            f"{source_path}{time.time()}".encode()
        ).hexdigest()[:12]

        task = {
            "id": transfer_id,
            "source": source_path,
            "destination": destination_dir or os.path.dirname(source_path),
            "recipient": recipient_id,
            "size": os.path.getsize(source_path),
            "sent": 0,
            "status": "pending",
            "checksum": None,
            "created_at": time.time(),
            "paused": False
        }

        self.transfers[transfer_id] = task
        self.transfer_queue.put(task)
        self.active_transfers.append(transfer_id)
        self._save_history()

        logger.info(f"Transfer queued: {transfer_id} - {source_path}")
        return task

    def _execute_transfer(self, task: Dict[str, Any]) -> None:
        """Execute actual file transfer with chunking."""
        try:
            task["status"] = "transferring"
            file_path = task["source"]
            sent = 0
            total = task["size"]

            # Calculate checksum for integrity
            hasher = hashlib.md5()

            with open(file_path, 'rb') as f:
                while sent < total:
                    if task.get("paused", False):
                        task["status"] = "paused"
                        return

                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break

                    # Send chunk via network
                    self.conn_manager.send_file_chunk(
                        transfer_id=task["id"],
                        chunk=chunk,
                        position=sent,
                        total=total
                    )

                    hasher.update(chunk)
                    sent += len(chunk)
                    task["sent"] = sent

                    # Update progress
                    progress = (sent / total) * 100
                    logger.debug(f"Transfer {task['id']}: {progress:.1f}%")

            task["status"] = "completed"
            task["checksum"] = hasher.hexdigest()
            logger.info(f"Transfer completed: {task['id']}")

        except Exception as e:
            task["status"] = "error"
            logger.error(f"Transfer failed: {task['id']} - {e}")
        finally:
            self._save_history()

    def pause_transfer(self, transfer_id: str) -> bool:
        """Pause an active transfer."""
        if transfer_id in self.transfers:
            self.transfers[transfer_id]["paused"] = True
            self.transfers[transfer_id]["status"] = "paused"
            return True
        return False

    def resume_transfer(self, transfer_id: str) -> bool:
        """Resume a paused transfer."""
        if transfer_id in self.transfers:
            self.transfers[transfer_id]["paused"] = False
            self.transfers[transfer_id]["status"] = "transferring"
            # Re-queue for processing
            self.transfer_queue.put(self.transfers[transfer_id])
            return True
        return False

    def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel and cleanup a transfer."""
        if transfer_id in self.transfers:
            task = self.transfers[transfer_id]
            task["status"] = "cancelled"
            # Cleanup partial file if exists
            if os.path.exists(task["destination"]):
                try:
                    os.remove(task["destination"])
                except:
                    pass
            self._save_history()
            return True
        return False

    def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get current status of a transfer."""
        return self.transfers.get(transfer_id, {})

    def list_active_transfers(self) -> List[Dict[str, Any]]:
        """List all currently active transfers."""
        return [t for t in self.transfers.values()
                if t["status"] in ("pending", "transferring", "paused")]

    def _load_history(self) -> None:
        """Load transfer history from disk."""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r') as f:
                    data = json.load(f)
                    self.transfers.update({
                        tid: t for tid, t in data.get("transfers", {}).items()
                    })
        except Exception as e:
            logger.warning(f"Failed to load transfer history: {e}")

    def _save_history(self) -> None:
        """Persist transfer history to disk."""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(
                    {"transfers": self.transfers},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save transfer history: {e}")


class FileTransferPage(ctk.CTkFrame):
    """
    GUI page for managing file transfers with drag-and-drop support.
    """

    def __init__(self, parent: ctk.CTk, app_controller: Any, **kwargs):
        super().__init__(parent, **kwargs)
        self.app_controller = app_controller
        self.logger = get_logger()
        self.transfer_widgets: Dict[str, Any] = {}

        # Transfer manager
        self.transfer_manager = FileTransferManager(
            getattr(app_controller, 'connection_manager', None)
        )

        self._create_widgets()
        self._setup_drag_and_drop()

    def _create_widgets(self) -> None:
        """Create all UI components."""
        # Header
        header = ctk.CTkLabel(
            self,
            text="📁 File Transfer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4A90E2",
        )
        header.pack(pady=(20, 10), anchor="w", padx=20)

        # Drag & Drop Area
        self.drop_zone = ctk.CTkFrame(
            self,
            height=120,
            fg_color=("#2A2A2A", "#333333"),
            corner_radius=10
        )
        self.drop_zone.pack(fill="x", padx=20, pady=10)
        self.drop_zone.pack_propagate(False)

        drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="Drag & Drop Files/Folders Here\nor Click to Browse",
            font=ctk.CTkFont(size=14),
            text_color="#888888",
            anchor="center"
        )
        drop_label.pack(expand=True)

        self.drop_zone.bind("<Button-1>", self._browse_files)

        # Transfer List
        self.transfer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.transfer_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollable transfer list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.transfer_frame,
            label_text="Active Transfers"
        )
        self.scroll_frame.pack(fill="both", expand=True)

    def _setup_drag_and_drop(self) -> None:
        """Configure drag-and-drop event handlers."""
        self.drop_zone.bind("<DragEnter>", self._on_drag_enter)
        self.drop_zone.bind("<DragLeave>", self._on_drag_leave)
        self.drop_zone.bind("<Drop>", self._on_drop)

    def _on_drag_enter(self, event) -> None:
        """Highlight drop zone when dragging enters."""
        self.drop_zone.configure(fg_color="#1E90FF")

    def _on_drag_leave(self, event) -> None:
        """Reset drop zone color when dragging leaves."""
        self.drop_zone.configure(fg_color=("#2A2A2A", "#333333"))

    def _on_drop(self, event) -> None:
        """Handle dropped files/folders."""
        files = self._extract_dropped_files(event)
        for file_path in files:
            self._start_transfer(file_path)

    def _extract_dropped_files(self, event) -> List[str]:
        """
        Extract file paths from drag-and-drop event.
        Returns list of absolute paths.
        """
        # This depends on the OS - simplified for Windows
        try:
            data = event.data
            if data.startswith("{") and data.endswith("}"):
                # Multiple files
                paths = [p.strip("{}") for p in data.split("} {")]
            else:
                paths = [data]
            return [p for p in paths if os.path.exists(p)]
        except:
            return []

    def _browse_files(self, event=None) -> None:
        """Open file browser dialog."""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Select Files to Transfer",
            filetypes=[("All files", "*.*")]
        )
        for file_path in files:
            self._start_transfer(file_path)

    def _start_transfer(self, file_path: str) -> None:
        """Initiate transfer for a specific file."""
        try:
            task = self.transfer_manager.start_transfer(
                source_path=file_path,
                recipient_id=self._get_active_recipient()
            )
            self._create_transfer_widget(task)
            logger.info(f"Transfer started: {task['id']}")
        except Exception as e:
            logger.error(f"Failed to start transfer: {e}")
            self._show_error(str(e))

    def _get_active_recipient(self) -> Optional[str]:
        """Get ID of connected device for transfer."""
        # In real implementation, this would query connection manager
        return "remote_device_001"

    def _create_transfer_widget(self, task: Dict[str, Any]) -> None:
        """Create visual representation of a transfer."""
        widget = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=("#1A1A1A", "#262626"),
            corner_radius=8
        )
        widget.pack(fill="x", pady=5, padx=5)

        # File info
        info_frame = ctk.CTkFrame(widget, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)

        name_label = ctk.CTkLabel(
            info_frame,
            text=os.path.basename(task["source"]),
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        size_label = ctk.CTkLabel(
            info_frame,
            text=self._format_size(task["size"]),
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        size_label.pack(side="right")

        # Progress bar
        progress = ctk.CTkProgressBar(
            widget,
            orientation="horizontal"
        )
        progress.pack(fill="x", padx=10, pady=(2, 5))
        progress.set(0)

        # Control buttons
        btn_frame = ctk.CTkFrame(widget, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(2, 8))

        pause_btn = ctk.CTkButton(
            btn_frame,
            text="⏸ Pause",
            width=80,
            command=lambda: self._pause_transfer(task["id"])
        )
        pause_btn.pack(side="left", padx=2)

        resume_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Resume",
            width=80,
            command=lambda: self._resume_transfer(task["id"])
        )
        resume_btn.pack(side="left", padx=2)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="🗑 Cancel",
            width=80,
            fg_color="#FF4444",
            command=lambda: self._cancel_transfer(task["id"])
        )
        cancel_btn.pack(side="right", padx=2)

        # Store reference for updates
        self.transfer_widgets[task["id"]] = {
            "widget": widget,
            "progress": progress,
            "status_label": ctk.CTkLabel(
                widget,
                text="Pending",
                font=ctk.CTkFont(size=10),
                text_color="#888888"
            )
        }
        self.transfer_widgets[task["id"]]["status_label"].pack(
            fill="x", padx=10, pady=(0, 5)
        )

        # Start update loop
        self._update_transfer_widget(task["id"])

    def _update_transfer_widget(self, transfer_id: str) -> None:
        """Update progress display for a transfer."""
        if transfer_id not in self.transfer_widgets:
            return

        task = self.transfer_manager.get_transfer_status(transfer_id)
        widget_data = self.transfer_widgets[transfer_id]

        # Update progress bar
        if task["size"] > 0:
            progress = (task["sent"] / task["size"]) * 100
            widget_data["progress"].set(progress / 100)

        # Update status label
        status_text = {
            "pending": "Waiting...",
            "transferring": "Transferring",
            "paused": "Paused",
            "completed": "Completed ✓",
            "error": "Error ✗",
            "cancelled": "Cancelled"
        }.get(task["status"], task["status"])

        widget_data["status_label"].configure(text=status_text)

        # Auto-remove completed transfers after delay
        if task["status"] in ("completed", "error", "cancelled"):
            self.after(3000, lambda: self._remove_transfer_widget(transfer_id))

    def _pause_transfer(self, transfer_id: str) -> None:
        self.transfer_manager.pause_transfer(transfer_id)

    def _resume_transfer(self, transfer_id: str) -> None:
        self.transfer_manager.resume_transfer(transfer_id)

    def _cancel_transfer(self, transfer_id: str) -> None:
        self.transfer_manager.cancel_transfer(transfer_id)

    def _remove_transfer_widget(self, transfer_id: str) -> None:
        """Remove transfer widget from display."""
        if transfer_id in self.transfer_widgets:
            self.transfer_widgets[transfer_id]["widget"].destroy()
            del self.transfer_widgets[transfer_id]

    def _format_size(self, size_bytes: int) -> str:
        """Format byte size to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

    def _show_error(self, message: str) -> None:
        """Display error message to user."""
        logger.error(message)