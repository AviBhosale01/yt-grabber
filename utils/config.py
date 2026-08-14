import json
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_FILE_PATH = Path.home() / ".yt_grabber_config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file.

    Returns:
        Configuration dictionary.
    """
    if not CONFIG_FILE_PATH.exists():
        return {}

    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config_data: Dict[str, Any]) -> None:
    """Save configuration dictionary to JSON file.

    Args:
        config_data: Configuration data to persist.
    """
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_last_download_dir() -> Optional[str]:
    """Retrieve last used download directory if valid.

    Returns:
        Path string or None.
    """
    config = load_config()
    last_dir = config.get("last_download_dir")
    if last_dir and Path(last_dir).exists() and Path(last_dir).is_dir():
        return last_dir
    return None


def set_last_download_dir(dir_path: str) -> None:
    """Update last used download directory in config.

    Args:
        dir_path: Path string.
    """
    config = load_config()
    config["last_download_dir"] = dir_path
    save_config(config)


def add_history_entry(title: str, file_path: str, file_size: str, format_name: str) -> None:
    """Add a completed download entry to history log.

    Args:
        title: Video title.
        file_path: Saved file path.
        file_size: Formatted size.
        format_name: Selected format description.
    """
    config = load_config()
    history: List[Dict[str, str]] = config.get("download_history", [])

    entry = {
        "title": title,
        "path": file_path,
        "size": file_size,
        "format": format_name,
    }

    # Prepend and limit to 50 entries
    history.insert(0, entry)
    config["download_history"] = history[:50]
    save_config(config)
