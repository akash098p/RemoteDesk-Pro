"""
RemoteDesk Pro - Phase 6 File Transfer Module
Complete peer-to-peer file transfer with drag-and-drop support.
"""

import os
import threading
import base64
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

    def __init__(self, connection_manager: Any, download_dir: Optional[str] = None):
        self.conn_manager = connection_manager
        self.transfers: Dict[str, Dict[str, Any]] = {}
        self.active_transfers: List[str] = []
        self.transfer_queue = queue.Queue(maxsize=100)
        self.chunk_size = 64 * 1024  # 64KB chunks
        self.history_path = Path.home() / ".remotedesk" / "transfer_history.json"
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

        self.download_dir = Path(download_dir or (Path.home() / "Downloads"))
        self.incoming: Dict[str, Dict[str, Any]] = {}
        # Optional UI hook: called with a transfer task whenever its state changes.
        self.on_transfer_update: Optional[Callable[[Dict[str, Any]], None]] = None

        self._load_history()
        self._start_worker()

    # ------------------------------------------------------------- receiving
    def handle_file_meta(self, payload: Dict[str, Any]) -> None:
        """Track an incoming transfer announcement or completion notice."""
        transfer_id = payload.get("transfer_id")
        if not transfer_id:
            return

        action = payload.get("action", "start")

        if action == "start":
            self.incoming[transfer_id] = {
                "id": transfer_id,
                "file_name": os.path.basename(str(payload.get("file_name", "received_file"))),
                "size": int(payload.get("file_size", 0)),
                "received": 0,
                "status": "transferring",
                "direction": "incoming",
                "is_image": bool(payload.get("is_image")),
                "relative_path": payload.get("relative_path"),
                "created_at": time.time(),
                "sender": payload.get("sender", "Remote device"),
            }
            logger.info(f"Incoming transfer {transfer_id} ({payload.get('file_name')})")
        elif action in ("complete", "abort"):
            entry = self.incoming.get(transfer_id)
            if entry is not None:
                entry["status"] = "completed" if action == "complete" else "cancelled"
                entry["checksum"] = payload.get("checksum")
        self._notify(transfer_id)

    def handle_file_chunk(self, payload: Dict[str, Any]) -> None:
        """Write an incoming file chunk to the download folder."""
        transfer_id = payload.get("transfer_id")
        encoded = payload.get("chunk")
        if not transfer_id or not encoded:
            return

        entry = self.incoming.get(transfer_id)
        if entry is None:
            # A chunk without metadata: create a placeholder entry so the data
            # is still saved instead of being dropped silently.
            entry = {
                "id": transfer_id,
                "file_name": f"received_{transfer_id}",
                "size": int(payload.get("total", 0)),
                "received": 0,
                "status": "transferring",
                "direction": "incoming",
                "is_image": False,
                "relative_path": payload.get("relative_path"),
                "created_at": time.time(),
                "sender": "Remote device",
            }
            self.incoming[transfer_id] = entry

        try:
            chunk = base64.b64decode(encoded)
        except Exception as exc:
            logger.error(f"Invalid chunk for {transfer_id}: {exc}")
            entry["status"] = "error"
            self._notify(transfer_id)
            return

        target = self._incoming_path(entry)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "ab") as file_handle:
                file_handle.write(chunk)
        except Exception as exc:
            logger.error(f"Failed to store chunk for {transfer_id}: {exc}")
            entry["status"] = "error"
            self._notify(transfer_id)
            return

        entry["received"] = entry.get("received", 0) + len(chunk)
        entry["path"] = str(target)
        if entry.get("size") and entry["received"] >= entry["size"]:
            entry["status"] = "completed"
        self._notify(transfer_id)

    def _incoming_path(self, entry: Dict[str, Any]) -> Path:
        """Resolve a safe destination path for an incoming transfer."""
        relative = str(entry.get("relative_path") or entry.get("file_name") or "received_file")
        safe_parts = [
            part for part in Path(relative).parts
            if part not in ("", ".", "..") and not Path(part).is_absolute()
        ]
        if not safe_parts:
            safe_parts = [f"received_{entry.get('id', 'file')}"]
        return self.download_dir.joinpath(*safe_parts)

    def _notify(self, transfer_id: str) -> None:
        """Notify the UI about an incoming/outgoing transfer update."""
        if self.on_transfer_update is None:
            return
        task = self.incoming.get(transfer_id) or self.transfers.get(transfer_id)
        if task is None:
            return
        try:
            self.on_transfer_update(task)
        except Exception as exc:
            logger.debug(f"Transfer update callback failed: {exc}")

    def list_incoming(self) -> List[Dict[str, Any]]:
        """Return all received transfers."""
        return list(self.incoming.values())

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
                       recipient_id: str = None,
                       relative_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate a file transfer.
        
        Args:
            source_path: Path to file/folder to transfer
            destination_dir: Where to save on remote (optional)
            recipient_id: Target device ID (optional)
            relative_path: Folder-aware path used to rebuild folders remotely
                           (must be supplied here; setting it after this call
                           races with the worker thread that sends the meta)
            
        Returns:
            Transfer task dictionary with status
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source not found: {source_path}")

        if os.path.isdir(source_path):
            raise IsADirectoryError(
                f"{source_path} is a folder. Use start_folder_transfer() to queue folders."
            )

        transfer_id = hashlib.md5(
            f"{source_path}{time.time()}".encode()
        ).hexdigest()[:12]

        task = {
            "id": transfer_id,
            "source": source_path,
            "file_name": os.path.basename(source_path),
            "relative_path": relative_path or os.path.basename(source_path),
            "destination": destination_dir or os.path.basename(source_path),
            "recipient": recipient_id,
            "size": os.path.getsize(source_path),
            "sent": 0,
            "status": "pending",
            "checksum": None,
            "created_at": time.time(),
            "paused": False,
            "is_image": self._is_image(source_path),
            "direction": "outgoing",
        }

        self.transfers[transfer_id] = task
        self.transfer_queue.put(task)
        self.active_transfers.append(transfer_id)
        self._save_history()

        logger.info(f"Transfer queued: {transfer_id} - {source_path}")
        return task

    def start_folder_transfer(
        self,
        folder_path: str,
        destination_dir: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Queue every file inside a folder, keeping the folder structure.

        Args:
            folder_path: Folder to send
            destination_dir: Remote folder that will hold the folder contents
            recipient_id: Target device ID (optional)

        Returns:
            The list of queued transfer task dictionaries
        """
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Not a folder: {folder_path}")

        root_name = os.path.basename(os.path.normpath(folder_path))
        queued: List[Dict[str, Any]] = []

        for current_root, _dir_names, file_names in os.walk(folder_path):
            for file_name in file_names:
                full_path = os.path.join(current_root, file_name)
                relative_path = os.path.relpath(full_path, folder_path)
                task = self.start_transfer(
                    full_path,
                    destination_dir=destination_dir or root_name,
                    recipient_id=recipient_id,
                    # Keep the folder structure so nested folders can be rebuilt.
                    relative_path=os.path.join(root_name, relative_path),
                )
                queued.append(task)

        logger.info(f"Queued {len(queued)} file(s) from folder {folder_path}")
        return queued

    @staticmethod
    def _is_image(path: str) -> bool:
        """Return True when the file looks like an image that can be previewed."""
        return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    def _execute_transfer(self, task: Dict[str, Any]) -> None:
        """Execute a file transfer with chunking, progress and integrity checks."""
        if self.conn_manager is None or not self.conn_manager.has_active_session():
            task["status"] = "error"
            task["error"] = "No active session. Connect to a device before sending files."
            logger.warning(f"Transfer {task['id']} skipped: no active session")
            self._save_history()
            self._notify(task["id"])
            return

        file_path = task["source"]
        total = task["size"]
        try:
            task["status"] = "transferring"
            task["error"] = None
            self._notify(task["id"])

            # Announce the transfer so the receiver can prepare the file.
            self.conn_manager.send_file_meta(
                transfer_id=task["id"],
                file_name=task.get("file_name") or os.path.basename(file_path),
                file_size=total,
                action="start",
                is_image=bool(task.get("is_image")),
                relative_path=task.get("relative_path"),
            )

            # Resume from wherever we stopped so pause/resume never duplicates data.
            sent = int(task.get("sent", 0))
            hasher = hashlib.md5()

            with open(file_path, "rb") as file_handle:
                if sent:
                    # Re-read (and hash) the already delivered prefix so the
                    # checksum still describes the complete file after a resume.
                    remaining_prefix = sent
                    while remaining_prefix > 0:
                        prefix = file_handle.read(min(self.chunk_size, remaining_prefix))
                        if not prefix:
                            break
                        hasher.update(prefix)
                        remaining_prefix -= len(prefix)
                    file_handle.seek(sent)
                while sent < total:
                    if task.get("paused", False):
                        task["status"] = "paused"
                        self._notify(task["id"])
                        return

                    chunk = file_handle.read(self.chunk_size)
                    if not chunk:
                        break

                    if not self.conn_manager.send_file_chunk(
                        transfer_id=task["id"],
                        chunk=chunk,
                        position=sent,
                        total=total,
                    ):
                        task["status"] = "error"
                        task["error"] = "The connection dropped while sending chunks."
                        logger.error(f"Transfer {task['id']} aborted: send failed")
                        self._notify(task["id"])
                        return

                    hasher.update(chunk)
                    sent += len(chunk)
                    task["sent"] = sent

                    logger.debug(f"Transfer {task['id']}: {(sent / total) * 100:.1f}%")
                    self._notify(task["id"])

            task["status"] = "completed"
            task["checksum"] = hasher.hexdigest()
            self.conn_manager.send_file_meta(
                transfer_id=task["id"],
                file_name=task.get("file_name") or os.path.basename(file_path),
                file_size=total,
                action="complete",
                checksum=task["checksum"],
                relative_path=task.get("relative_path"),
            )
            logger.info(f"Transfer completed: {task['id']}")

        except Exception as e:
            task["status"] = "error"
            task["error"] = str(e)
            logger.error(f"Transfer failed: {task['id']} - {e}")
        finally:
            self._save_history()
            self._notify(task["id"])

    def pause_transfer(self, transfer_id: str) -> bool:
        """Pause an active transfer."""
        task = self.transfers.get(transfer_id) or self.incoming.get(transfer_id)
        if task is None:
            return False
        task["paused"] = True
        task["status"] = "paused"
        self._notify(transfer_id)
        return True

    def resume_transfer(self, transfer_id: str) -> bool:
        """Resume a paused transfer."""
        task = self.transfers.get(transfer_id)
        if task is None:
            return False
        task["paused"] = False
        task["status"] = "transferring"
        # Re-queue for processing; sending continues from task["sent"].
        self.transfer_queue.put(task)
        self._notify(transfer_id)
        return True

    def cancel_transfer(self, transfer_id: str) -> bool:
        """Cancel a transfer and remove any partially received file."""
        task = self.transfers.get(transfer_id)
        if task is not None:
            task["status"] = "cancelled"
            task["paused"] = False
            if self.conn_manager is not None and self.conn_manager.has_active_session():
                try:
                    self.conn_manager.send_file_meta(
                        transfer_id=transfer_id,
                        file_name=task.get("file_name") or os.path.basename(task["source"]),
                        file_size=task.get("size", 0),
                        action="abort",
                        relative_path=task.get("relative_path"),
                    )
                except Exception as exc:
                    logger.debug(f"Unable to notify peer about cancelled transfer: {exc}")
            self._save_history()
            self._notify(transfer_id)
            return True

        incoming = self.incoming.get(transfer_id)
        if incoming is not None:
            incoming["status"] = "cancelled"
            partial_path = incoming.get("path")
            if partial_path:
                try:
                    os.remove(partial_path)
                except OSError as exc:
                    logger.debug(f"Unable to remove partial download {partial_path}: {exc}")
            self._notify(transfer_id)
            return True

        return False

    def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """Get current status of a transfer."""
        return self.transfers.get(transfer_id) or self.incoming.get(transfer_id) or {}

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

    def __init__(self, master: Any, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.logger = get_logger()
        self.transfer_widgets: Dict[str, Any] = {}
        self._drop_target: Any = None

        # Transfer manager (uses the shared session when one is available)
        self.transfer_manager = FileTransferManager(
            self._connection_manager,
            download_dir=self._download_folder(),
        )
        self.transfer_manager.on_transfer_update = self._on_manager_update

        self._create_widgets()
        self._setup_drag_and_drop()

    @property
    def _connection_manager(self):
        """Connection manager shared by every page."""
        return getattr(self.master, "_connection_manager", None)

    def _download_folder(self) -> Optional[str]:
        """Resolve the configured download folder for incoming files."""
        app = getattr(self.master, "_app", None)
        config_manager = getattr(app, "config_manager", None)
        if config_manager is None:
            return None
        try:
            return config_manager.get_value("settings", "download_folder", None)
        except Exception:
            return None

    # ------------------------------------------------------- network plumbing
    def handle_file_meta(self, payload: Dict[str, Any], peer_id: Optional[str] = None) -> None:
        """Route incoming file metadata into the transfer manager."""
        self.transfer_manager.handle_file_meta(payload)

    def handle_file_chunk(self, payload: Dict[str, Any], peer_id: Optional[str] = None) -> None:
        """Route incoming file chunks into the transfer manager."""
        self.transfer_manager.handle_file_chunk(payload)

    def _on_manager_update(self, task: Dict[str, Any]) -> None:
        """Refresh the transfer list when the manager reports progress."""
        try:
            self.after(0, lambda: self._refresh_transfer_widget(task))
        except Exception:
            pass

    def _refresh_transfer_widget(self, task: Dict[str, Any]) -> None:
        """Create or update the widget that represents a transfer."""
        transfer_id = task.get("id")
        if not transfer_id:
            return
        if transfer_id not in self.transfer_widgets:
            self._create_transfer_widget(task)
            return
        self._update_transfer_widget(transfer_id)

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
            fg_color=("#EDEDED", "#333333"),
            corner_radius=10
        )
        self.drop_zone.pack(fill="x", padx=20, pady=10)
        self.drop_zone.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="Drag & Drop Files/Folders Here\nor use the buttons below",
            font=ctk.CTkFont(size=14),
            text_color=("#666666", "#A0A0A0"),
            anchor="center"
        )
        self.drop_label.pack(expand=True)
        self.drop_label.bind("<Button-1>", self._browse_files)
        self.drop_zone.bind("<Button-1>", self._browse_files)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 4))

        ctk.CTkButton(
            actions,
            text="Send Files",
            width=140,
            command=self._browse_files,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Send Folder",
            width=140,
            command=self._browse_folder,
        ).pack(side="left", padx=(0, 8))

        self.destination_label = ctk.CTkLabel(
            actions,
            text=f"Received files are saved to: {self.transfer_manager.download_dir}",
            font=ctk.CTkFont(size=11),
            text_color=("#666666", "#A0A0A0"),
            anchor="w",
        )
        self.destination_label.pack(side="left", padx=8)

        # Transfer List
        self.transfer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.transfer_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollable transfer list
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.transfer_frame,
            label_text="Transfers"
        )
        self.scroll_frame.pack(fill="both", expand=True)

        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No transfers yet. Send a file or wait for an incoming transfer.",
            font=ctk.CTkFont(size=12),
            text_color=("#777777", "#999999"),
        )
        self.empty_label.pack(pady=30)

    def _setup_drag_and_drop(self) -> None:
        """Enable native file drag-and-drop when the platform supports it."""
        from files.drag_drop import enable_file_drop

        self._drop_target = enable_file_drop(
            self,
            on_files=self._on_files_dropped,
            on_enter=lambda: self.drop_zone.configure(fg_color="#1E90FF"),
            on_leave=lambda: self.drop_zone.configure(fg_color=("#EDEDED", "#333333")),
        )
        if self._drop_target is None:
            # TkDnD is not installed: drag-and-drop stays disabled and users
            # pick files with the drop zone click or the Send buttons instead.
            self.drop_label.configure(
                text="Drag & Drop unavailable (tkdnd missing)\nor use the buttons below"
            )

    def _on_files_dropped(self, paths: List[str]) -> None:
        """Queue dropped files and folders for transfer."""
        for path in paths:
            self._start_transfer(path)

    def _browse_files(self, event=None) -> None:
        """Open file browser dialog."""
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            title="Select Files to Transfer",
            filetypes=[("All files", "*.*")]
        )
        for file_path in files:
            self._start_transfer(file_path)

    def _browse_folder(self, event=None) -> None:
        """Open folder browser dialog and queue every file inside it."""
        from tkinter import filedialog

        folder = filedialog.askdirectory(title="Select Folder to Transfer")
        if not folder:
            return
        try:
            tasks = self.transfer_manager.start_folder_transfer(
                folder_path=folder,
                recipient_id=self._get_active_recipient(),
            )
            for task in tasks:
                self._create_transfer_widget(task)
            logger.info(f"Queued folder transfer: {folder} ({len(tasks)} file(s))")
        except Exception as e:
            logger.error(f"Failed to start folder transfer: {e}")
            self._show_error(str(e))

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
        """Return the peer id of the active session, if any."""
        manager = self._connection_manager
        if manager is None or not manager.has_active_session():
            return None
        getter = getattr(manager, "get_active_peer_id", None)
        if callable(getter):
            try:
                return getter()
            except Exception:
                return None
        return None

    def _create_transfer_widget(self, task: Dict[str, Any]) -> None:
        """Create visual representation of a transfer."""
        if self.empty_label.winfo_exists():
            self.empty_label.pack_forget()
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
            text=task.get("file_name")
            or os.path.basename(str(task.get("source") or task.get("id", "file"))),
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        size_label = ctk.CTkLabel(
            info_frame,
            text=self._format_size(int(task.get("size", 0))),
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
        if not task:
            self._remove_transfer_widget(transfer_id)
            return

        # Update progress bar (incoming transfers track "received")
        total = int(task.get("size", 0))
        sent = int(task.get("sent", task.get("received", 0)))
        if total > 0:
            progress = (sent / total) * 100
            widget_data["progress"].set(progress / 100)

        # Update status label
        status_text = {
            "pending": "Waiting...",
            "transferring": "Transferring",
            "receiving": "Receiving",
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
        if not self.transfer_widgets and self.empty_label.winfo_exists():
            self.empty_label.pack(pady=30)

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