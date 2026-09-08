import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from core.extractor import extract_video_info, build_format_options
from core.downloader import download_media
from utils.helpers import check_ffmpeg_installed, format_duration
from utils.validators import is_valid_youtube_url, sanitize_filename

app = FastAPI(
    title="Avii's YT Grabber API",
    description="Backend API for high-definition YouTube video and MP3 downloads",
    version="2.0.0",
)

# Enable CORS for Vercel and mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cleanup_temp_dir(temp_path: str):
    """Clean up temporary directory and downloaded media file after response completes."""
    try:
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path, ignore_errors=True)
    except Exception:
        pass


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify API and FFmpeg status."""
    return {
        "status": "ok",
        "service": "Avii's YT Grabber Engine",
        "ffmpeg_installed": check_ffmpeg_installed(),
    }


@app.get("/api/info")
def get_video_info(url: str = Query(..., description="YouTube video or Shorts URL")):
    """Extract metadata and all genuine available formats for the specified YouTube video."""
    url = url.strip()
    if not is_valid_youtube_url(url):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Invalid YouTube URL provided."},
        )

    info, err = extract_video_info(url)
    if err or not info:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": err or "Failed to extract video details."},
        )

    formats = build_format_options(info)

    # Format upload date
    upload_date = info.get("upload_date")
    if upload_date and len(upload_date) == 8:
        upload_date_fmt = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
    else:
        upload_date_fmt = "N/A"

    thumbnail = info.get("thumbnail")
    thumbnails = info.get("thumbnails", [])
    if thumbnails:
        thumbnail = thumbnails[-1].get("url") or thumbnail

    return {
        "success": True,
        "video": {
            "title": info.get("title", "YouTube Video"),
            "channel": info.get("uploader") or info.get("channel", "Unknown Channel"),
            "duration_seconds": info.get("duration", 0),
            "duration_str": format_duration(info.get("duration")),
            "views": info.get("view_count", 0),
            "upload_date": upload_date_fmt,
            "thumbnail": thumbnail,
        },
        "formats": formats,
    }


@app.get("/api/download")
def download_stream(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube video URL"),
    type: str = Query("video", description="Type: video, audio, original_audio"),
    height: int = Query(0, description="Target vertical resolution height (e.g. 1080, 720, 2160)"),
    ext: str = Query("mp4", description="Output container extension (mp4, mp3, m4a)"),
    audio_quality: str = Query("192", description="Audio bitrate in kbps (320, 256, 192, 128)"),
    title: Optional[str] = Query(None, description="Optional custom video title"),
):
    """Download, merge with FFmpeg, and stream the file directly to the client browser/app."""
    url = url.strip()
    if not is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")

    # Determine format selector based on requested quality
    if type == "audio":
        format_selector = "bestaudio/best"
    elif type == "original_audio":
        format_selector = "bestaudio[ext=m4a]/bestaudio/best"
    else:
        if height > 0:
            format_selector = (
                f"bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height={height}]+bestaudio/"
                f"best[height={height}]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best[height<={height}]/"
                f"best"
            )
        else:
            format_selector = "bestvideo+bestaudio/best"

    selected_format = {
        "type": type,
        "ext": ext,
        "height": height,
        "audio_quality": audio_quality,
        "format_selector": format_selector,
    }

    # Fetch title if not provided
    if not title:
        info, _ = extract_video_info(url)
        title = info.get("title", "download") if info else "download"

    safe_title = sanitize_filename(title)
    temp_dir = Path(tempfile.mkdtemp())

    success, saved_file_path, err, _ = download_media(url, selected_format, temp_dir, safe_title)

    if not success or not saved_file_path or not Path(saved_file_path).exists():
        cleanup_temp_dir(str(temp_dir))
        raise HTTPException(status_code=500, detail=err or "Failed to process download stream.")

    file_name = Path(saved_file_path).name
    media_type = "audio/mpeg" if ext == "mp3" else ("audio/mp4" if ext == "m4a" else "video/mp4")

    # Schedule temporary folder cleanup after response has been fully streamed
    background_tasks.add_task(cleanup_temp_dir, str(temp_dir))

    return FileResponse(
        path=saved_file_path,
        filename=file_name,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Cache-Control": "no-cache",
        },
    )


# Mount public directory for local testing
public_dir = Path(__file__).parent / "public"
if public_dir.exists():
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Avii's YT Grabber Web Server on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
