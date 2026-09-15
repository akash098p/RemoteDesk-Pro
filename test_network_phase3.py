"""
RemoteDesk Pro - Phase 3+ Networking End-to-End Test

Runs a real host/client session over localhost and validates:
  1. TCP connect + hello handshake (peer tracking)
  2. Chat message delivery in both directions
  3. Screen frame delivery with base64 payload
  4. Single file transfer (chunked, checksummed, received intact)
  5. Folder transfer (relative paths rebuilt on the receiving side)

Run:  python test_network_phase3.py
"""

import os
import shutil
import sys
import tempfile
import time
import uuid

from network.connection_manager import ConnectionManager
from gui.pages.files import FileTransferManager

HOST_PORT = 15876
results = []


def check(name, condition):
    results.append((name, bool(condition)))
    print(f"{'PASS' if condition else 'FAIL'}: {name}")


def wait_until(predicate, timeout=8.0, interval=0.05):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


workspace = tempfile.mkdtemp(prefix="rdp_net_test_")
host_downloads = os.path.join(workspace, "host_downloads")
os.makedirs(host_downloads, exist_ok=True)

# ---------------------------------------------------------------- hosts/clients
host_cm = ConnectionManager(HOST_PORT)
client_cm = ConnectionManager()

host_chat = []
client_chat = []
host_frames = []

host_cm.register_callback("chat_message", lambda payload, peer_id=None: host_chat.append(payload))
client_cm.register_callback("chat_message", lambda payload, peer_id=None: client_chat.append(payload))
host_cm.register_callback("screen_frame", lambda payload: host_frames.append(payload))

host_transfer = FileTransferManager(host_cm, download_dir=host_downloads)
client_transfer = FileTransferManager(client_cm)
host_cm.register_callback("file_meta", lambda payload, peer_id=None: host_transfer.handle_file_meta(payload))
host_cm.register_callback("file_chunk", lambda payload, peer_id=None: host_transfer.handle_file_chunk(payload))

try:
    # 1. Host + connect -------------------------------------------------------
    check("host server started", host_cm.start_server(port=HOST_PORT))
    check("client connected", client_cm.connect_to_host("127.0.0.1", HOST_PORT))
    check("host sees peer", wait_until(host_cm.has_active_session))
    check("client sees peer", client_cm.has_active_session())

    # 2. Chat both directions --------------------------------------------------
    check("host -> client chat", host_cm.send_chat_message("hello from host", "Host"))
    check("client -> host chat", client_cm.send_chat_message("hello from client", "Client"))
    check("client received host chat", wait_until(lambda: any(m.get("content") == "hello from host" for m in client_chat)))
    check("host received client chat", wait_until(lambda: any(m.get("content") == "hello from client" for m in host_chat)))

    # 3. Screen frame -----------------------------------------------------------
    frame_payload = os.urandom(2048)
    check("screen frame sent", client_cm.send_screen_frame(frame_payload))
    check("host received screen frame", wait_until(lambda: bool(host_frames)))
    if host_frames:
        import base64
        decoded = base64.b64decode(host_frames[0].get("frame_data", ""))
        check("screen frame bytes intact", decoded == frame_payload)
    else:
        check("screen frame bytes intact", False)

    # 4. Single file transfer ----------------------------------------------------
    src = os.path.join(workspace, "payload.bin")
    content = os.urandom(300 * 1024)
    with open(src, "wb") as fh:
        fh.write(content)

    task = client_transfer.start_transfer(src)
    check("file transfer queued", bool(task.get("id")))
    received_ok = wait_until(
        lambda: host_transfer.get_transfer_status(task["id"]).get("status") == "completed",
        timeout=20,
    )
    check("file transfer completed on host", received_ok)
    received_file = os.path.join(host_downloads, "payload.bin")
    check("received file exists", os.path.exists(received_file))
    if os.path.exists(received_file):
        with open(received_file, "rb") as fh:
            check("received file content intact", fh.read() == content)
    else:
        check("received file content intact", False)
    sent_status = client_transfer.get_transfer_status(task["id"]).get("status")
    check(f"sender reports completed (got {sent_status})", sent_status == "completed")

    # 5. Folder transfer ----------------------------------------------------------
    folder = os.path.join(workspace, "my_folder")
    nested = os.path.join(folder, "nested")
    os.makedirs(nested, exist_ok=True)
    with open(os.path.join(folder, "a.txt"), "wb") as fh:
        fh.write(b"alpha")
    with open(os.path.join(nested, "b.txt"), "wb") as fh:
        fh.write(b"beta")

    queued = client_transfer.start_folder_transfer(folder)
    check("folder transfer queued 2 files", len(queued) == 2)
    folder_done = wait_until(
        lambda: all(
            host_transfer.get_transfer_status(t["id"]).get("status") == "completed"
            for t in queued
        ),
        timeout=20,
    )
    check("all folder transfers completed on host", folder_done)
    a_ok = os.path.exists(os.path.join(host_downloads, "my_folder", "a.txt"))
    b_ok = os.path.exists(os.path.join(host_downloads, "my_folder", "nested", "b.txt"))
    check("folder structure rebuilt (a.txt)", a_ok)
    check("folder structure rebuilt (nested/b.txt)", b_ok)
finally:
    client_cm.disconnect_all()
    host_cm.disconnect_all()
    shutil.rmtree(workspace, ignore_errors=True)
    shutil.rmtree(os.path.join(tempfile.gettempdir(), "__placeholder__"), ignore_errors=True)

print()
failed = [n for n, ok in results if not ok]
if failed:
    print(f"NETWORK TEST: {len(failed)} FAILURE(S): {failed}")
    sys.exit(1)
print("NETWORK TEST: ALL CHECKS PASSED")