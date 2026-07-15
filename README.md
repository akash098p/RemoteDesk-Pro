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

# ✨ Features

## 🖥️ Screen Sharing

- Live desktop streaming
- High-quality image compression
- Adjustable FPS
- Full-screen mode
- Multi-monitor support (planned)
- Cross-network support

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
- Image sharing
- File sharing
- Drag & Drop
- Typing indicator
- Read status (planned)
- Timestamp

---

## 📂 File Transfer

- Send files
- Send folders
- Drag & Drop
- Progress bar
- Pause / Resume
- Image preview
- Download history
- Save location selection

---

## 📋 Clipboard Synchronization

- Automatic clipboard sync
- Text
- URLs
- Code snippets

---

## 🎤 Audio Streaming *(Planned)*

- Microphone streaming
- Speaker streaming
- Volume control
- Mute

---

## 🎨 User Interface

- Modern CustomTkinter interface
- Dark Mode
- Light Mode
- AMOLED Theme
- Dracula Theme
- Nord Theme
- Custom themes (planned)
- Responsive layout

---

## ⚙️ Settings

- Theme selection
- FPS selection
- Quality selection
- Download folder
- Notifications
- Hotkeys
- Language
- Auto-connect (planned)

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
- Folder Transfer
- Image Preview
- Download Manager
- Transfer progress and reliability

---

## 🚧 Phase 7 — Remote Control & Session Reliability

- Remote Mouse
- Remote Keyboard
- Permission System
- Secure session controls
- Session cleanup and disconnect handling
- Cross-page stability improvements

---

## 🚧 Phase 8 — Cross-Network Access & Audio

- Public endpoint guidance and tunnel UX
- Optional live audio dependencies
- Better host / peer connection flow
- Internet-session reliability improvements

---

## ⏳ Phase 9 — Polishing & Release

- Performance Optimization
- Notifications refinement
- Packaging and distribution testing
- Multi-device validation on different networks

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

# 📸 Screenshots

Coming Soon

---

# 📅 Current Progress

| Module | Status |
|---------|--------|
| Project Structure | ✅ |
| GUI Foundation | ✅ |
| Theme Engine | ✅ |
| Logger | ✅ |
| Dashboard | ✅ |
| Navigation / Sidebar UX | ✅ |
| About Page | ✅ |
| Networking | 🚧 |
| Screen Sharing | 🚧 |
| Remote Control | 🚧 |
| Chat | ✅ |
| File Transfer | 🚧 |
| Clipboard | ✅ |
| Public Tunnel / Internet Access | 🚧 |
| Audio | ⏳ |

---

# 🤝 Contributing

Contributions are welcome.

If you'd like to improve RemoteDesk Pro, feel free to fork the repository and submit a Pull Request.

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

## ⭐ Support

If you like this project,

⭐ Star the repository

🐛 Report issues

💡 Suggest features


---
