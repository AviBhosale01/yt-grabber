import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import yt_dlp

from ui.progress import DownloadProgressManager
from utils.validators import sanitize_filename


def download_media(
    url: str,
    selected_format: Dict[str, Any],
    destination_dir: Path,
    video_title: str,
) -> Tuple[bool, Optional[str], Optional[str], float]:
    """Download the media stream according to the selected format and destination.

    Args:
        url: YouTube video URL.
        selected_format: Format specification dictionary from build_format_options.
        destination_dir: Directory path where output file will be saved.
        video_title: Video title for sanitization and output naming.

    Returns:
        Tuple of (success, saved_file_path, error_message, elapsed_seconds).
    """
    safe_title = sanitize_filename(video_title)
    fmt_type = selected_format.get("type", "video")
    ext = selected_format.get("ext", "mp4")

    expected_filename = f"{safe_title}.{ext}"
    progress_manager = DownloadProgressManager(expected_filename)

    # Base outtmpl pattern
    outtmpl_pattern = str(destination_dir / f"{safe_title}.%(ext)s")

    format_selector = selected_format.get("format_selector", "best")

    ydl_opts: Dict[str, Any] = {
        "outtmpl": outtmpl_pattern,
        "format": format_selector,
        "progress_hooks": [progress_manager.ytdlp_progress_hook],
        "postprocessor_hooks": [progress_manager.ytdlp_postprocessor_hook],
        "quiet": True,
        "no_warnings": True,
        "windowsfilenames": True,
        "retries": 10,
        "fragment_retries": 10,
        "js_runtimes": {"node": {}},
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    if fmt_type == "audio":
        audio_q = selected_format.get("audio_quality", "192")
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_q,
            }
        ]
    elif fmt_type == "video":
        ydl_opts["merge_output_format"] = "mp4"

    start_time = time.time()
    progress_manager.start()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        elapsed = time.time() - start_time
        progress_manager.stop()

        # Locate saved file
        saved_file = progress_manager.downloaded_file_path
        if not saved_file or not Path(saved_file).exists():
            candidates = list(destination_dir.glob(f"{safe_title}.*"))
            if candidates:
                exact = [c for c in candidates if c.suffix.lower() == f".{ext}"]
                saved_file = str(exact[0] if exact else candidates[0])
            else:
                saved_file = str(destination_dir / expected_filename)

        return True, saved_file, None, elapsed

    except KeyboardInterrupt:
        progress_manager.stop()
        _cleanup_partial_files(destination_dir, safe_title)
        return False, None, "Download cancelled by user.", time.time() - start_time

    except yt_dlp.utils.DownloadError as e:
        progress_manager.stop()
        _cleanup_partial_files(destination_dir, safe_title)
        error_msg = str(e).replace("ERROR: ", "").strip()
        return False, None, f"Download failed: {error_msg}", time.time() - start_time

    except Exception as e:
        progress_manager.stop()
        _cleanup_partial_files(destination_dir, safe_title)
        return False, None, f"Unexpected error during download: {e}", time.time() - start_time


def _cleanup_partial_files(directory: Path, safe_title: str) -> None:
    """Remove temporary partial or incomplete download files on error or cancellation.

    Args:
        directory: Destination folder.
        safe_title: Sanitized title prefix.
    """
    try:
        for file in directory.glob(f"{safe_title}.*"):
            if file.suffix in [".part", ".ytdl", ".temp", ".tmp"]:
                try:
                    file.unlink()
                except Exception:
                    pass
    except Exception:
        pass
