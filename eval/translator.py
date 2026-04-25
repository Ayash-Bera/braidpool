import re
import requests

_ENDPOINT = "https://api.sarvam.ai/translate"
_CHUNK_SIZE = 900

def _chunk_text(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current = [], ''
    for s in sentences:
        if len(current) + len(s) < _CHUNK_SIZE:
            current += ' ' + s
        else:
            if current:
                chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks

def translate_to_hindi(text: str, api_key: str) -> str:
    chunks = _chunk_text(text)
    parts = []
    for chunk in chunks:
        resp = requests.post(
            _ENDPOINT,
            headers={"api-subscription-key": api_key},
            json={
                "input": chunk,
                "source_language_code": "en-IN",
                "target_language_code": "hi-IN",
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": True,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Sarvam translate error {resp.status_code}: {resp.text}")
        parts.append(resp.json().get("translated_text", ""))
    return " ".join(parts)
