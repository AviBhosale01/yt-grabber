import sys
import pyfiglet
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
    """Render the application banner with pyfiglet ASCII art and rich styling."""
    try:
        ascii_title = pyfiglet.figlet_format("YT GRABBER", font="slant").rstrip()
    except Exception:
        ascii_title = "YT GRABBER"

    title_text = Text()
    # Apply a neon gradient effect to ASCII text
    lines = ascii_title.split("\n")
    colors = ["bright_cyan", "cyan", "deep_sky_blue1", "magenta", "bright_magenta"]
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        title_text.append(line + "\n", style=f"bold {color}")

    subtitle = Text()
    subtitle.append("⚡ Terminal YouTube Downloader ⚡\n", style="bold yellow")
    subtitle.append("made with ❤️  by ", style="dim white")
    subtitle.append("Avii", style="bold magenta underline")

    banner_content = Text()
    banner_content.append_text(title_text)
    banner_content.append_text(subtitle)

    ffmpeg_ready = check_ffmpeg_installed()
    status_style = "bold green" if ffmpeg_ready else "bold red"
    status_text = "● FFmpeg Ready" if ffmpeg_ready else "▲ FFmpeg Missing (Remuxing limited)"

    panel = Panel(
        banner_content,
        border_style="bright_magenta",
        box=box.ROUNDED,
        title="[bold bright_cyan]Avii's YT Grabber[/bold bright_cyan]",
        subtitle=f"[{status_style}]{status_text}[/{status_style}]",
        subtitle_align="right",
        padding=(1, 2),
    )
    console.print(panel)


def print_video_info(info: dict) -> None:
    """Print a clean metadata summary card for the fetched YouTube video.

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
    table.add_column("Key", style="bold cyan", width=12)
    table.add_column("Value", style="white")

    table.add_row("🎬 Title:", f"[bold white]{title}[/bold white]")
    table.add_row("📺 Channel:", f"[yellow]{channel}[/yellow]")
    table.add_row("⏱️ Duration:", f"[green]{duration}[/green]")
    table.add_row("👀 Views:", f"[bright_black]{views_str}[/bright_black]")
    table.add_row("📅 Uploaded:", f"[bright_black]{upload_date}[/bright_black]")

    panel = Panel(
        table,
        title="[bold green]✓ Video Metadata Found[/bold green]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)
