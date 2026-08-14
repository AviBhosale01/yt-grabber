import os
import sys
from pathlib import Path
from typing import Optional

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


def interactive_folder_picker(initial_dir: Optional[str] = None) -> Path:
    """Provide an arrow-key navigable directory browser to select a download destination.

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
            # List subdirectories
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

        # Build choices
        choices = [
            questionary.Choice(
                title=f"✅  Save here [{current_path}]",
                value=("CONFIRM", current_path),
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
            # User pressed Ctrl+C or Esc, fallback to current_path
            set_last_download_dir(str(current_path))
            return current_path

        if selected_action == "CONFIRM":
            set_last_download_dir(str(current_path))
            return current_path

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
