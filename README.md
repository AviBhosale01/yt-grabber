<div align="center">

# ⚡ Avii's YT Grabber

### *Ultra-Fast Next-Gen Terminal YouTube Video & Audio Downloader*

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-2026.8%2B-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![Rich](https://img.shields.io/badge/Rich-Terminal%20UI-00C7B7?style=for-the-badge&logo=gnometerminal&logoColor=white)](https://github.com/Textualize/rich)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Remuxing-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-blueviolet.svg?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=for-the-badge&logo=linux&logoColor=white)](#prerequisites--installation)

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-10-second-quick-start">10s Quick Start</a> •
  <a href="#-prerequisites--step-by-step-setup">Setup Guide</a> •
  <a href="#-user-flow">User Flow</a> •
  <a href="#-project-architecture">Architecture</a> •
  <a href="#-license">License</a>
</p>

```
  █████╗  ██╗   ██╗██╗██╗  ███████╗
 ██╔══██╗ ██║   ██║██║╚═╝  ██╔════╝
 ███████║ ██║   ██║██║     ███████╗
 ██╔══██║ ╚██╗ ██╔╝██║     ╚════██║
 ██║  ██║  ╚████╔╝ ██║     ███████║
 ╚═╝  ╚═╝   ╚═══╝  ╚═╝     ╚══════╝

    █▄ █▄ ▀█▀   █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀ █▀▀█
     ▀█▄▀  █    █ ▄▄ █▄▄▀ █▄▄█ █▀▀▄ █▀▀▄ █▀▀ █▄▄▀
      ▀█▀  █    █▄▄█ █  █ █  █ █▄▄█ █▄▄█ █▄▄ █  █

   👾 8-BIT ARCADE  •  ⚡ YOUTUBE GRABBER PRO EDITION ⚡
             🕹️ CREATED BY: Avii. [ARCADE ENGINE]
```

</div>

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🎮 **Arrow-Key Quality Picker** | Interactive TUI — navigate video resolutions & MP3 options with **Up / Down / Enter** (no numeric typing). |
| 📂 **Native OS Folder Picker Popup** | Hitting Enter immediately opens your operating system's native **File Explorer / Folder Dialog** window to select the destination visually. |
| 🎬 **Smart Stream Remuxing** | Automatically discovers genuine resolutions (4K 60fps, 2K, 1080p, 720p, 480p, 360p, 240p, 144p) and remuxes separate video + best audio streams into MP4 via FFmpeg. |
| 🎵 **Multi-Bitrate MP3 Extraction** | Direct audio downloads across multiple bitrates (320 kbps Ultra, 256 kbps High, 192 kbps Standard, 128 kbps Voice) or lossless .M4A streams. |
| 📁 **Interactive Terminal Fallback** | Fallback in-terminal directory navigator with subfolder traversing, parent navigation (`..`), and manual path input. |
| 📊 **Neon Live Progress Bar** | Rich animated progress display showing download percentage, transfer speed (MB/s), ETA countdown, and merging spinners. |
| 🛡️ **Anti-403 Challenge Engine** | Integrated Node.js challenge solving runtime and resilient client routing to eliminate HTTP 403 Forbidden errors on YouTube DASH streams. |
| 💾 **History & Config Persistence** | Remembers your last-used download folder and maintains a download history in `~/.yt_grabber_config.json`. |
| 🛑 **Graceful Signal Handling** | Non-destructive `Ctrl+C` cancellation that immediately removes temporary `.part` / `.ytdl` files without raw tracebacks. |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core application logic and runtime |
| **Media Engine** | ![yt-dlp](https://img.shields.io/badge/yt--dlp-FF0000?style=flat-square&logo=youtube&logoColor=white) | Metadata extraction & multi-stream download |
| **Media Processing** | ![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white) | Video/audio remuxing & MP3 encoding |
| **Terminal UI** | ![Rich](https://img.shields.io/badge/Rich-00C7B7?style=flat-square&logo=gnometerminal&logoColor=white) | Neon gradients, panels, tables, live progress bars |
| **Interactive Prompts** | ![Questionary](https://img.shields.io/badge/Questionary-FF6F00?style=flat-square&logo=inquirer&logoColor=white) | Arrow-key selection menus & folder browser |
| **ASCII Typography** | ![PyFiglet](https://img.shields.io/badge/PyFiglet-8A2BE2?style=flat-square) | Header ASCII art rendering |

</div>

---

## 📦 Prerequisites & Installation

### 1. Install FFmpeg *(Required for merging high-res streams & MP3 conversion)*

Verify FFmpeg is on your PATH by running `ffmpeg -version`. If not installed:

## ⚡ 10-Second Quick Start

Copy and paste the 1-liner for your operating system:

### 🪟 Windows (PowerShell)
```powershell
git clone https://github.com/AviBhosale01/yt-grabber.git; cd yt-grabber; python -m pip install -r requirements.txt; python main.py
```
> 💡 *Or simply double-click **`run.bat`** in the project folder!*

### 🍎 macOS / 🐧 Linux (Bash/Zsh)
```bash
git clone https://github.com/AviBhosale01/yt-grabber.git && cd yt-grabber && python3 -m pip install -r requirements.txt && python3 main.py
```
> 💡 *Or run `./run.sh`!*

---

## 📦 Prerequisites & Step-by-Step Setup

### Step 1: Install FFmpeg *(Required for 1080p+ stream merging & MP3 conversion)*

<table>
<tr>
<th>Platform</th>
<th>Fastest Install Command</th>
</tr>
<tr>
<td><b>🪟 Windows</b></td>
<td>

```powershell
# Run in PowerShell, then restart terminal:
winget install Gyan.FFmpeg
```
*(Alternatively: `choco install ffmpeg` or `scoop install ffmpeg`)*
</td>
</tr>
<tr>
<td><b>🍎 macOS</b></td>
<td>

```bash
brew install ffmpeg
```
</td>
</tr>
<tr>
<td><b>🐧 Linux</b></td>
<td>

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```
</td>
</tr>
</table>

---

### Step 2: Clone & Launch

```bash
# 1. Clone the repo
git clone https://github.com/AviBhosale01/yt-grabber.git
cd yt-grabber

# 2. Install requirements (use 'python -m pip' to avoid Windows PATH errors)
python -m pip install -r requirements.txt

# 3. Run
python main.py
```

---

## 🕹️ User Flow

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ Avii's YT Grabber                                      │
└─────────────────────────────────────────────────────────────┘

? Paste YouTube link (or 'q' to quit): https://youtu.be/...

⠋ Fetching video info...

╭─────────────────────────── ✓ Video Metadata Found ───────────────────────────╮
│  🎬 Title:     Sample YouTube Video                                          │
│  📺 Channel:   Creator Studio                                                │
│  ⏱️ Duration:  04:32                                                         │
│  👀 Views:     1,420,890                                                     │
│  📅 Uploaded:  2024-06-15                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

? Choose a format (↑↓ to navigate, Enter to select):
  ▶ 🎬 4K 2160p 60fps  MP4  (Ultra HD 4K)      ~520.4 MB
    🎬 1080p 60fps     MP4  (Full HD)          ~145.2 MB
    🎬 720p 60fps      MP4  (High Def)         ~78.4 MB
    🎬 480p            MP4  (Standard)         ~42.1 MB
    ──────────── 🎵 Audio Only Options ────────────
    🎵 MP3 — Ultra Quality (320 kbps)          ~10.5 MB
    🎵 MP3 — High Quality  (256 kbps)          ~8.4 MB
    🎵 Original Audio (.M4A / Best Bitrate)    ~5.8 MB

Opening folder selector window...
[🗂️ Native OS File Explorer / Folder Dialog window opens in foreground]
✓ Selected folder: C:\Users\Avii\Desktop

Starting download for: Sample YouTube Video
⠦ Downloading Sample Video.mp4 ━━━━━━━━━━━━━━━━━━━ 75% • 4.2 MB/s • ETA 00:08

╭─────────────────────── ✔ Download Completed Successfully! ────────────────────╮
│  📁 Saved Path: C:\Users\Avii\Downloads\Sample Video.mp4                     │
│  📦 File Size:  145.2 MB in 12.4s                                             │
│  🎯 File Name:  Sample Video.mp4                                             │
╰───────────────────────────────────────────────────────────────────────────────╯

? Download another video? (Y/n)
```

---

## 📂 Project Architecture

```
yt-grabber/
├── main.py                 # Application lifecycle, error traps, interactive loop
├── requirements.txt        # Python package dependencies
├── LICENSE                 # MIT License
├── README.md               # Visual documentation & setup guide
├── core/
│   ├── extractor.py        # Multi-client metadata extraction & format aggregation
│   └── downloader.py       # Download engine, progress hook wiring, FFmpeg merging
├── ui/
│   ├── banner.py           # pyfiglet ASCII art & Rich metadata panels
│   ├── format_menu.py      # Questionary arrow-key quality selection
│   ├── folder_picker.py    # Arrow-key directory tree browser
│   └── progress.py         # Real-time progress bar & post-processor state manager
├── utils/
│   ├── validators.py       # YouTube URL regex validator & Windows filename sanitizer
│   ├── config.py           # Persistent settings & download history (~/.yt_grabber_config.json)
│   └── helpers.py          # Human-readable byte formatting & system checks
└── tests/
    └── test_components.py  # Automated unit test suite (10 test cases)
```

---

## 🧪 Testing

Run the automated test suite:

```bash
python -m unittest discover tests
```

---

## ⚖️ Legal & Scope Disclaimer

This software is intended for personal and educational use on content that you own, have explicit rights to download, or which is published under Creative Commons licenses. Downloading copyrighted media without authorization may violate YouTube's Terms of Service and applicable copyright laws. Please use responsibly.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

Made with ❤️ by [**Avi Bhosale**](https://github.com/AviBhosale01)

⭐ **If you find this project useful, don't forget to give it a star on GitHub!** ⭐

</div>
