# 🖥️ RemoteDesk Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1F6FEB?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Under%20Development-orange?style=for-the-badge)

### 🚀 A Modern Cross-Platform Remote Collaboration Platform Built with Python

**Screen Sharing • Remote Control • Chat • File Transfer • Clipboard Sync • Audio Streaming**

</div>

---

# 📖 Overview

RemoteDesk Pro is an open-source desktop application inspired by AnyDesk, TeamViewer, and Telegram Desktop.

The goal is to create a lightweight, modern, and secure remote collaboration platform that allows users to connect across different networks without using WebRTC or any cloud database.

Everything is built in Python using a modular architecture for easy maintenance and future expansion.

---
# 📹 Live Demo

<p align="center">
  <img src="media/RemoteDesk Pro.gif" width="100%">
</p>

---

# 📸 Screenshots

Coming Soon

---

# ✨ Features

## 🖥️ Screen Sharing

- Live desktop streaming (verified end-to-end over real TCP sessions)
- High-quality image compression
- Adjustable FPS
- Cross-network support (LAN + Tailscale Tailnet IP detection)
- Full-screen mode (planned)
- Multi-monitor support (planned)

---

## 🎮 Remote Control

- Mouse control
- Keyboard control
- Permission request dialog
- Remote shortcuts
- Safe control mode

---

## 💬 Chat

- Two-way messaging
- Emoji support 😀
- Image/file attachments
- Timestamp
- Read-receipt ticks (local display only)
- Typing indicator (planned)

---

## 📂 File Transfer

- Send files
- Send folders (structure-preserving, content-verified end-to-end)
- Native drag & drop via tkinterdnd2 (graceful fallback to dialogs)
- Progress bar
- Pause / Resume
- Cancel + abort notification
- Image preview
- Download history
- Save location selection

---

## 📋 Clipboard Synchronization

- Local clipboard manager page (view / copy / clear)
- Text, URLs and code snippets
- Network clipboard-sync protocol + background watcher (ready)
- Automatic UI sync wiring (pending — page currently shows "Remote sync is not configured yet")

---

## 🎤 Audio Streaming *(in progress — Screen-page toggle, no dedicated page yet)*

- Microphone streaming
- Speaker streaming
- Volume control
- Mute

---

## 🎨 User Interface

- Modern CustomTkinter interface
- Dark Mode
- Light Mode
- JSON themes (add more `gui/themes/*.json` to extend)
- Responsive layout
- Keyboard-first navigation (Ctrl+, Settings · Ctrl+Home Dashboard · Ctrl+L Logs · Ctrl+T theme · Ctrl+M minimize · Ctrl+Q quit)

---

## ⚙️ Settings

- Theme selection
- FPS selection
- Quality selection
- Font size
- Download folder
- Notification preferences
- Language
- Window settings
- Auto-connect (planned)
- Hotkeys (page shortcuts; global shortcuts fixed in code — full remapping UI planned)

---

## 📊 Dashboard

- System information
- CPU usage
- RAM usage
- Connection status
- Network information
- Logs

---

# 🛠️ Tech Stack

| Category | Technology |
|------------|----------------|
| Language | Python 3.14+ |
| GUI | CustomTkinter |
| Screen Capture | MSS |
| Networking | Python Socket |
| Cross-Network Access | Pyngrok / Tailscale-friendly manual endpoints |
| Images | Pillow |
| System Monitoring | Psutil |
| Clipboard | Pyperclip |
| Remote Control | Pynput + PyAutoGUI |
| Drag & Drop | tkinterdnd2 |
| Input / Emoji / UX Helpers | Emoji, ScreenInfo, Requests |
| Audio | SoundDevice / PyAudio *(optional)* |
| Logging | Python Logging |
| Config | JSON |
| Packaging | PyInstaller |

---

# 📁 Project Structure

```text
RemoteDesk-Pro/
│
├── app.py
├── assets/
├── config/
├── core/
├── gui/
├── network/
├── streaming/
├── chat/
├── files/
├── clipboard/
├── remote_control/
├── audio/
├── storage/
├── docs/
└── tests/
```

---

# 🚀 Development Roadmap

## ✅ Phase 1 — Foundation

- Project Structure
- Virtual Environment
- Git Repository
- Configuration System
- Theme Files
- Logging
- Foundation

---

## ✅ Phase 2 — UI & Navigation

- Main Window
- Sidebar
- Dashboard
- Navigation
- Settings
- Theme Manager
- Logger
- Status Bar

---

## ✅ Phase 3 — Networking Core

- Socket Server
- Socket Client
- Connection Manager
- Heartbeat
- Packet System

---

## ✅ Phase 4 — Screen Sharing

- Screen Sharing
- Video Compression
- FPS Controller
- Screen Receiver

---

## ✅ Phase 5 — Chat & Clipboard

- Chat
- Emoji
- Attachments
- Clipboard Sync
- Chat page UI
- Clipboard page UI
- Icon loading and theme compatibility

---

## ✅ Phase 6 — File Transfer

- File Transfer
- Folder Transfer (structure-preserving, resume-aware)
- Native drag & drop via tkinterdnd2
- Cancel / abort flow
- Image Preview
- Download Manager
- Transfer progress and reliability
- Incoming-transfers UI wiring

---

## ✅ Phase 7 — Remote Control & Session Reliability

- Remote Mouse (permission-gated, pyautogui)
- Remote Keyboard (permission-gated, pyautogui/pynput)
- Permission request/grant/deny dialog flow
- Control-request deep link from Screen page
- Session cleanup and disconnect handling
- Connect → Screen auto-navigation
- Cross-page stability improvements

---

## ✅ Phase 8 — Cross-Network Access & Audio Foundation

- LAN hosting + connect flow with auto-navigation to Screen
- Tailscale Tailnet IP auto-detection + in-app guidance (free cross-network path)
- Saved ngrok token field in Connection page (manual public-tunnel option)
- Live audio pipeline: sounddevice capture + sender wired to Screen-page toggle
- Internet-session reliability improvements

---

## 🚧 Phase 9 — In Progress

- Dedicated Audio settings page (`gui/pages/audio.py` is an empty stub)
- Clipboard page ↔ network sync wiring (protocol + watcher ready, page still local-only)
- Chat typing indicator + true delivery/read receipts over the wire
- Screen full-screen mode + multi-monitor selection
- Settings: auto-connect, full hotkey remapping UI
- Notifications refinement
- Multi-device validation on different networks

---

## ⏳ Phase 10 — Polishing & Release

- Performance optimization
- Packaging and distribution testing
- Release hardening

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/akash098p/RemoteDesk-Pro.git
```

Open the project

```bash
cd RemoteDesk-Pro
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Developer

**Akash Pramanik**

<p>
  <strong>For questions or support: </strong>
<a href="https://instagram.com/akash.098p" target="_blank">
  <img src="https://img.shields.io/badge/akash.098p-E4405F?style=flat&logo=instagram&logoColor=white"/>
</a> 

<a href="mailto:akashpramanik098@gmail.com">
  <img src="https://img.shields.io/badge/akashpramanik422%40gmail.com-D14836?style=flat&logo=gmail&logoColor=white"/>
</a>
</p>

---

# 📅 Current Progress

*Verified against the codebase — see "How to verify" below.*

| Module | Status | Notes |
|---------|--------|-------|
| Project Structure | ✅ | Modular layout stable |
| GUI Foundation | ✅ | CustomTkinter shell, navigation manager, status bar |
| Theme Engine | ✅ | JSON themes (dark + light shipped, extensible) |
| Logger | ✅ | File + console + in-memory buffer for Logs page |
| Dashboard | ✅ | CPU/RAM, session summary, quick actions |
| Navigation / Sidebar UX | ✅ | All pages registered; keyboard shortcuts wired |
| About Page | ✅ | App info |
| Networking Core | ✅ | Real TCP host/client verified 20/20 in `test_network_phase3.py` |
| Screen Sharing | ✅ | Live streaming verified end-to-end (FPS/quality controls) |
| Remote Control | ✅ | Permission-gated mouse/keyboard over active session |
| Chat | ✅ | Two-way messaging + attachments (typing indicator & true receipts pending) |
| File Transfer | ✅ | Files + folders with resume/cancel/history, verified end-to-end |
| Clipboard | 🚧 | Local manager works; network sync protocol ready but page not yet wired |
| Cross-Network Access | ✅ | LAN + Tailscale guidance; saved tunnel-token field |
| Audio | 🚧 | Capture + sender pipeline works from Screen-page toggle; no dedicated page yet |

---

## ✅ How to verify

```bash
venv\Scripts\python.exe test_network_phase3.py   # 20/20 end-to-end network checks
venv\Scripts\python.exe app.py                   # run the app
```

Status legend: ✅ working · 🚧 partially working / in progress · ⏳ not started

---

# 🤝 Contributing

Contributions are welcome.

If you'd like to improve RemoteDesk Pro, feel free to fork the repository and submit a Pull Request.

---

## ⭐ Support

If you like this project,

⭐ Star the repository

🐛 Report issues

💡 Suggest features


---
