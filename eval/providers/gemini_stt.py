import time
from pathlib import Path
import google.generativeai as genai
from eval.providers import Provider

_PROMPT = (
    "Please transcribe the following audio file verbatim. "
    "Output only the transcript text, no commentary."
)
_MAX_RETRIES = 5

class GeminiProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="gemini-2.0-flash-lite")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def transcribe(self, audio_path: Path) -> str:
        audio_bytes = audio_path.read_bytes()
        audio_part = {"mime_type": "audio/mpeg", "data": audio_bytes}
        delay = 10
        for attempt in range(_MAX_RETRIES):
            try:
                response = self._model.generate_content([_PROMPT, audio_part])
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) and attempt < _MAX_RETRIES - 1:
                    print(f"    [gemini-2.0-flash] rate limited, waiting {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise
