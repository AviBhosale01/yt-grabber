import os
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import questionary
from rich.console import Console

from ui.format_menu import CUSTOM_STYLE
from utils.config import get_last_download_dir, set_last_download_dir
from utils.helpers import get_default_download_directory

console = Console()


def open_native_folder_dialog(initial_dir: Optional[str] = None) -> Optional[Path]:
    """Open the native OS File Explorer folder picker popup window.

    Args:
        initial_dir: Optional starting directory path.

    Returns:
        Resolved Path of selected folder, or None if cancelled.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.wm_attributes("-topmost", 1)
        root.focus_force()

        start_path = (
            initial_dir
            or get_last_download_dir()
            or str(get_default_download_directory())
        )

        selected = filedialog.askdirectory(
            title="Avii's YT Grabber — Select Destination Folder",
            initialdir=str(Path(start_path).resolve()),
            mustexist=True,
        )
        root.destroy()

        if selected:
            selected_path = Path(selected).resolve()
            set_last_download_dir(str(selected_path))
            return selected_path
        return None
    except Exception as e:
        return None


def select_download_destination(initial_dir: Optional[str] = None) -> Path:
    """Prompt the user for download destination using native OS popup, falling back to CLI.

    Args:
        initial_dir: Optional initial directory path string.

    Returns:
        Resolved Path object of the selected directory.
    """
    # 1. Try opening native OS folder picker popup first
    native_path = open_native_folder_dialog(initial_dir)
    if native_path:
        return native_path

    # 2. If user closed/cancelled popup or running headless, offer terminal choices
    last_dir = get_last_download_dir()
    fallback_dir = Path(last_dir) if (last_dir and Path(last_dir).exists()) else get_default_download_directory()

    console.print(
        f"[yellow]Window closed. Defaulting to:[/yellow] [cyan]{fallback_dir}[/cyan]"
    )

    action = questionary.select(
        "Destination Folder:",
        choices=[
            questionary.Choice(
                title=f"✅  Use default folder [{fallback_dir}]",
                value="DEFAULT",
            ),
            questionary.Choice(
                title="📂  Re-open OS Folder Picker window",
                value="REOPEN",
            ),
            questionary.Choice(
                title="📁  Browse folders in terminal (TUI)",
                value="TUI",
            ),
            questionary.Choice(
                title="✏️   Type path manually",
                value="MANUAL",
            ),
        ],
        style=CUSTOM_STYLE,
        use_indicator=True,
    ).ask()

    if action == "REOPEN":
        reopened = open_native_folder_dialog(str(fallback_dir))
        if reopened:
            return reopened
        return fallback_dir
    elif action == "TUI":
        return interactive_folder_picker(str(fallback_dir))
    elif action == "MANUAL":
        manual_input = questionary.text(
            "Enter folder path (or '.' for current directory):",
            style=CUSTOM_STYLE,
        ).ask()
        if manual_input:
            path = Path(manual_input.strip()).expanduser().resolve()
            path.mkdir(parents=True, exist_ok=True)
            set_last_download_dir(str(path))
            return path
        return fallback_dir
    else:
        set_last_download_dir(str(fallback_dir))
        return fallback_dir


def interactive_folder_picker(initial_dir: Optional[str] = None) -> Path:
    """Provide an arrow-key navigable terminal directory browser.

    Args:
        initial_dir: Optional initial directory path string.

    Returns:
        Resolved Path object of the selected directory.
    """
    if initial_dir and Path(initial_dir).exists() and Path(initial_dir).is_dir():
        current_path = Path(initial_dir).resolve()
    else:
        last_dir = get_last_download_dir()
        if last_dir and Path(last_dir).exists():
            current_path = Path(last_dir).resolve()
        else:
            current_path = get_default_download_directory().resolve()

    while True:
        try:
            subdirs = []
            for item in sorted(current_path.iterdir(), key=lambda p: p.name.lower()):
                try:
                    if item.is_dir() and not item.name.startswith("."):
                        subdirs.append(item.name)
                except (PermissionError, OSError):
                    continue
        except (PermissionError, OSError) as e:
            console.print(f"[bold red]Cannot access {current_path}: {e}[/bold red]")
            current_path = current_path.parent
            continue

        choices = [
            questionary.Choice(
                title=f"✅  Save here [{current_path}]",
                value=("CONFIRM", current_path),
            ),
            questionary.Choice(
                title="📂  Open OS File Dialog Popup",
                value=("NATIVE", None),
            ),
            questionary.Choice(
                title="✏️   Type path manually...",
                value=("MANUAL", None),
            ),
        ]

        if current_path.parent != current_path:
            choices.append(
                questionary.Choice(
                    title="📁  .. (Go up)",
                    value=("NAVIGATE", current_path.parent),
                )
            )

        if subdirs:
            choices.append(questionary.Separator("── Subfolders ──"))
            for subdir_name in subdirs:
                subdir_path = current_path / subdir_name
                choices.append(
                    questionary.Choice(
                        title=f"📁  {subdir_name}",
                        value=("NAVIGATE", subdir_path),
                    )
                )

        selected_action, target = questionary.select(
            f"Choose download folder (Current: {current_path}):",
            choices=choices,
            style=CUSTOM_STYLE,
            use_indicator=True,
        ).ask()

        if selected_action is None:
            set_last_download_dir(str(current_path))
            return current_path

        if selected_action == "CONFIRM":
            set_last_download_dir(str(current_path))
            return current_path

        elif selected_action == "NATIVE":
            res = open_native_folder_dialog(str(current_path))
            if res:
                return res

        elif selected_action == "NAVIGATE":
            current_path = target.resolve()

        elif selected_action == "MANUAL":
            manual_input = questionary.text(
                "Enter folder path (or '.' for current working dir):",
                style=CUSTOM_STYLE,
            ).ask()

            if manual_input:
                manual_path = Path(manual_input.strip()).expanduser().resolve()
                if not manual_path.exists():
                    try:
                        manual_path.mkdir(parents=True, exist_ok=True)
                        console.print(f"[green]Created folder: {manual_path}[/green]")
                    except Exception as e:
                        console.print(f"[bold red]Failed to create directory {manual_path}: {e}[/bold red]")
                        continue
                if manual_path.is_dir():
                    set_last_download_dir(str(manual_path))
                    return manual_path
                else:
                    console.print(f"[bold red]{manual_path} is not a directory.[/bold red]")
