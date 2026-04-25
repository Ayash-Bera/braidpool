from pathlib import Path
from eval.providers import Provider
from unittest.mock import patch, MagicMock
from eval.providers.openai_stt import OpenAIProvider

class ConcreteProvider(Provider):
    def transcribe(self, audio_path: Path) -> str:
        return "hello"

def test_provider_interface():
    p = ConcreteProvider(name="test")
    assert p.transcribe(Path("any.mp3")) == "hello"
    assert p.name == "test"

def test_openai_provider_calls_whisper(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake audio")
    mock_transcript = MagicMock()
    mock_transcript.text = "bitcoin is digital gold"
    with patch("eval.providers.openai_stt.openai.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = mock_transcript
        p = OpenAIProvider(api_key="sk-test")
        result = p.transcribe(audio)
    assert result == "bitcoin is digital gold"
    mock_client.audio.transcriptions.create.assert_called_once()
    _, kwargs = mock_client.audio.transcriptions.create.call_args
    assert kwargs["model"] == "whisper-1"
