from pathlib import Path
from unittest.mock import patch, MagicMock
from eval.evaluator import evaluate_video
from eval.video_list import VideoEntry

def make_entry():
    return VideoEntry(
        slug="test-talk", youtube_url="https://yt.be/x",
        title="Test", speaker="Bob", conference="C", year=2025, gt_slug=None,
    )

def test_evaluate_video_returns_rows_per_provider(tmp_path):
    entry = make_entry()
    audio = tmp_path / "test-talk.mp3"
    audio.write_bytes(b"fake")
    fake_provider = MagicMock()
    fake_provider.name = "test-provider"
    fake_provider.transcribe.return_value = "raw text here"
    with patch("eval.evaluator.download_audio", return_value=audio), \
         patch("eval.evaluator.fetch_ground_truth", return_value=None), \
         patch("eval.evaluator.correct_transcript", return_value="corrected text"), \
         patch("eval.evaluator.summarize", return_value="summary text"):
        rows = evaluate_video(
            entry,
            providers=[fake_provider],
            anthropic_api_key="sk-ant-test",
            audio_dir=tmp_path,
            gt_cache_dir=tmp_path,
        )
    assert len(rows) == 1
    assert rows[0]["provider"] == "test-provider"
    assert rows[0]["raw_transcript"] == "raw text here"
    assert rows[0]["corrected_transcript"] == "corrected text"
    assert rows[0]["wer"] is None  # no ground truth
