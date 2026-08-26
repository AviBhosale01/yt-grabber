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
    """Extract full metadata and all available formats from a YouTube URL.

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
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
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
            clean_msg = error_msg.replace("ERROR: ", "").strip()
            return None, f"Download error: {clean_msg}"
    except Exception as e:
        return None, f"Unexpected error while extracting video info: {e}"


def build_format_options(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse all available video resolutions and audio qualities from metadata.

    Args:
        info: Extracted video metadata dictionary.

    Returns:
        List of deduplicated format option dictionaries for UI selection.
    """
    raw_formats = info.get("formats", [])
    duration = info.get("duration", 0) or 0

    # 1. Best Audio Stream Estimation
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

    # 2. Gather All Available Video Resolutions (Deduplicate by height, tracking highest FPS & size)
    resolutions_map: Dict[int, Dict[str, Any]] = {}

    for f in raw_formats:
        height = f.get("height")
        vcodec = f.get("vcodec")

        if not height or vcodec == "none":
            continue

        size = f.get("filesize") or f.get("filesize_approx")
        if not size and f.get("tbr") and duration:
            size = int(f["tbr"] * 1000 / 8 * duration)

        fps = f.get("fps") or 30

        if height not in resolutions_map:
            resolutions_map[height] = {
                "height": height,
                "fps": fps,
                "video_size": size or 0,
                "is_progressive": f.get("acodec") != "none",
                "ext": "mp4",
                "format_note": f.get("format_note", ""),
            }
        else:
            curr = resolutions_map[height]
            if fps > curr["fps"]:
                curr["fps"] = fps
            if size and (curr["video_size"] == 0 or size > curr["video_size"]):
                curr["video_size"] = size
            if f.get("acodec") != "none":
                curr["is_progressive"] = True

    # 3. Build Video Quality Options (Highest resolution to lowest)
    sorted_heights = sorted(resolutions_map.keys(), reverse=True)
    options: List[Dict[str, Any]] = []

    for h in sorted_heights:
        data = resolutions_map[h]
        video_size = data["video_size"]
        fps = data["fps"]

        if data["is_progressive"] and video_size > 0:
            total_size = video_size
        else:
            total_size = (video_size + best_audio_size) if (video_size > 0 and best_audio_size > 0) else video_size

        size_display = format_bytes(total_size) if total_size > 0 else "size unknown"

        # Construct descriptive quality tags and badges
        fps_str = f" {fps}fps" if fps >= 50 else ""
        if h >= 4320:
            quality_tag = f"8K {h}p{fps_str}"
            desc = "Ultra HD 8K"
        elif h >= 2160:
            quality_tag = f"4K {h}p{fps_str}"
            desc = "Ultra HD 4K"
        elif h >= 1440:
            quality_tag = f"2K {h}p{fps_str}"
            desc = "Quad HD 2K"
        elif h >= 1080:
            quality_tag = f"1080p{fps_str}"
            desc = "Full HD"
        elif h >= 720:
            quality_tag = f"720p{fps_str}"
            desc = "High Def"
        elif h >= 480:
            quality_tag = f"480p"
            desc = "Standard"
        elif h >= 360:
            quality_tag = f"360p"
            desc = "Medium"
        elif h >= 240:
            quality_tag = f"240p"
            desc = "Low"
        else:
            quality_tag = f"{h}p"
            desc = "Data Saver"

        # Resilient format selector for video + best audio merged into MP4
        format_selector = (
            f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={h}]+bestaudio/"
            f"best[height<={h}]/"
            f"bestvideo+bestaudio/"
            f"best"
        )

        label = f"🎬  {quality_tag:<14} MP4  ({desc:<11})   ~{size_display}"

        options.append({
            "type": "video",
            "height": h,
            "quality_tag": quality_tag,
            "format_selector": format_selector,
            "ext": "mp4",
            "label": label,
            "size_str": size_display,
        })

    # Fallback if no video formats were parsed
    if not options:
        options.append({
            "type": "video",
            "height": 0,
            "quality_tag": "Best",
            "format_selector": "bestvideo+bestaudio/best",
            "ext": "mp4",
            "label": "🎬  Best Available Video (Auto MP4)",
            "size_str": "size unknown",
        })

    # Separator
    options.append({
        "is_separator": True,
        "label": "──────────── 🎵 Audio Only Options ────────────",
    })

    # 4. Audio Options (Various MP3 bitrates & Original Audio)
    # Estimate MP3 sizes by bitrate
    def est_audio_size(kbps: int) -> str:
        if duration > 0:
            bytes_val = int((kbps * 1000 / 8) * duration)
            return format_bytes(bytes_val)
        return format_bytes(best_audio_size) if best_audio_size > 0 else "size unknown"

    audio_qualities = [
        ("320", "Ultra Quality (320 kbps)", est_audio_size(320)),
        ("256", "High Quality  (256 kbps)", est_audio_size(256)),
        ("192", "Standard      (192 kbps)", est_audio_size(192)),
        ("128", "Compact Voice (128 kbps)", est_audio_size(128)),
    ]

    for bitrate, name, sz in audio_qualities:
        options.append({
            "type": "audio",
            "height": 0,
            "audio_quality": bitrate,
            "quality_tag": f"MP3 {bitrate}k",
            "format_selector": "bestaudio/best",
            "ext": "mp3",
            "label": f"🎵  MP3 — {name:<24} ~{sz}",
            "size_str": sz,
        })

    # Original audio stream option (no re-encoding)
    orig_sz = format_bytes(best_audio_size) if best_audio_size > 0 else "size unknown"
    options.append({
        "type": "original_audio",
        "height": 0,
        "quality_tag": "Original Audio",
        "format_selector": "bestaudio[ext=m4a]/bestaudio/best",
        "ext": "m4a",
        "label": f"🎵  Original Audio (.M4A / Best Bitrate)     ~{orig_sz}",
        "size_str": orig_sz,
    })

    return options
