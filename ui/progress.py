import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.table import Table
from rich import box

from utils.helpers import format_bytes

console = Console()


class DownloadProgressManager:
    """Manages the rich live progress bar and status transitions for yt-dlp downloads."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.console = console
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
        self.downloaded_file_path: Optional[str] = None
        self.total_size_bytes: Optional[int] = None
        self.current_phase: str = "downloading"
        self._is_active = False

    def start(self) -> None:
        """Initialize and start the live Rich progress display."""
        self.progress = Progress(
            SpinnerColumn(spinner_name="dots", style="bright_cyan"),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(
                bar_width=35,
                style="grey30",
                complete_style="bold bright_magenta",
                finished_style="bold bright_green",
            ),
            TaskProgressColumn(text_format="[bold bright_green]{task.percentage:>3.0f}%[/bold bright_green]"),
            TextColumn("•", style="dim"),
            DownloadColumn(),
            TextColumn("•", style="dim"),
            TransferSpeedColumn(),
            TextColumn("•", style="dim"),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )
        self.progress.start()
        display_name = (self.filename[:30] + "...") if len(self.filename) > 33 else self.filename
        self.task_id = self.progress.add_task(f"Downloading {display_name}", total=None)
        self._is_active = True

    def stop(self) -> None:
        """Stop the progress bar display."""
        if self.progress and self._is_active:
            self.progress.stop()
            self._is_active = False

    def ytdlp_progress_hook(self, d: Dict[str, Any]) -> None:
        """Handle status callbacks from yt-dlp download hooks."""
        if not self.progress or self.task_id is None:
            return

        status = d.get("status")

        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            filename = d.get("filename", self.filename)
            base_name = Path(filename).name
            display_name = (base_name[:28] + "...") if len(base_name) > 31 else base_name

            if total and total > 0:
                self.progress.update(
                    self.task_id,
                    completed=downloaded,
                    total=total,
                    description=f"Downloading [bright_white]{display_name}[/bright_white]",
                )
            else:
                self.progress.update(
                    self.task_id,
                    completed=downloaded,
                    description=f"Downloading [bright_white]{display_name}[/bright_white]",
                )

        elif status == "finished":
            filename = d.get("filename")
            if filename:
                self.downloaded_file_path = filename
            total = d.get("total_bytes") or d.get("downloaded_bytes")
            if total:
                self.total_size_bytes = total
                self.progress.update(self.task_id, completed=total, total=total)

    def ytdlp_postprocessor_hook(self, d: Dict[str, Any]) -> None:
        """Handle status callbacks from yt-dlp post-processors (e.g. ffmpeg merging, MP3 extraction)."""
        if not self.progress or self.task_id is None:
            return

        status = d.get("status")
        postprocessor = d.get("postprocessor", "")

        if status == "started":
            if "Merger" in postprocessor:
                self.progress.update(
                    self.task_id,
                    description="[bold yellow]⚡ Merging audio & video via FFmpeg...[/bold yellow]",
                )
            elif "ExtractAudio" in postprocessor:
                self.progress.update(
                    self.task_id,
                    description="[bold yellow]🎵 Converting audio to MP3 via FFmpeg...[/bold yellow]",
                )
            elif "Fixup" in postprocessor or "Embed" in postprocessor:
                self.progress.update(
                    self.task_id,
                    description="[bold yellow]🔧 Post-processing media streams...[/bold yellow]",
                )
            else:
                self.progress.update(
                    self.task_id,
                    description="[bold yellow]⚙️ Finalizing output file...[/bold yellow]",
                )

        elif status == "finished":
            info = d.get("info_dict", {})
            filepath = info.get("filepath") or info.get("_filename")
            if filepath:
                self.downloaded_file_path = filepath

    def show_success(self, final_file_path: str, duration_sec: Optional[float] = None) -> None:
        """Display a clean, stylized success panel upon completion."""
        self.stop()

        path_obj = Path(final_file_path)
        file_size_str = "size unknown"
        if path_obj.exists():
            file_size_str = format_bytes(path_obj.stat().st_size)
        elif self.total_size_bytes:
            file_size_str = format_bytes(self.total_size_bytes)

        dur_text = f" in {duration_sec:.1f}s" if duration_sec is not None else ""

        table = Table(show_header=False, box=box.SIMPLE, expand=True)
        table.add_column("Key", style="bold green", width=14)
        table.add_column("Value", style="bright_white")

        table.add_row("📁 Saved Path:", f"[bold cyan]{path_obj.resolve()}[/bold cyan]")
        table.add_row("📦 File Size:", f"[bold yellow]{file_size_str}[/bold yellow]{dur_text}")
        table.add_row("🎯 File Name:", f"[bold white]{path_obj.name}[/bold white]")

        panel = Panel(
            table,
            title="[bold bright_green]✔ Download Completed Successfully![/bold bright_green]",
            border_style="bright_green",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        self.console.print()
        self.console.print(panel)
