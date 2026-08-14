import re
import unicodedata

# Regex matching various valid YouTube URL formats
YOUTUBE_URL_REGEX = re.compile(
    r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com/(watch\?v=|embed/|v/|shorts/|live/)|youtu\.be/)[a-zA-Z0-9_-]{11}(.*)?$"
)

# Set of invalid filename characters on Windows and UNIX
INVALID_CHARS_REGEX = re.compile(r'[\\/*?:"<>|]')


def is_valid_youtube_url(url: str) -> bool:
    """Validate if the given string is a plausible YouTube URL.

    Args:
        url: URL string to check.

    Returns:
        True if valid YouTube URL format, False otherwise.
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(YOUTUBE_URL_REGEX.match(url))


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """Sanitize a string to be a safe filesystem filename across Windows, macOS, and Linux.

    Args:
        name: Original filename candidate.
        max_length: Maximum permitted length for the filename stem.

    Returns:
        A sanitized string safe for file creation.
    """
    if not name:
        return "video"

    # Normalize unicode characters
    name = unicodedata.normalize("NFKC", name)

    # Remove illegal characters: \ / : * ? " < > |
    cleaned = INVALID_CHARS_REGEX.sub("_", name)

    # Replace control characters
    cleaned = "".join(c for c in cleaned if ord(c) >= 32)

    # Strip leading/trailing whitespaces and dots (dots at end are problematic on Windows)
    cleaned = cleaned.strip(". ")

    if not cleaned:
        cleaned = "download"

    # Restrict length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip(". ")

    return cleaned
