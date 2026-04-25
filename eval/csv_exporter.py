import csv
from pathlib import Path

COLUMNS = [
    "video_slug",
    "title",
    "speaker",
    "conference",
    "year",
    "provider",
    "raw_transcript",
    "corrected_transcript",
    "summary",
    "wer",
    "cer",
    "audio_duration_seconds",
]

def export_results(rows: list[dict], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
