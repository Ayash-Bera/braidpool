import subprocess
import tempfile
import time
from pathlib import Path
import requests
from eval.providers import Provider

_ENDPOINT = "https://api.sarvam.ai/speech-to-text"
_CHUNK_SECONDS = 25  # Sarvam limit is 30s; use 25s for safety

def _get_duration(audio_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
        capture_output=True, text=True, timeout=30,
    )
    return float(result.stdout.strip())

def _split_audio(audio_path: Path, chunk_seconds: int, tmp_dir: str) -> list[Path]:
    duration = _get_duration(audio_path)
    chunks = []
    start = 0.0
    idx = 0
    while start < duration:
        out = Path(tmp_dir) / f"chunk_{idx:04d}.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(start), "-t", str(chunk_seconds),
             "-i", str(audio_path), "-acodec", "libmp3lame", "-q:a", "4", str(out)],
            capture_output=True, timeout=60,
        )
        if out.exists() and out.stat().st_size > 0:
            chunks.append(out)
        start += chunk_seconds
        idx += 1
    return chunks

class SarvamProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="sarvam-stt-v2.5")
        self._api_key = api_key

    def _transcribe_chunk(self, chunk_path: Path) -> str:
        with open(chunk_path, "rb") as f:
            resp = requests.post(
                _ENDPOINT,
                headers={"api-subscription-key": self._api_key},
                files={"file": (chunk_path.name, f, "audio/mpeg")},
                data={"language_code": "en-IN", "model": "saarika:v2.5"},
                timeout=120,
            )
        if resp.status_code != 200:
            raise RuntimeError(f"Sarvam API error {resp.status_code}: {resp.text}")
        return resp.json().get("transcript", "")

    def transcribe(self, audio_path: Path) -> str:
        with tempfile.TemporaryDirectory() as tmp_dir:
            chunks = _split_audio(audio_path, _CHUNK_SECONDS, tmp_dir)
            parts = []
            for chunk in chunks:
                parts.append(self._transcribe_chunk(chunk))
                time.sleep(0.5)  # avoid rate limiting
        return " ".join(parts)
