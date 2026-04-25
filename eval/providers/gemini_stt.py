from pathlib import Path
import google.generativeai as genai
from eval.providers import Provider

_PROMPT = (
    "Please transcribe the following audio file verbatim. "
    "Output only the transcript text, no commentary."
)

class GeminiProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="gemini-1.5-flash")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    def transcribe(self, audio_path: Path) -> str:
        audio_bytes = audio_path.read_bytes()
        audio_part = {"mime_type": "audio/mpeg", "data": audio_bytes}
        response = self._model.generate_content([_PROMPT, audio_part])
        return response.text.strip()
