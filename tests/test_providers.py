from pathlib import Path
from eval.providers import Provider

class ConcreteProvider(Provider):
    def transcribe(self, audio_path: Path) -> str:
        return "hello"

def test_provider_interface():
    p = ConcreteProvider(name="test")
    assert p.transcribe(Path("any.mp3")) == "hello"
    assert p.name == "test"
