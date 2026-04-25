from dataclasses import dataclass
from typing import Optional
import jiwer

@dataclass
class MetricsResult:
    wer: Optional[float]
    cer: Optional[float]

def _normalize(text: str) -> str:
    return " ".join(text.lower().split())

def wer(reference: Optional[str], hypothesis: str) -> Optional[float]:
    if reference is None:
        return None
    return jiwer.wer(_normalize(reference), _normalize(hypothesis))

def cer(reference: Optional[str], hypothesis: str) -> Optional[float]:
    if reference is None:
        return None
    return jiwer.cer(_normalize(reference), _normalize(hypothesis))

def compute(reference: Optional[str], hypothesis: str) -> MetricsResult:
    return MetricsResult(
        wer=wer(reference, hypothesis),
        cer=cer(reference, hypothesis),
    )
