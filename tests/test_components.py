import os
import unittest
from pathlib import Path
from unittest.mock import patch

from core.extractor import build_format_options
from utils.config import (
    CONFIG_FILE_PATH,
    add_history_entry,
    get_last_download_dir,
    load_config,
    save_config,
    set_last_download_dir,
)
from utils.helpers import check_ffmpeg_installed, format_bytes, format_duration
from utils.validators import is_valid_youtube_url, sanitize_filename


class TestValidators(unittest.TestCase):
    """Test URL and filename validators."""

    def test_valid_youtube_urls(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://youtube.com/live/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(is_valid_youtube_url(url), f"Failed for valid URL: {url}")

    def test_invalid_youtube_urls(self):
        invalid_urls = [
            "",
            "not a url",
            "https://vimeo.com/123456789",
            "https://facebook.com/watch?v=123",
            "https://youtube.com/user/channel",
            "https://youtube.com/about",
            None,
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(is_valid_youtube_url(url), f"Should be invalid: {url}")

    def test_sanitize_filename(self):
        # Illegal characters in Windows: \ / : * ? " < > |
        raw_name = 'Video: "Best Song" *EVER*? <Awesome> / 2026 | New\\Track...'
        sanitized = sanitize_filename(raw_name)
        for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            self.assertNotIn(char, sanitized)
        self.assertFalse(sanitized.endswith("."))


class TestHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_format_bytes(self):
        self.assertEqual(format_bytes(None), "size unknown")
        self.assertEqual(format_bytes(0), "size unknown")
        self.assertEqual(format_bytes(500), "500 B")
        self.assertEqual(format_bytes(1024 * 1024), "1.0 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 145), "145.0 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 2.5), "2.5 GB")

    def test_format_duration(self):
        self.assertEqual(format_duration(None), "--:--")
        self.assertEqual(format_duration(45), "00:45")
        self.assertEqual(format_duration(754), "12:34")
        self.assertEqual(format_duration(3665), "01:01:05")

    def test_check_ffmpeg_installed(self):
        # Should return boolean
        self.assertIsInstance(check_ffmpeg_installed(), bool)


class TestConfig(unittest.TestCase):
    """Test JSON persistence configuration."""

    def setUp(self):
        self.test_config = {
            "last_download_dir": str(Path.home()),
            "download_history": [],
        }

    def test_save_and_load_config(self):
        save_config(self.test_config)
        loaded = load_config()
        self.assertEqual(loaded.get("last_download_dir"), str(Path.home()))

    def test_set_and_get_last_dir(self):
        target = str(Path.home())
        set_last_download_dir(target)
        self.assertEqual(get_last_download_dir(), target)

    def test_add_history_entry(self):
        add_history_entry("Test Video", "/path/to/video.mp4", "10.5 MB", "1080p")
        loaded = load_config()
        self.assertTrue(len(loaded.get("download_history", [])) > 0)
        self.assertEqual(loaded["download_history"][0]["title"], "Test Video")


class TestExtractor(unittest.TestCase):
    """Test format option construction from mock metadata."""

    def test_build_format_options(self):
        mock_info = {
            "title": "Sample Mock Video",
            "duration": 180,
            "formats": [
                {
                    "format_id": "137",
                    "height": 1080,
                    "vcodec": "avc1.640028",
                    "acodec": "none",
                    "filesize": 50 * 1024 * 1024,
                },
                {
                    "format_id": "136",
                    "height": 720,
                    "vcodec": "avc1.4d401f",
                    "acodec": "none",
                    "filesize": 25 * 1024 * 1024,
                },
                {
                    "format_id": "140",
                    "height": None,
                    "vcodec": "none",
                    "acodec": "mp4a.40.2",
                    "filesize": 5 * 1024 * 1024,
                    "tbr": 128,
                },
            ],
        }

        options = build_format_options(mock_info)
        self.assertTrue(len(options) >= 3)

        # Video options
        video_opts = [o for o in options if o.get("type") == "video"]
        self.assertEqual(video_opts[0]["height"], 1080)
        self.assertEqual(video_opts[1]["height"], 720)

        # Audio option
        audio_opts = [o for o in options if o.get("type") == "audio"]
        self.assertEqual(len(audio_opts), 1)
        self.assertEqual(audio_opts[0]["ext"], "mp3")


if __name__ == "__main__":
    unittest.main()
