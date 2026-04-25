from unittest.mock import patch, MagicMock
from eval.correction import correct_transcript

def test_correct_transcript_calls_anthropic():
    raw = "bitcon is dig ital gol d"
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="Bitcoin is digital gold")]
    with patch("eval.correction.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_msg
        result = correct_transcript(raw, api_key="sk-ant-test")
    assert result == "Bitcoin is digital gold"
    mock_client.messages.create.assert_called_once()
