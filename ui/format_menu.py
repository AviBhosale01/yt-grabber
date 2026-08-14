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


# Neon / Cyberpunk terminal theme for questionary
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#ff007f bold"),
        ("question", "fg:#f8f8f2 bold"),
        ("answer", "fg:#50fa7b bold"),
        ("pointer", "fg:#00ffff bold"),
        ("highlighted", "fg:#00ffff bold"),
        ("selected", "fg:#50fa7b"),
        ("separator", "fg:#6272a4"),
        ("instruction", "fg:#bd93f9 italic"),
        ("text", "fg:#f8f8f2"),
        ("disabled", "fg:#6272a4 italic"),
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
