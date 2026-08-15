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
    """Render the 3D Pixel Arcade banner with authentic 8-bit typography and retro palette."""
    # 3D Pixel Font for PIXELS (from the reference arcade title)
    pixel_art_lines = [
        "  ██████╗ ██╗██╗  ██╗███████╗██╗     ███████╗",
        "  ██╔══██╗██║╚██╗██╔╝██╔════╝██║     ██╔════╝",
        "  ██████╔╝██║ ╚███╔╝ █████╗  ██║     ███████╗",
        "  ██╔═══╝ ██║ ██╔██╗ ██╔══╝  ██║     ╚════██║",
        "  ██║     ██║██╔╝ ██╗███████╗███████╗███████║",
        "  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝",
    ]

    # Isometric block sub-banner for YT GRABBER
    sub_pixel_lines = [
        " █▄ █▄ ▀█▀   █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀█ █▀▀ █▀▀█ ",
        "  ▀█▄▀  █    █ ▄▄ █▄▄▀ █▄▄█ █▀▀▄ █▀▀▄ █▀▀ █▄▄▀ ",
        "   ▀█▀  █    █▄▄█ █  █ █  █ █▄▄█ █▄▄█ █▄▄ █  █ ",
    ]

    banner_text = Text()

    # Arcade Palette: Neon Yellow -> Bright Orange -> Hot Pink -> Cyber Violet -> Cyan
    p_colors = ["#FFE600", "#FF9100", "#FF007F", "#D000FF", "#7209B7", "#00F0FF"]
    for i, line in enumerate(pixel_art_lines):
        banner_text.append(line + "\n", style=f"bold {p_colors[i % len(p_colors)]}")

    banner_text.append("\n")

    # Sub-bar in Electric Cyan & Space Lime
    sub_colors = ["bold #00F0FF", "bold #00D8F6", "bold #39FF14"]
    for i, line in enumerate(sub_pixel_lines):
        banner_text.append("    " + line + "\n", style=sub_colors[i % len(sub_colors)])

    banner_text.append("\n")

    # Retro Arcade Player Badge & Subtitle
    footer = Text()
    footer.append(" 👾 8-BIT RETRO EDITION ", style="bold black on #00F0FF")
    footer.append(" ⚡ NEXT-GEN TERMINAL GRABBER ", style="bold black on #FFE600")
    footer.append("\n")
    footer.append(" 🕹️  PLAYER: ", style="bold #FF007F")
    footer.append("Avii", style="bold #00F0FF underline")
    footer.append("   ★   ", style="bold #FFE600")
    footer.append("HIGH-SCORE QUALITY ENGINE", style="bold #39FF14")

    banner_text.append_text(footer)

    ffmpeg_ready = check_ffmpeg_installed()
    status_style = "bold #39FF14" if ffmpeg_ready else "bold #FF3366"
    status_text = "● FFmpeg Ready  [100% 8-Bit Power]" if ffmpeg_ready else "▲ FFmpeg Missing [Remux Limited]"

    panel = Panel(
        banner_text,
        title="[bold #FFE600]══[ 🕹️  P I X E L   A R C A D E  ]══[/bold #FFE600]",
        subtitle=f"[{status_style}]{status_text}[/{status_style}]",
        subtitle_align="right",
        border_style="#FF007F",
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
    table.add_row("⏱️ Duration:", f"[bold #39FF14]{duration}[/bold #39FF14]")
    table.add_row("👀 Views:", f"[#FF9100]{views_str}[/#FF9100]")
    table.add_row("📅 Uploaded:", f"[dim #00F0FF]{upload_date}[/dim #00F0FF]")

    panel = Panel(
        table,
        title="[bold #39FF14]👾 ✓ Video Metadata Loaded[/bold #39FF14]",
        border_style="#00F0FF",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)
