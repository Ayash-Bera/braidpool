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

from unittest.mock import patch, MagicMock
from eval.providers.gemini_stt import GeminiProvider

def test_gemini_provider_transcribes(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake audio")
    mock_response = MagicMock()
    mock_response.text = "satoshi invented bitcoin"
    with patch("eval.providers.gemini_stt.genai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_model.generate_content.return_value = mock_response
        p = GeminiProvider(api_key="fake-key")
        result = p.transcribe(audio)
    assert result == "satoshi invented bitcoin"

from eval.providers.sarvam_stt import SarvamProvider

def test_sarvam_provider_transcribes(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake audio")
    fake_response = {"transcript": "hodl your bitcoin"}
    with patch("eval.providers.sarvam_stt.requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = fake_response
        p = SarvamProvider(api_key="fake-key")
        result = p.transcribe(audio)
    assert result == "hodl your bitcoin"

def test_sarvam_raises_on_api_error(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake audio")
    with patch("eval.providers.sarvam_stt.requests.post") as mock_post:
        mock_post.return_value.status_code = 401
        mock_post.return_value.text = "Unauthorized"
        p = SarvamProvider(api_key="bad-key")
        try:
            p.transcribe(audio)
            assert False, "should have raised"
        except RuntimeError as e:
            assert "401" in str(e)

from unittest.mock import patch, MagicMock
from eval.providers.genesis_kb import GenesisPipelineProvider

def test_genesis_pipeline_provider_returns_string(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake")
    with patch("eval.providers.genesis_kb.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="transcript output\n")
        p = GenesisPipelineProvider(pipeline_dir=str(tmp_path))
        # The provider reads a .txt file — create one so glob finds it
        txt_file = tmp_path / "out.txt"
        txt_file.write_text("transcript output")
        with patch("eval.providers.genesis_kb.glob.glob", return_value=[str(txt_file)]):
            result = p.transcribe(audio)
    assert isinstance(result, str)
    assert result == "transcript output"
