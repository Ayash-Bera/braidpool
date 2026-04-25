from pathlib import Path
import requests
from eval.providers import Provider

_ENDPOINT = "https://api.sarvam.ai/speech-to-text"

class SarvamProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="sarvam-stt-v2.5")
        self._api_key = api_key

    def transcribe(self, audio_path: Path) -> str:
        with open(audio_path, "rb") as f:
            resp = requests.post(
                _ENDPOINT,
                headers={"api-subscription-key": self._api_key},
                files={"file": (audio_path.name, f, "audio/mpeg")},
                data={"language_code": "en-IN", "model": "saarika:v2.5"},
                timeout=120,
            )
        if resp.status_code != 200:
            raise RuntimeError(f"Sarvam API error {resp.status_code}: {resp.text}")
        return resp.json().get("transcript", "")
