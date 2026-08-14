import os
import shutil
from pathlib import Path
from typing import Optional, Union


def format_bytes(bytes_num: Optional[Union[int, float]]) -> str:
    """Convert bytes count to human-readable string (e.g., 14.5 MB, 1.2 GB).

    Args:
        bytes_num: Number of bytes or None.

    Returns:
        Formatted string or 'size unknown'.
    """
    if bytes_num is None or bytes_num <= 0:
        return "size unknown"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_num)
    unit_index = 0

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: Optional[Union[int, float]]) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS format.

    Args:
        seconds: Duration in seconds or None.

    Returns:
        Formatted duration string.
    """
    if seconds is None or seconds < 0:
        return "--:--"

    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def check_ffmpeg_installed() -> bool:
    """Check if ffmpeg executable is available on system PATH.

    Returns:
        True if ffmpeg is found, False otherwise.
    """
    return shutil.which("ffmpeg") is not None


def get_default_download_directory() -> Path:
    """Get the operating system's standard Downloads folder.

    Returns:
        Path to Downloads directory, falling back to User Home if nonexistent.
    """
    # Windows / macOS / Linux standard downloads
    downloads = Path.home() / "Downloads"
    if downloads.exists() and downloads.is_dir():
        return downloads

    # Fallback to home directory
    return Path.home()
