"""
===============================================================================
RemoteDesk Pro
File: network/connection_manager.py
Session transport for screen, chat, audio, and remote input.
===============================================================================
"""

from __future__ import annotations

import base64
import platform
import socket
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse

from core.constants import DEFAULT_PORT
from core.logger import get_logger
from core.utils import get_tailscale_ip
from network.ngrok_integration import NgrokIntegration
from network.packet_system import PacketSystem
from network.protocol import MessageType, RemoteDeskMessage

logger = get_logger()


@dataclass
class PeerSession:
    """Connected peer metadata tracked by the session manager."""

    peer_id: str
    socket: socket.socket
    address: tuple[str, int]
    device_name: str = "Remote Device"
    remote_client_id: Optional[str] = None
    last_seen: float = field(default_factory=time.time)
    connected_at: float = field(default_factory=time.time)


class ConnectionManager:
    """
    Real-time session manager for RemoteDesk Pro.

    Features:
    - LAN host/client TCP transport
    - Optional public tunnel bootstrap through ngrok
    - Screen/audio/chat message routing
    - Incoming mouse/keyboard application on the host
    """

    def __init__(self, server_port: int = DEFAULT_PORT) -> None:
        self.server_port = server_port
        self.device_name = socket.gethostname()
        self.client_id = str(uuid.uuid4())

        self._server_socket: Optional[socket.socket] = None
        self._client_socket: Optional[socket.socket] = None
        self._client_peer: Optional[PeerSession] = None
        self._peers: Dict[str, PeerSession] = {}
        self._receive_threads: Dict[str, threading.Thread] = {}
        self._running = False
        self._is_server = False
        self._is_client = False
        self._remote_control_enabled = False
        self._lock = threading.RLock()
        self._send_lock = threading.RLock()

        self._callbacks: Dict[str, Optional[Callable[..., None]]] = {
            "status": None,
            "screen_frame": None,
            "chat_message": None,
            "audio_frame": None,
            "peer_connected": None,
            "peer_disconnected": None,
            "control_request": None,
        }

        self._mouse_controller = None
        self._keyboard_controller = None
        self._ngrok: Optional[NgrokIntegration] = None
        self._last_public_tunnel_error: Optional[str] = None
        logger.info(f"ConnectionManager initialized on port {server_port}")

    def parse_connection_target(self, host: str, port: Optional[int] = None) -> tuple[str, int]:
        """Accept raw hosts, host:port values, or ngrok-style tcp URLs."""
        raw_host = host.strip()
        raw_port = port

        if "://" in raw_host:
            parsed = urlparse(raw_host)
            if parsed.hostname:
                raw_host = parsed.hostname
            if parsed.port:
                raw_port = parsed.port
        elif raw_host.count(":") == 1 and raw_host.rsplit(":", 1)[1].isdigit():
            host_part, port_part = raw_host.rsplit(":", 1)
            raw_host = host_part
            raw_port = int(port_part)

        return raw_host, int(raw_port or DEFAULT_PORT)

    def register_callback(self, event: str, callback: Callable[..., None]) -> None:
        """Register a callback for connection/session events."""
        if event in self._callbacks:
            self._callbacks[event] = callback

    def _emit(self, event: str, *args: Any) -> None:
        callback = self._callbacks.get(event)
        if callback is None:
            return
        try:
            callback(*args)
        except Exception as exc:
            logger.error(f"Callback '{event}' failed: {exc}")

    def get_connection_status(self) -> str:
        """Return a UI-friendly session state."""
        if self._is_client and self._client_socket:
            return "connected"
        if self._peers:
            return "connected"
        if self._server_socket:
            return "hosting"
        return "idle"

    def get_local_ip(self) -> str:
        """Best-effort local IPv4 address for LAN sessions."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"
        finally:
            sock.close()

    def get_tailscale_ip(self) -> Optional[str]:
        """Return the local Tailscale/mesh VPN address when available."""
        return get_tailscale_ip()

    def start_server(self, host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> bool:
        """Start accepting inbound LAN connections."""
        with self._lock:
            if self._server_socket is not None:
                return True

            try:
                self.server_port = port
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((host, port))
                server_socket.listen(10)
                server_socket.settimeout(1.0)
                self._server_socket = server_socket
                self._running = True
                self._is_server = True
                threading.Thread(
                    target=self._accept_loop,
                    name="RemoteDeskAcceptLoop",
                    daemon=True,
                ).start()
                self._emit("status", f"Hosting on {self.get_local_ip()}:{port}", True)
                logger.info(f"Server started on {host}:{port}")
                return True
            except Exception as exc:
                logger.error(f"Failed to start server: {exc}")
                self._emit("status", f"Host failed: {exc}", False)
                return False

    def connect_to_host(self, host: str, port: int = DEFAULT_PORT) -> bool:
        """Connect to a remote host over TCP."""
        try:
            host, port = self.parse_connection_target(host, port)
            if self._client_socket is not None:
                self.disconnect_active_session()

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            client_socket.connect((host, port))
            client_socket.settimeout(1.0)

            peer = PeerSession(
                peer_id=str(uuid.uuid4()),
                socket=client_socket,
                address=(host, port),
                device_name=f"{host}:{port}",
            )

            with self._lock:
                self._client_socket = client_socket
                self._client_peer = peer
                self._running = True
                self._is_client = True

            thread = threading.Thread(
                target=self._receive_loop,
                args=(client_socket, peer.peer_id, False),
                name="RemoteDeskClientReceive",
                daemon=True,
            )
            self._receive_threads[peer.peer_id] = thread
            thread.start()

            self._send_hello(client_socket)
            self._emit("peer_connected", peer)
            self._emit("status", f"Connected to {host}:{port}", True)
            logger.info(f"Connected to host {host}:{port}")
            return True
        except Exception as exc:
            logger.error(f"Connection to host failed: {exc}")
            self._emit("status", f"Connect failed: {exc}", False)
            return False

    def enable_public_tunnel(self, auth_token: Optional[str] = None, region: str = "us") -> Optional[str]:
        """Expose the host port publicly when pyngrok is available."""
        if self._server_socket is None:
            self._last_public_tunnel_error = "Host server is not running."
            return None

        if self._ngrok is None:
            self._ngrok = NgrokIntegration(auth_token=auth_token, region=region)
        else:
            self._ngrok._auth_token = auth_token
            self._ngrok._region = region

        self._last_public_tunnel_error = None

        if self._ngrok.start_tunnel(port=self.server_port):
            public_url = self._ngrok.get_public_url()
            self._last_public_tunnel_error = None
            if public_url:
                self._emit("status", f"Public endpoint ready: {public_url}", True)
            return public_url
        self._last_public_tunnel_error = self._ngrok.get_last_error() if self._ngrok is not None else "Unknown ngrok error."
        return None

    def disable_public_tunnel(self) -> None:
        """Stop the active public endpoint if present."""
        if self._ngrok is not None:
            self._ngrok.stop_tunnel()

    def get_public_endpoint(self) -> Optional[str]:
        """Return current public endpoint if one exists."""
        if self._ngrok is None:
            return None
        return self._ngrok.get_public_url()

    def get_last_public_tunnel_error(self) -> Optional[str]:
        """Return the last ngrok/public-tunnel error, if any."""
        return self._last_public_tunnel_error

    def has_active_session(self) -> bool:
        """True when hosting with peers or connected to a host."""
        return bool(self._peers) or self._client_socket is not None

    def connected_peer_count(self) -> int:
        """Number of currently connected remote peers."""
        return len(self._peers) + (1 if self._client_socket else 0)

    def send_screen_frame(self, frame_data: bytes, metadata: Optional[dict] = None) -> bool:
        """Transmit a compressed screen frame."""
        payload = {
            "frame_data": base64.b64encode(frame_data).decode("ascii"),
            "metadata": metadata or {},
            "sender": self.device_name,
            "timestamp": time.time(),
        }
        return self._broadcast(RemoteDeskMessage(MessageType.SCREEN_FRAME, payload))

    def send_audio_frame(self, audio_data: bytes, metadata: Optional[dict] = None) -> bool:
        """Transmit raw PCM audio chunks."""
        payload = {
            "audio_data": base64.b64encode(audio_data).decode("ascii"),
            "metadata": metadata or {},
            "sender": self.device_name,
            "timestamp": time.time(),
        }
        return self._broadcast(RemoteDeskMessage(MessageType.AUDIO_FRAME, payload))

    def send_chat_message(
        self,
        content: str,
        sender: str,
        sender_id: Optional[str] = None,
        message_type: str = "text",
        metadata: Optional[dict] = None,
    ) -> bool:
        """Send a chat message through the active session."""
        payload = {
            "sender": sender,
            "sender_id": sender_id or self.client_id,
            "content": content,
            "message_type": message_type,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        return self._broadcast(RemoteDeskMessage(MessageType.CHAT_MESSAGE, payload))

    def send_mouse_event(self, payload: Any = None, **kwargs: Any) -> bool:
        """Send mouse input to the host or connected peers."""
        data = self._normalize_mouse_payload(payload, **kwargs)
        return self._broadcast(RemoteDeskMessage(MessageType.MOUSE_EVENT, data), client_only=True)

    def send_keyboard_event(self, payload: Any = None, **kwargs: Any) -> bool:
        """Send keyboard input to the host or connected peers."""
        data = self._normalize_keyboard_payload(payload, **kwargs)
        return self._broadcast(RemoteDeskMessage(MessageType.KEYBOARD_EVENT, data), client_only=True)

    def request_remote_control(self, requested_by: str) -> bool:
        """Ask the host to allow remote input control."""
        message = RemoteDeskMessage(
            MessageType.CONTROL_REQUEST,
            {"action": "request", "requested_by": requested_by, "timestamp": time.time()},
        )
        return self._broadcast(message, client_only=True)

    def set_remote_control_enabled(self, enabled: bool) -> None:
        """Enable or disable applying inbound mouse/keyboard events locally."""
        self._remote_control_enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f"Remote control {status}")

    def disconnect_all(self) -> None:
        """Close all sockets and reset state."""
        with self._lock:
            self._running = False
            peers = list(self._peers.values())
            client_socket = self._client_socket
            server_socket = self._server_socket
            self._peers.clear()
            self._client_socket = None
            self._client_peer = None
            self._server_socket = None
            self._is_client = False
            self._is_server = False
            self._remote_control_enabled = False

        for peer in peers:
            self._close_socket(peer.socket)
        if client_socket is not None:
            self._close_socket(client_socket)
        if server_socket is not None:
            self._close_socket(server_socket)

        self.disable_public_tunnel()
        self._emit("status", "Idle", False)
        logger.info("All connections disconnected")

    def disconnect_active_session(self) -> None:
        """End the current connected session but keep hosting available."""
        if self._client_socket is not None:
            client_socket = self._client_socket
            peer = self._client_peer
            self._client_socket = None
            self._client_peer = None
            self._is_client = False
            self._remote_control_enabled = False
            if client_socket is not None:
                self._close_socket(client_socket)
            if peer is not None:
                self._emit("peer_disconnected", peer)
            self._emit("status", self.get_connection_status().title(), self.has_active_session())
            return

        with self._lock:
            peers = list(self._peers.values())
            self._peers.clear()
            self._remote_control_enabled = False

        for peer in peers:
            self._close_socket(peer.socket)
            self._emit("peer_disconnected", peer)

        self._emit("status", self.get_connection_status().title(), self.has_active_session())

    def get_session_summary(self) -> str:
        """Human-readable summary for the current session state."""
        if self._client_peer is not None:
            return f"Connected to {self._client_peer.device_name}"
        if self._peers:
            return f"{len(self._peers)} device(s) connected to this host"
        if self._server_socket is not None:
            return f"Hosting on {self.get_local_ip()}:{self.server_port}"
        return "Idle"

    def _broadcast(self, message: RemoteDeskMessage, client_only: bool = False) -> bool:
        packet = PacketSystem.create_packet(message.to_dict())
        if not packet:
            return False

        sent = False
        if self._is_client and self._client_socket is not None:
            sent = self._send_packet(self._client_socket, packet)
        elif self._is_server:
            with self._lock:
                peers = list(self._peers.values())
            for peer in peers:
                sent = self._send_packet(peer.socket, packet) or sent
        return sent

    def respond_to_control_request(self, peer_id: str, granted: bool, requested_by: str = "remote") -> bool:
        """Reply to a pending remote-control request."""
        with self._lock:
            peer = self._peers.get(peer_id)
        if peer is None:
            return False

        action = "granted" if granted else "denied"
        response = RemoteDeskMessage(
            MessageType.CONTROL_REQUEST,
            {
                "action": action,
                "requested_by": requested_by,
                "timestamp": time.time(),
            },
        )
        if granted:
            self.set_remote_control_enabled(True)
        return self._send_packet(peer.socket, PacketSystem.create_packet(response.to_dict()))

    def _send_packet(self, sock: socket.socket, packet: bytes) -> bool:
        try:
            with self._send_lock:
                sock.sendall(packet)
            return True
        except Exception as exc:
            logger.error(f"Send failed: {exc}")
            self._drop_socket(sock)
            return False

    def _drop_socket(self, sock: socket.socket) -> None:
        """Remove a socket from active tracking after transport failure."""
        self._close_socket(sock)
        with self._lock:
            if self._client_socket is sock:
                self._client_socket = None
                self._client_peer = None
                self._is_client = False
                self._remote_control_enabled = False
                self._emit("status", self.get_connection_status().title(), self.has_active_session())
                return

            removed_peer_id = None
            removed_peer = None
            for peer_id, peer in self._peers.items():
                if peer.socket is sock:
                    removed_peer_id = peer_id
                    removed_peer = peer
                    break
            if removed_peer_id is not None:
                self._peers.pop(removed_peer_id, None)
                if removed_peer is not None:
                    self._emit("peer_disconnected", removed_peer)
                self._emit("status", self.get_connection_status().title(), self.has_active_session())

    def _accept_loop(self) -> None:
        while self._running and self._server_socket is not None:
            try:
                client_socket, address = self._server_socket.accept()
                client_socket.settimeout(1.0)
                peer = PeerSession(
                    peer_id=str(uuid.uuid4()),
                    socket=client_socket,
                    address=address,
                    device_name=f"{address[0]}:{address[1]}",
                )
                with self._lock:
                    self._peers[peer.peer_id] = peer
                thread = threading.Thread(
                    target=self._receive_loop,
                    args=(client_socket, peer.peer_id, True),
                    name=f"RemoteDeskPeer-{peer.peer_id}",
                    daemon=True,
                )
                self._receive_threads[peer.peer_id] = thread
                thread.start()
                self._emit("peer_connected", peer)
                self._emit("status", f"{len(self._peers)} device(s) connected", True)
                logger.info(f"Peer connected from {address}")
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as exc:
                logger.error(f"Accept loop error: {exc}")
                break

    def _receive_loop(self, sock: socket.socket, peer_id: str, is_server_side: bool) -> None:
        buffer = b""
        while self._running:
            try:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buffer += chunk
                buffer = self._consume_buffer(buffer, peer_id, is_server_side)
            except socket.timeout:
                continue
            except OSError:
                break
            except Exception as exc:
                logger.error(f"Receive loop error for {peer_id}: {exc}")
                break

        self._handle_disconnect(peer_id, sock, is_server_side)

    def _consume_buffer(self, buffer: bytes, peer_id: str, is_server_side: bool) -> bytes:
        while len(buffer) >= 4:
            packet_length = int.from_bytes(buffer[:4], "big")
            if len(buffer) < 4 + packet_length:
                return buffer
            packet = buffer[: 4 + packet_length]
            buffer = buffer[4 + packet_length :]
            message_dict = PacketSystem.parse_packet(packet)
            if not message_dict:
                continue
            self._process_message(RemoteDeskMessage.from_dict(message_dict), peer_id, is_server_side)
        return buffer

    def _process_message(self, message: RemoteDeskMessage, peer_id: str, is_server_side: bool) -> None:
        if message.type == MessageType.HEARTBEAT:
            self._handle_heartbeat(message.payload, peer_id, is_server_side)
            return
        if message.type == MessageType.SCREEN_FRAME:
            self._emit("screen_frame", message.payload)
            if is_server_side:
                self._relay_to_other_clients(message, peer_id)
            return
        if message.type == MessageType.AUDIO_FRAME:
            self._emit("audio_frame", message.payload)
            if is_server_side:
                self._relay_to_other_clients(message, peer_id)
            return
        if message.type == MessageType.CHAT_MESSAGE:
            self._emit("chat_message", message.payload, peer_id)
            if is_server_side:
                self._relay_to_other_clients(message, peer_id)
            return
        if message.type == MessageType.MOUSE_EVENT:
            self._handle_mouse_event(message.payload)
            return
        if message.type == MessageType.KEYBOARD_EVENT:
            self._handle_keyboard_event(message.payload)
            return
        if message.type == MessageType.CONTROL_REQUEST:
            self._handle_control_request(message.payload, peer_id, is_server_side)

    def _relay_to_other_clients(self, message: RemoteDeskMessage, exclude_peer_id: str) -> None:
        packet = PacketSystem.create_packet(message.to_dict())
        with self._lock:
            peers = [peer for peer_id, peer in self._peers.items() if peer_id != exclude_peer_id]
        for peer in peers:
            self._send_packet(peer.socket, packet)

    def _handle_mouse_event(self, payload: dict) -> None:
        if not self._remote_control_enabled:
            return
        controller = self._ensure_mouse_controller()
        if controller is None:
            return

        action = payload.get("action", payload.get("event_type", "move"))
        x = int(payload.get("x", 0))
        y = int(payload.get("y", 0))
        button = str(payload.get("button", "left")).lower()

        try:
            if action == "move":
                controller.moveTo(x, y)
            elif action == "click":
                controller.click(x=x, y=y, button=button)
            elif action == "down":
                controller.mouseDown(x=x, y=y, button=button)
            elif action == "up":
                controller.mouseUp(x=x, y=y, button=button)
            elif action == "scroll":
                controller.scroll(int(payload.get("delta", payload.get("dy", 0))))
        except Exception as exc:
            logger.error(f"Failed to apply mouse event: {exc}")

    def _handle_keyboard_event(self, payload: dict) -> None:
        if not self._remote_control_enabled:
            return
        action = str(payload.get("action", "press")).lower()
        key = str(payload.get("key", ""))

        try:
            if platform.system() == "Windows":
                import pyautogui

                if action == "press":
                    pyautogui.keyDown(key)
                elif action == "release":
                    pyautogui.keyUp(key)
                elif action == "tap":
                    pyautogui.press(key)
                elif action == "type":
                    pyautogui.write(key)
            else:
                from pynput.keyboard import Controller

                keyboard = Controller()
                if action == "press":
                    keyboard.press(key)
                elif action == "release":
                    keyboard.release(key)
                elif action == "tap":
                    keyboard.press(key)
                    keyboard.release(key)
                elif action == "type":
                    keyboard.type(key)
        except Exception as exc:
            logger.error(f"Failed to apply keyboard event: {exc}")

    def _handle_control_request(self, payload: dict, peer_id: str, is_server_side: bool) -> None:
        if payload.get("action") == "request":
            self._emit("control_request", payload, peer_id)
            if not is_server_side:
                self.set_remote_control_enabled(True)
        elif payload.get("action") == "granted":
            self.set_remote_control_enabled(True)
            self._emit("status", "Remote control granted", True)
        elif payload.get("action") == "denied":
            self.set_remote_control_enabled(False)
            self._emit("status", "Remote control denied", False)

    def _handle_heartbeat(self, payload: dict, peer_id: str, is_server_side: bool) -> None:
        """Update peer metadata from hello/heartbeat messages."""
        with self._lock:
            if is_server_side:
                peer = self._peers.get(peer_id)
            else:
                peer = self._client_peer

            if peer is None:
                return

            peer.last_seen = time.time()
            peer.device_name = payload.get("device_name", peer.device_name)
            peer.remote_client_id = payload.get("client_id", peer.remote_client_id)

        self._emit("status", self.get_session_summary(), True)

    def _ensure_mouse_controller(self):
        if self._mouse_controller is not None:
            return self._mouse_controller
        try:
            import pyautogui

            pyautogui.FAILSAFE = False
            self._mouse_controller = pyautogui
            return self._mouse_controller
        except Exception as exc:
            logger.error(f"Mouse controller unavailable: {exc}")
            return None

    def _send_hello(self, sock: socket.socket) -> None:
        hello = RemoteDeskMessage(
            MessageType.HEARTBEAT,
            {
                "device_name": self.device_name,
                "client_id": self.client_id,
                "timestamp": time.time(),
            },
        )
        self._send_packet(sock, PacketSystem.create_packet(hello.to_dict()))

    def _handle_disconnect(self, peer_id: str, sock: socket.socket, is_server_side: bool) -> None:
        self._close_socket(sock)
        with self._lock:
            if is_server_side:
                peer = self._peers.pop(peer_id, None)
            else:
                peer = self._client_peer
                self._client_peer = None
                self._client_socket = None
                self._is_client = False

        if peer is not None:
            self._emit("peer_disconnected", peer)
        self._emit("status", self.get_connection_status().title(), self.has_active_session())

    def _close_socket(self, sock: socket.socket) -> None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass

    def _normalize_mouse_payload(self, payload: Any = None, **kwargs: Any) -> dict:
        if isinstance(payload, dict):
            data = dict(payload)
        elif payload is not None and hasattr(payload, "__dict__"):
            data = dict(payload.__dict__)
        else:
            data = {}
        data.update(kwargs)
        if "event_type" in data and "action" not in data:
            data["action"] = data["event_type"]
        return {
            "action": data.get("action", "move"),
            "x": int(data.get("x", 0)),
            "y": int(data.get("y", 0)),
            "button": str(data.get("button", "left")),
            "delta": int(data.get("delta", data.get("dy", 0))),
        }

    def _normalize_keyboard_payload(self, payload: Any = None, **kwargs: Any) -> dict:
        if isinstance(payload, dict):
            data = dict(payload)
        elif payload is not None and hasattr(payload, "__dict__"):
            data = dict(payload.__dict__)
        else:
            data = {}
        data.update(kwargs)
        action = str(data.get("action", data.get("type", "tap"))).lower()
        if action == "combo":
            action = "type"
        return {
            "action": action,
            "key": str(data.get("key", "")),
        }

    def __del__(self) -> None:
        self.disconnect_all()
