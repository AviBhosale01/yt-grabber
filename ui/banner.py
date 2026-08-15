import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from utils.helpers import check_ffmpeg_installed, format_duration, format_bytes

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(force_terminal=True, highlight=False)


def print_banner() -> None:
    """Render the 3D Pixel Arcade banner with AVI'S typography and custom retro palette."""
    # 3D Pixel Character segments for AVI'S (A, V, I, ', S)
    avis_segments = [
        (" █████╗ ", " ██╗   ██╗", "██╗", "██╗  ", "███████╗"),
        ("██╔══██╗", " ██║   ██║", "██║", "╚═╝  ", "██╔════╝"),
        ("███████║", " ██║   ██║", "██║", "     ", "███████╗"),
        ("██╔══██║", " ╚██╗ ██╔╝", "██║", "     ", "╚════██║"),
        ("██║  ██║", "  ╚████╔╝ ", "██║", "     ", "███████║"),
        ("╚═╝  ╚═╝", "   ╚═══╝  ", "╚═╝", "     ", "╚══════╝"),
    ]

    # Vibrant Terminal Color Palette (Red, Gold, Lime, White, Cyan)
    char_styles = [
        "bold #FF1E56",  # A - Crimson Neon
        "bold #FFE600",  # V - Cyber Gold
        "bold #00FF66",  # I - Electric Lime
        "bold #FFFFFF",  # ' - Pure Diamond White
        "bold #00F0FF",  # S - Electric Cyan
    ]

    banner_text = Text()

    # Render AVI'S in multi-color 3D blocks
    for row in avis_segments:
        for idx, segment in enumerate(row):
            banner_text.append(segment, style=char_styles[idx])
        banner_text.append("\n")

    banner_text.append("\n")

    # Isometric sub-banner for YT GRABBER (Violet -> Magenta -> Neon Pink)
    sub_pixel_lines = [
        " █▄ █▄ ▀█▀   █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀ █▀▀█ ",
        "  ▀█▄▀  █    █ ▄▄ █▄▄▀ █▄▄█ █▀▀▄ █▀▀▄ █▀▀ █▄▄▀ ",
        "   ▀█▀  █    █▄▄█ █  █ █  █ █▄▄█ █▄▄█ █▄▄ █  █ ",
    ]

    sub_styles = ["bold #BD00FF", "bold #D000FF", "bold #FF007F"]
    for i, line in enumerate(sub_pixel_lines):
        banner_text.append("    " + line + "\n", style=sub_styles[i % len(sub_styles)])

    banner_text.append("\n")

    # Retro Arcade Badges
    footer = Text()
    footer.append(" 👾 8-BIT ARCADE ", style="bold black on #00FF66")
    footer.append(" ⚡ YOUTUBE GRABBER ", style="bold black on #FFE600")
    footer.append(" 🚀 PRO EDITION ", style="bold white on #BD00FF")
    footer.append("\n")
    footer.append(" 🕹️  CREATED BY: ", style="bold #FF007F")
    footer.append("Avii", style="bold #00F0FF underline")
    footer.append("   ★   ", style="bold #FFE600")
    footer.append("ULTRA HIGH-SPEED DOWNLOAD ENGINE", style="bold #00FF66")

    banner_text.append_text(footer)

    ffmpeg_ready = check_ffmpeg_installed()
    status_style = "bold #00FF66" if ffmpeg_ready else "bold #FF1E56"
    status_text = "● FFmpeg Ready  [Arcade Mode Active]" if ffmpeg_ready else "▲ FFmpeg Missing [Remux Limited]"

    panel = Panel(
        banner_text,
        title="[bold #FFE600]══[ 🕹️   A V I I ' S   Y T   G R A B B E R   ]══[/bold #FFE600]",
        subtitle=f"[{status_style}]{status_text}[/{status_style}]",
        subtitle_align="right",
        border_style="#00F0FF",
        box=box.DOUBLE,
        padding=(1, 2),
    )
    console.print(panel)


def print_video_info(info: dict) -> None:
    """Print a retro pixel-styled metadata summary card for the fetched YouTube video.

    Args:
        info: Video metadata dictionary from yt-dlp.
    """
    title = info.get("title", "Unknown Title")
    channel = info.get("uploader") or info.get("channel", "Unknown Channel")
    duration = format_duration(info.get("duration"))
    views = info.get("view_count")
    views_str = f"{views:,}" if isinstance(views, int) else "N/A"
    upload_date = info.get("upload_date")
    if upload_date and len(upload_date) == 8:
        upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        upload_date = "N/A"

    table = Table(show_header=False, box=box.SIMPLE, expand=True)
    table.add_column("Key", style="bold #00F0FF", width=14)
    table.add_column("Value", style="white")

    table.add_row("🎬 Title:", f"[bold bright_white]{title}[/bold bright_white]")
    table.add_row("📺 Channel:", f"[bold #FFE600]{channel}[/bold #FFE600]")
    table.add_row("⏱️ Duration:", f"[bold #00FF66]{duration}[/bold #00FF66]")
    table.add_row("👀 Views:", f"[#FF9100]{views_str}[/#FF9100]")
    table.add_row("📅 Uploaded:", f"[dim #00F0FF]{upload_date}[/dim #00F0FF]")

    panel = Panel(
        table,
        title="[bold #00FF66]👾 ✓ Video Metadata Loaded[/bold #00FF66]",
        border_style="#00F0FF",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)
