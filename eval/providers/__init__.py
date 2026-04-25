from abc import ABC, abstractmethod
from pathlib import Path

class Provider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        ...
