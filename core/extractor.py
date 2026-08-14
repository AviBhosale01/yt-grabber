import sys
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import yt_dlp
from rich.console import Console


from utils.helpers import format_bytes

console = Console()


def extract_video_info(url: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Extract metadata and format information from a YouTube URL.

    Args:
        url: YouTube video URL.

    Returns:
        Tuple of (info_dict, None) on success, or (None, error_message) on failure.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb", "android", "web", "tv"],
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return None, "No video information could be retrieved."
            return info, None
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Private video" in error_msg:
            return None, "This video is private and cannot be accessed."
        elif "Video unavailable" in error_msg:
            return None, "This video is unavailable or deleted."
        elif "Sign in to confirm your age" in error_msg or "age" in error_msg.lower():
            return None, "This video is age-restricted and requires authentication."
        elif "country" in error_msg.lower() or "blocked" in error_msg.lower():
            return None, "This video is not available in your region."
        elif "Unable to download webpage" in error_msg or "network" in error_msg.lower():
            return None, "Network error: Please check your internet connection."
        else:
            # Clean up yt-dlp prefix if present
            clean_msg = error_msg.replace("ERROR: ", "").strip()
            return None, f"Download error: {clean_msg}"
    except Exception as e:
        return None, f"Unexpected error while extracting video info: {e}"


def build_format_options(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse available formats from extracted metadata and build a deduplicated list of options.

    Args:
        info: Extracted video metadata dictionary.

    Returns:
        List of format options formatted for interactive UI selection.
    """
    raw_formats = info.get("formats", [])
    duration = info.get("duration", 0) or 0

    # Best audio estimate
    best_audio_size = 0
    best_audio_tbr = 0
    for f in raw_formats:
        if f.get("vcodec") == "none" and f.get("acodec") != "none":
            size = f.get("filesize") or f.get("filesize_approx")
            if not size and f.get("tbr") and duration:
                size = int(f["tbr"] * 1000 / 8 * duration)
            if size and size > best_audio_size:
                best_audio_size = size
            if f.get("tbr") and f["tbr"] > best_audio_tbr:
                best_audio_tbr = f["tbr"]

    # Gather available video resolutions
    # Key by resolution height (e.g. 2160, 1440, 1080, 720, 480, 360, 240, 144)
    resolutions_map: Dict[int, Dict[str, Any]] = {}

    for f in raw_formats:
        height = f.get("height")
        vcodec = f.get("vcodec")

        if not height or vcodec == "none":
            continue

        size = f.get("filesize") or f.get("filesize_approx")
        if not size and f.get("tbr") and duration:
            size = int(f["tbr"] * 1000 / 8 * duration)

        if height not in resolutions_map:
            resolutions_map[height] = {
                "height": height,
                "video_size": size or 0,
                "is_progressive": f.get("acodec") != "none",
                "ext": "mp4",
                "format_note": f.get("format_note", ""),
                "fps": f.get("fps"),
            }
        else:
            # Update with better size estimate if available
            curr = resolutions_map[height]
            if size and (curr["video_size"] == 0 or size > curr["video_size"]):
                curr["video_size"] = size
            if f.get("acodec") != "none":
                curr["is_progressive"] = True

    # Standard video quality labels and sorting
    sorted_heights = sorted(resolutions_map.keys(), reverse=True)
    options: List[Dict[str, Any]] = []

    for h in sorted_heights:
        data = resolutions_map[h]
        video_size = data["video_size"]

        if data["is_progressive"] and video_size > 0:
            total_size = video_size
        else:
            total_size = (video_size + best_audio_size) if (video_size > 0 and best_audio_size > 0) else video_size

        size_display = format_bytes(total_size) if total_size > 0 else "size unknown"

        # Quality badge
        if h >= 2160:
            quality_tag = f"{h}p 4K"
        elif h >= 1440:
            quality_tag = f"{h}p 2K"
        elif h >= 1080:
            quality_tag = f"{h}p HD"
        elif h >= 720:
            quality_tag = f"{h}p HD"
        else:
            quality_tag = f"{h}p"

        # Construct format selector
        # yt-dlp standard selector to get best video up to height merged with best audio into mp4
        format_selector = (
            f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={h}]+bestaudio/"
            f"best[height<={h}]/best"
        )

        label = f"🎬  {quality_tag:<9} MP4  (Video + Audio)   ~{size_display}"

        options.append({
            "type": "video",
            "height": h,
            "quality_tag": quality_tag,
            "format_selector": format_selector,
            "ext": "mp4",
            "label": label,
            "size_str": size_display,
        })

    # If no video formats were detected (rare), fallback to standard best
    if not options:
        options.append({
            "type": "video",
            "height": 0,
            "quality_tag": "Best",
            "format_selector": "bestvideo+bestaudio/best",
            "ext": "mp4",
            "label": "🎬  Best Available MP4 (Video + Audio)",
            "size_str": "size unknown",
        })

    # Separator
    options.append({
        "is_separator": True,
        "label": "──────────────────────────────────────────",
    })

    # Audio option (MP3)
    audio_size_display = format_bytes(best_audio_size) if best_audio_size > 0 else "size unknown"
    options.append({
        "type": "audio",
        "height": 0,
        "quality_tag": "Audio MP3",
        "format_selector": "bestaudio/best",
        "ext": "mp3",
        "label": f"🎵  Audio only — MP3 (Best Quality)     ~{audio_size_display}",
        "size_str": audio_size_display,
    })

    return options
