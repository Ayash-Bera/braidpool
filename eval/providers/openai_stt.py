from pathlib import Path
import openai
from eval.providers import Provider

class OpenAIProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="openai-whisper-1")
        self._client = openai.OpenAI(api_key=api_key)

    def transcribe(self, audio_path: Path) -> str:
        with open(audio_path, "rb") as f:
            transcript = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )
        return transcript.text if hasattr(transcript, "text") else str(transcript)
