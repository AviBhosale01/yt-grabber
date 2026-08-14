# ⚡ Avii's YT Grabber

> **A sleek, arrow-key-navigable terminal YouTube downloader crafted with Python, yt-dlp, and Rich.**
> Made with ❤️ by **Avii**.

---

## ✨ Features

- 🎯 **Interactive TUI Menus**: Navigate quality options and browse directory trees natively using **Up/Down arrow keys + Enter** (no numeric typing).
- 🎬 **Smart Stream Detection & Remuxing**: Automatic grouping of video resolutions (4K, 2K, 1080p, 720p, 480p, 360p) merged with optimal audio streams into clean MP4 files.
- 🎵 **Audio Extraction**: Dedicated MP3 audio conversion using FFmpeg post-processing.
- 📁 **Interactive Folder Browser**: Arrow-key directory navigator starting at your OS Downloads folder, with manual path entry fallback and last-used folder persistence.
- 📊 **Rich Live Progress Bar**: Real-time download percentage, transfer speed (MB/s), ETA countdown, and status spinners during FFmpeg stream merging.
- 🛡️ **Graceful Error Handling & Cleanup**: Safe traps for invalid URLs, private/deleted videos, age restrictions, and clean Ctrl+C cancellation without partial artifacts or tracebacks.

---

## 🛠️ Prerequisites & Setup

### 1. Install FFmpeg (Required for remuxing high-res streams and MP3 extraction)

Make sure FFmpeg is installed and accessible on your system `PATH` (`ffmpeg -version` should succeed).

#### Windows
- **Using Winget**:
  ```powershell
  winget install Gyan.FFmpeg
  ```
- **Using Chocolatey**:
  ```powershell
  choco install ffmpeg
  ```
- **Using Scoop**:
  ```powershell
  scoop install ffmpeg
  ```
- **Manual**: Download the build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/), extract, and add the `bin` folder to your Windows System `PATH`.

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Debian / Ubuntu / Arch)
```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

---

### 2. Install Python Dependencies

Make sure Python 3.9+ is installed:

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

Launch the application:

```bash
python main.py
```

---

## 🕹️ User Flow

```
┌─────────────────────────────────────────────────────────────┐
│    __  _______   __________  ___ _____  ___  __________   │
│    \ \/ /_  __/  / ____/ __ \/   |  __ )/ __ )/ ____/ __ \  │
│     \  / / /    / / __/ /_/ / /| | __  / __  / __/ / /_/ /  │
│     / / / /    / /_/ / _, _/ ___ |/ /_/ / /_/ / /___/ _, _/   │
│    /_/ /_/     \____/_/ |_/_/  |_/_____/_____/_____/_/ |_|   │
│                                                             │
│                ⚡ Terminal YouTube Downloader ⚡             │
│                       made with ❤️  by Avii                  │
└─────────────────────────────────────────────────────────────┘

Paste YouTube link: https://www.youtube.com/watch?v=...

⠋ Fetching video info...

Choose a format (↑↓ to navigate, Enter to select):
  ▶ 🎬 1080p HD   MP4  (Video + Audio)   ~145.2 MB
    🎬 720p HD    MP4  (Video + Audio)   ~78.4 MB
    🎬 480p       MP4  (Video + Audio)   ~42.1 MB
    ──────────────────────────────────────────
    🎵 MP3        Audio only (Best Quality)  ~6.4 MB

Choose download folder:
  ▶ ✅ Save here [C:\Users\...\Downloads]
    ✏️ Type path manually...
    📁 .. (Go up)
    📁 Music
    📁 Videos

Downloading "Sample_Video.mp4"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  75%  •  4.2 MB/s  •  ETA 00:08

✔ Download Completed Successfully!
📁 Saved Path: C:\Users\...\Downloads\Sample_Video.mp4
📦 File Size: 145.2 MB in 12.4s

Download another video? (Y/n):
```

---

## ⚖️ Legal & Scope Disclaimer

This tool is intended for personal and educational use on content that you own, have explicit rights to download, or which is published under Creative Commons licenses. Downloading copyrighted media without authorization may violate YouTube's Terms of Service and applicable copyright laws. Please use responsibly.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the [LICENSE](LICENSE) file for details.

