from pathlib import Path
from unittest.mock import patch
from eval.ground_truth import fetch_ground_truth
from eval.video_list import VideoEntry

def make_entry(gt_slug=None):
    return VideoEntry(
        slug="test", youtube_url="https://yt.be/x",
        title="T", speaker="S", conference="C", year=2025,
        gt_slug=gt_slug,
    )

def test_returns_none_when_no_gt_slug():
    entry = make_entry(gt_slug=None)
    assert fetch_ground_truth(entry, cache_dir=Path("/tmp")) is None

def test_returns_cached_text_without_network(tmp_path):
    entry = make_entry(gt_slug="bitcoin-2025/speaker/talk")
    cache_file = tmp_path / "talk.txt"
    cache_file.write_text("Hello world transcript")
    result = fetch_ground_truth(entry, cache_dir=tmp_path)
    assert result == "Hello world transcript"

def test_fetches_and_caches_on_miss(tmp_path):
    entry = make_entry(gt_slug="bitcoin-2025/speaker/talk")
    fake_md = "---\ntitle: Talk\n---\n\nThis is the transcript text."
    with patch("eval.ground_truth.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = fake_md
        result = fetch_ground_truth(entry, cache_dir=tmp_path)
    assert "This is the transcript text." in result
    assert (tmp_path / "talk.txt").exists()
