import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

import questionary
from rich.console import Console


from core.downloader import download_media
from core.extractor import build_format_options, extract_video_info
from ui.banner import print_banner, print_video_info
from ui.folder_picker import select_download_destination, interactive_folder_picker
from ui.format_menu import CUSTOM_STYLE, select_format_menu
from ui.progress import DownloadProgressManager
from utils.config import add_history_entry
from utils.helpers import check_ffmpeg_installed, format_bytes
from utils.validators import is_valid_youtube_url

console = Console()


def run_app() -> None:
    """Run the main interactive loop for Avii's YT Grabber."""
    while True:
        console.clear()
        print_banner()

        # Check FFmpeg availability and warn if missing
        if not check_ffmpeg_installed():
            console.print(
                "[bold yellow]⚠️  Notice: FFmpeg is not found on your PATH.[/bold yellow]\n"
                "[dim]High-resolution stream merging and MP3 conversion require FFmpeg.\n"
                "Please refer to the README for FFmpeg setup instructions.[/dim]\n"
            )

        # 1. URL Input & Validation Loop
        url = None
        while True:
            try:
                raw_input = questionary.text(
                    "Paste YouTube link (or 'q' to quit):",
                    style=CUSTOM_STYLE,
                ).ask()
            except KeyboardInterrupt:
                console.print("\n[yellow]Session cancelled. Goodbye![/yellow]")
                sys.exit(0)

            if raw_input is None or raw_input.strip().lower() in ["q", "quit", "exit"]:
                console.print("[bold magenta]Thanks for using Avii's YT Grabber! Goodbye 👋[/bold magenta]")
                sys.exit(0)

            clean_url = raw_input.strip()
            if not clean_url:
                continue

            if not is_valid_youtube_url(clean_url):
                console.print(
                    "[bold red]❌ Invalid YouTube URL. Please enter a valid video or shorts link.[/bold red]\n"
                )
                continue

            url = clean_url
            break

        # 2. Fetch Video Metadata with Spinner
        console.print()
        with console.status("[bold cyan]⠋ Fetching video info...[/bold cyan]", spinner="dots"):
            info, error_msg = extract_video_info(url)

        if error_msg or not info:
            console.print(f"[bold red]❌ {error_msg}[/bold red]\n")
            if not questionary.confirm("Would you like to try another link?", default=True, style=CUSTOM_STYLE).ask():
                break
            continue

        # 3. Display Metadata Card
        print_video_info(info)
        console.print()

        # 4. Format Selection Menu
        format_options = build_format_options(info)
        selected_format = select_format_menu(format_options)

        if not selected_format:
            console.print("[yellow]Format selection cancelled.[/yellow]\n")
            if not questionary.confirm("Download another video?", default=True, style=CUSTOM_STYLE).ask():
                break
            continue

        console.print()

        # 5. Destination Folder Selection (Opens Native OS Explorer Dialog)
        console.print("[dim]Opening folder selector window...[/dim]")
        selected_dir = select_download_destination()
        console.print(f"[bold green]✓ Selected folder:[/bold green] [cyan]{selected_dir}[/cyan]\n")

        # 6. Download Execution
        video_title = info.get("title", "YouTube Video")
        console.print(f"[bold cyan]Starting download for:[/bold cyan] [bold white]{video_title}[/bold white]")

        success, saved_file_path, err, elapsed = download_media(
            url=url,
            selected_format=selected_format,
            destination_dir=selected_dir,
            video_title=video_title,
        )

        # 7. Post-Download Results
        if success and saved_file_path:
            # Show styled success card
            mgr = DownloadProgressManager(Path(saved_file_path).name)
            mgr.show_success(saved_file_path, duration_sec=elapsed)

            # Record history
            size_str = format_bytes(Path(saved_file_path).stat().st_size) if Path(saved_file_path).exists() else "unknown"
            add_history_entry(
                title=video_title,
                file_path=str(Path(saved_file_path).resolve()),
                file_size=size_str,
                format_name=selected_format.get("quality_tag", "Standard"),
            )
        else:
            console.print(f"\n[bold red]❌ {err}[/bold red]\n")

        # 8. Loop Prompt
        try:
            download_another = questionary.confirm(
                "Download another video?",
                default=True,
                style=CUSTOM_STYLE,
            ).ask()
        except KeyboardInterrupt:
            break

        if not download_another:
            console.print("\n[bold magenta]Thanks for using Avii's YT Grabber! Goodbye 👋[/bold magenta]")
            break


def main() -> None:
    """Entry point with graceful top-level signal handling."""
    try:
        run_app()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Process interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
