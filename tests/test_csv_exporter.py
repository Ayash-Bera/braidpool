import csv
from pathlib import Path
from eval.csv_exporter import export_results, COLUMNS

def test_export_creates_csv(tmp_path):
    rows = [
        {
            "video_slug": "test-talk",
            "title": "Test Talk",
            "speaker": "Alice",
            "conference": "TestConf",
            "year": 2025,
            "provider": "openai-whisper-1",
            "raw_transcript": "bitcon is grate",
            "corrected_transcript": "Bitcoin is great",
            "summary": "Bitcoin is great.",
            "wer": 0.33,
            "cer": 0.12,
            "audio_duration_seconds": 3600,
        }
    ]
    out = tmp_path / "results.csv"
    export_results(rows, out)
    assert out.exists()
    with open(out) as f:
        reader = csv.DictReader(f)
        data = list(reader)
    assert len(data) == 1
    assert data[0]["video_slug"] == "test-talk"
    assert data[0]["provider"] == "openai-whisper-1"

def test_export_uses_correct_columns(tmp_path):
    out = tmp_path / "results.csv"
    export_results([], out)
    with open(out) as f:
        header = f.readline().strip().split(",")
    assert header == COLUMNS
