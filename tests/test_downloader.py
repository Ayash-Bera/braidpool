from pathlib import Path
from unittest.mock import patch, MagicMock
from eval.downloader import download_audio
from eval.video_list import VideoEntry

def make_entry(slug="test-slug", url="https://www.youtube.com/watch?v=test"):
    return VideoEntry(
        slug=slug,
        youtube_url=url,
        title="Test",
        speaker="Tester",
        conference="TestConf",
        year=2025,
        gt_slug=None,
    )

def test_download_audio_returns_path(tmp_path):
    entry = make_entry()
    with patch("eval.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl = MagicMock()
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
        audio_path = tmp_path / f"{entry.slug}.mp3"
        audio_path.touch()
        result = download_audio(entry, output_dir=tmp_path)
    assert result == audio_path

def test_download_audio_skips_if_exists(tmp_path):
    entry = make_entry()
    audio_path = tmp_path / f"{entry.slug}.mp3"
    audio_path.touch()
    with patch("eval.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        result = download_audio(entry, output_dir=tmp_path)
        mock_ydl_cls.assert_not_called()
    assert result == audio_path
