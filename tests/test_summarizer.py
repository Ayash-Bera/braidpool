from unittest.mock import patch, MagicMock
from eval.summarizer import summarize

def test_summarize_calls_anthropic():
    transcript = "Bitcoin is a peer-to-peer electronic cash system. It uses cryptography."
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="Bitcoin: P2P cash using cryptography.")]
    with patch("eval.summarizer.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = mock_msg
        result = summarize(transcript, api_key="sk-ant-test")
    assert "Bitcoin" in result
    mock_client.messages.create.assert_called_once()
