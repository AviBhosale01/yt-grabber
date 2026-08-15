import sys
from typing import Any, Dict, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import questionary
from questionary import Style


# Retro 8-Bit Pixel Arcade theme for questionary
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#FFE600 bold"),
        ("question", "fg:#FFFFFF bold"),
        ("answer", "fg:#39FF14 bold"),
        ("pointer", "fg:#FFE600 bold"),
        ("highlighted", "fg:#00F0FF bold"),
        ("selected", "fg:#39FF14"),
        ("separator", "fg:#FF007F bold"),
        ("instruction", "fg:#FF9100 italic"),
        ("text", "fg:#FFFFFF"),
        ("disabled", "fg:#555555 italic"),
    ]
)


def select_format_menu(options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Display an arrow-key navigable menu for choosing video/audio quality.

    Args:
        options: List of format option dictionaries created by extractor.py.

    Returns:
        The selected format dictionary, or None if cancelled.
    """
    if not options:
        return None

    choices = []
    for opt in options:
        if opt.get("is_separator"):
            choices.append(questionary.Separator(opt.get("label", "──────────────────────────")))
        else:
            choices.append(
                questionary.Choice(
                    title=opt["label"],
                    value=opt,
                )
            )

    result = questionary.select(
        "Choose a format (↑↓ to navigate, Enter to select):",
        choices=choices,
        style=CUSTOM_STYLE,
        use_indicator=True,
    ).ask()

    return result
