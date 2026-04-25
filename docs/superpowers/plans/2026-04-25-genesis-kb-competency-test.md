# Genesis KB Competency Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the genesis-kb transcription pipeline on 10 Bitcoin 2025 conference videos, benchmark three STT providers (OpenAI, Gemini, Sarvam) using WER/CER against ground-truth transcripts, then export all raw transcripts, corrections, summaries, and metrics to a CSV for the proposal.

**Architecture:** Clone the upstream `transcription_engine`, wrap each STT provider behind a uniform interface, download audio from YouTube using yt-dlp, fetch ground-truth transcripts from `bitcointranscripts`, compute WER/CER via `jiwer`, run correction and summarization through an LLM, then write everything to a single `results.csv`. All provider wrappers share one interface so evaluation logic is provider-agnostic.

**Tech Stack:** Python 3.11+, yt-dlp, ffmpeg, jiwer, openai SDK, google-generativeai SDK, requests (Sarvam REST), anthropic SDK (correction/summarization), pandas, python-dotenv, pytest

---

## Scope Note

This plan covers only the competency test. The full Genesis KB project has three additional subsystems (conference discovery pipeline, multilingual support, enhanced correction/summarization) — each should be a separate plan once this submission is done.

---

## File Map

| File | Responsibility |
|------|---------------|
| `eval/video_list.py` | Hard-coded list of 10 videos (YouTube URL + expected bitcointranscripts slug) |
| `eval/downloader.py` | Download audio to `data/audio/<slug>.mp3` using yt-dlp |
| `eval/ground_truth.py` | Fetch/cache ground-truth text from bitcointranscripts repo |
| `eval/providers/__init__.py` | `Provider` base class with uniform `transcribe(audio_path) -> str` interface |
| `eval/providers/openai_stt.py` | OpenAI Whisper-1 provider |
| `eval/providers/gemini_stt.py` | Gemini 1.5 Flash audio provider |
| `eval/providers/sarvam_stt.py` | Sarvam AI REST provider |
| `eval/metrics.py` | `wer()` and `cer()` using jiwer |
| `eval/correction.py` | LLM-based transcript correction (Claude claude-sonnet-4-6) |
| `eval/summarizer.py` | LLM-based summarization (Claude claude-sonnet-4-6) |
| `eval/evaluator.py` | Orchestrate: download → transcribe → correct → summarize → measure |
| `eval/csv_exporter.py` | Write `results/results.csv` from a list of result dicts |
| `eval/run_eval.py` | CLI entry point (`python -m eval.run_eval`) |
| `tests/test_metrics.py` | Unit tests for WER/CER |
| `tests/test_providers.py` | Unit tests for provider interface (mocked API calls) |
| `tests/test_csv_exporter.py` | Unit tests for CSV export |
| `.env.example` | Template for required API keys |
| `requirements.txt` | Pinned dependencies |
| `data/audio/` | Downloaded audio files (gitignored) |
| `data/ground_truth/` | Cached ground-truth text files (gitignored) |
| `results/results.csv` | Final output (committed) |

---

## Task 1: Repo Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `eval/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
yt-dlp==2024.12.13
ffmpeg-python==0.2.0
jiwer==3.0.4
openai==1.54.3
google-generativeai==0.8.3
anthropic==0.39.0
requests==2.32.3
pandas==2.2.3
python-dotenv==1.0.1
pytest==8.3.3
pytest-mock==3.14.0
```

- [ ] **Step 2: Create .env.example**

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
SARVAM_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: all packages install without error. If ffmpeg missing: `sudo apt-get install ffmpeg` (Ubuntu) or `brew install ffmpeg` (macOS).

- [ ] **Step 4: Create empty init files**

```bash
mkdir -p eval/providers tests data/audio data/ground_truth results
touch eval/__init__.py eval/providers/__init__.py tests/__init__.py
```

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt .env.example eval/ tests/ data/.gitkeep results/.gitkeep
git commit -m "chore: bootstrap eval project structure"
```

---

## Task 2: Video List

**Files:**
- Create: `eval/video_list.py`

The 10 videos are chosen from Bitcoin 2025 and Baltic Honeybadger 2025. The `gt_slug` field is the path under `https://raw.githubusercontent.com/bitcointranscripts/bitcointranscripts/master/` — leave `None` if ground truth doesn't exist yet (evaluator will skip WER/CER for that row).

- [ ] **Step 1: Write the video list**

```python
# eval/video_list.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class VideoEntry:
    slug: str
    youtube_url: str
    title: str
    speaker: str
    conference: str
    year: int
    gt_slug: Optional[str]  # path in bitcointranscripts repo, or None

VIDEOS: list[VideoEntry] = [
    VideoEntry(
        slug="bitcoin-2025-adam-back-keynote",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE with real URL
        title="Opening Keynote",
        speaker="Adam Back",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-michael-saylor-strategy",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Bitcoin Treasury Strategy",
        speaker="Michael Saylor",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-lightning-panel",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Lightning Network State of the Union",
        speaker="Various",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-block-scaling",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Block Size and Scaling Debate",
        speaker="Various",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-privacy-coinjoin",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Privacy on Bitcoin: CoinJoin and Beyond",
        speaker="Various",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-peter-todd-covenants",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Covenants Without Soft Forks",
        speaker="Peter Todd",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-calle-cashu",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Cashu: Chaumian Ecash on Bitcoin",
        speaker="calle",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-fedimint",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Fedimint Update",
        speaker="Various",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-mempool-policy",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Mempool Policy and Fee Markets",
        speaker="Various",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-self-custody",
        youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # REPLACE
        title="Self-Custody in 2025",
        speaker="Various",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
]
```

> **Action required:** Replace all placeholder `youtube_url` values with real URLs from the Bitcoin 2025 conference YouTube channel (`@BitcoinMagazine`) and Baltic Honeybadger 2025 channel before running. Search YouTube for the speaker name + conference name.

- [ ] **Step 2: Verify import**

```bash
python -c "from eval.video_list import VIDEOS; print(len(VIDEOS))"
```

Expected: `10`

- [ ] **Step 3: Commit**

```bash
git add eval/video_list.py
git commit -m "feat: add 10-video evaluation list"
```

---

## Task 3: Audio Downloader

**Files:**
- Create: `eval/downloader.py`
- Create: `tests/test_downloader.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_downloader.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from eval.downloader import download_audio
from eval.video_list import VideoEntry

def make_entry(slug="test-slug", url="https://www.youtube.com/watch?v=test"):
    return VideoEntry(
        slug=slug,
        youtube_url=url,
        title="Test",
        speaker="Tester",
        conference="TestConf",
        year=2025,
        gt_slug=None,
    )

def test_download_audio_returns_path(tmp_path):
    entry = make_entry()
    with patch("eval.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl = MagicMock()
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl
        audio_path = tmp_path / f"{entry.slug}.mp3"
        audio_path.touch()
        result = download_audio(entry, output_dir=tmp_path)
    assert result == audio_path

def test_download_audio_skips_if_exists(tmp_path):
    entry = make_entry()
    audio_path = tmp_path / f"{entry.slug}.mp3"
    audio_path.touch()
    with patch("eval.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        result = download_audio(entry, output_dir=tmp_path)
        mock_ydl_cls.assert_not_called()
    assert result == audio_path
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_downloader.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `eval.downloader` does not exist yet.

- [ ] **Step 3: Implement downloader**

```python
# eval/downloader.py
from pathlib import Path
import yt_dlp

def download_audio(entry, output_dir: Path = Path("data/audio")) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f"{entry.slug}.mp3"
    if dest.exists():
        return dest
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / f"{entry.slug}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([entry.youtube_url])
    return dest
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_downloader.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/downloader.py tests/test_downloader.py
git commit -m "feat: add yt-dlp audio downloader"
```

---

## Task 4: Ground Truth Fetcher

**Files:**
- Create: `eval/ground_truth.py`
- Create: `tests/test_ground_truth.py`

Ground truth comes from the `bitcointranscripts` GitHub repo. For 2025 videos not yet in the repo, `gt_slug=None` and this function returns `None`.

- [ ] **Step 1: Write failing tests**

```python
# tests/test_ground_truth.py
from pathlib import Path
from unittest.mock import patch
from eval.ground_truth import fetch_ground_truth
from eval.video_list import VideoEntry

def make_entry(gt_slug=None):
    return VideoEntry(
        slug="test", youtube_url="https://yt.be/x",
        title="T", speaker="S", conference="C", year=2025,
        gt_slug=gt_slug,
    )

def test_returns_none_when_no_gt_slug():
    entry = make_entry(gt_slug=None)
    assert fetch_ground_truth(entry, cache_dir=Path("/tmp")) is None

def test_returns_cached_text_without_network(tmp_path):
    entry = make_entry(gt_slug="bitcoin-2025/speaker/talk")
    cache_file = tmp_path / "talk.txt"
    cache_file.write_text("Hello world transcript")
    result = fetch_ground_truth(entry, cache_dir=tmp_path)
    assert result == "Hello world transcript"

def test_fetches_and_caches_on_miss(tmp_path):
    entry = make_entry(gt_slug="bitcoin-2025/speaker/talk")
    fake_md = "---\ntitle: Talk\n---\n\nThis is the transcript text."
    with patch("eval.ground_truth.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = fake_md
        result = fetch_ground_truth(entry, cache_dir=tmp_path)
    assert "This is the transcript text." in result
    assert (tmp_path / "talk.txt").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_ground_truth.py -v
```

Expected: `ImportError` — `eval.ground_truth` not found.

- [ ] **Step 3: Implement ground truth fetcher**

```python
# eval/ground_truth.py
import re
import requests
from pathlib import Path

_BASE = "https://raw.githubusercontent.com/bitcointranscripts/bitcointranscripts/master"

def _strip_frontmatter(text: str) -> str:
    # Remove YAML frontmatter block if present
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    return text.strip()

def fetch_ground_truth(entry, cache_dir: Path = Path("data/ground_truth")) -> str | None:
    if entry.gt_slug is None:
        return None
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    slug_name = entry.gt_slug.rstrip("/").split("/")[-1]
    cache_file = cache_dir / f"{slug_name}.txt"
    if cache_file.exists():
        return cache_file.read_text()
    url = f"{_BASE}/{entry.gt_slug}.md"
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        return None
    text = _strip_frontmatter(resp.text)
    cache_file.write_text(text)
    return text
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_ground_truth.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/ground_truth.py tests/test_ground_truth.py
git commit -m "feat: add bitcointranscripts ground truth fetcher"
```

---

## Task 5: Provider Base Class

**Files:**
- Modify: `eval/providers/__init__.py`
- Create: `tests/test_providers.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_providers.py
from pathlib import Path
from eval.providers import Provider

class ConcreteProvider(Provider):
    def transcribe(self, audio_path: Path) -> str:
        return "hello"

def test_provider_interface():
    p = ConcreteProvider(name="test")
    assert p.transcribe(Path("any.mp3")) == "hello"
    assert p.name == "test"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement base class**

```python
# eval/providers/__init__.py
from abc import ABC, abstractmethod
from pathlib import Path

class Provider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        ...
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_providers.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/providers/__init__.py tests/test_providers.py
git commit -m "feat: add Provider base class"
```

---

## Task 6: OpenAI Whisper Provider

**Files:**
- Create: `eval/providers/openai_stt.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_providers.py`:

```python
from unittest.mock import patch, MagicMock
from eval.providers.openai_stt import OpenAIProvider

def test_openai_provider_calls_whisper(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake audio")
    mock_transcript = MagicMock()
    mock_transcript.text = "bitcoin is digital gold"
    with patch("eval.providers.openai_stt.openai.audio.transcriptions.create",
               return_value=mock_transcript) as mock_create:
        p = OpenAIProvider(api_key="sk-test")
        result = p.transcribe(audio)
    assert result == "bitcoin is digital gold"
    mock_create.assert_called_once()
    _, kwargs = mock_create.call_args
    assert kwargs["model"] == "whisper-1"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers.py::test_openai_provider_calls_whisper -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement OpenAI provider**

```python
# eval/providers/openai_stt.py
from pathlib import Path
import openai
from eval.providers import Provider

class OpenAIProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="openai-whisper-1")
        self._client = openai.OpenAI(api_key=api_key)

    def transcribe(self, audio_path: Path) -> str:
        with open(audio_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
            )
        return transcript.text if hasattr(transcript, "text") else str(transcript)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_providers.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/providers/openai_stt.py tests/test_providers.py
git commit -m "feat: add OpenAI Whisper provider"
```

---

## Task 7: Gemini STT Provider

**Files:**
- Create: `eval/providers/gemini_stt.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_providers.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers.py::test_gemini_provider_transcribes -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement Gemini provider**

```python
# eval/providers/gemini_stt.py
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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_providers.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/providers/gemini_stt.py tests/test_providers.py
git commit -m "feat: add Gemini 1.5 Flash STT provider"
```

---

## Task 8: Sarvam STT Provider

**Files:**
- Create: `eval/providers/sarvam_stt.py`

Sarvam AI exposes a REST endpoint at `https://api.sarvam.ai/speech-to-text`. Docs: https://docs.sarvam.ai/api-reference-docs/speech-to-text

- [ ] **Step 1: Write failing test**

Add to `tests/test_providers.py`:

```python
from unittest.mock import patch
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_providers.py::test_sarvam_provider_transcribes tests/test_providers.py::test_sarvam_raises_on_api_error -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement Sarvam provider**

```python
# eval/providers/sarvam_stt.py
from pathlib import Path
import requests
from eval.providers import Provider

_ENDPOINT = "https://api.sarvam.ai/speech-to-text"

class SarvamProvider(Provider):
    def __init__(self, api_key: str):
        super().__init__(name="sarvam-stt-v1")
        self._api_key = api_key

    def transcribe(self, audio_path: Path) -> str:
        with open(audio_path, "rb") as f:
            resp = requests.post(
                _ENDPOINT,
                headers={"api-subscription-key": self._api_key},
                files={"file": (audio_path.name, f, "audio/mpeg")},
                data={"language_code": "en-IN", "model": "saarika:v1"},
                timeout=120,
            )
        if resp.status_code != 200:
            raise RuntimeError(f"Sarvam API error {resp.status_code}: {resp.text}")
        return resp.json().get("transcript", "")
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_providers.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/providers/sarvam_stt.py tests/test_providers.py
git commit -m "feat: add Sarvam AI STT provider"
```

---

## Task 9: WER/CER Metrics

**Files:**
- Create: `eval/metrics.py`
- Create: `tests/test_metrics.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_metrics.py
from eval.metrics import wer, cer, MetricsResult

def test_perfect_match():
    result = wer("hello world", "hello world")
    assert result == 0.0

def test_one_word_wrong():
    result = wer("hello world", "hello bitcoin")
    assert 0.0 < result <= 0.5

def test_cer_char_level():
    result = cer("abc", "axc")
    assert 0.0 < result <= 0.5

def test_returns_none_when_reference_is_none():
    result = wer(None, "anything")
    assert result is None

def test_metrics_result_dataclass():
    m = MetricsResult(wer=0.1, cer=0.05)
    assert m.wer == 0.1
    assert m.cer == 0.05
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_metrics.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement metrics**

```python
# eval/metrics.py
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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_metrics.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/metrics.py tests/test_metrics.py
git commit -m "feat: add WER/CER metrics with jiwer"
```

---

## Task 10: Correction Module

**Files:**
- Create: `eval/correction.py`

Uses Claude claude-sonnet-4-6 to fix STT errors: hallucinations, bitcoin-specific terminology, run-on sentences.

- [ ] **Step 1: Write failing test**

```python
# add to tests/ as tests/test_correction.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_correction.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement correction**

```python
# eval/correction.py
import anthropic

_SYSTEM = """You are a Bitcoin transcript editor. Fix speech-to-text errors in the provided transcript:
- Correct Bitcoin-specific terminology (SegWit, Lightning Network, UTXO, HODL, Taproot, etc.)
- Fix run-on sentences and punctuation
- Do not change meaning or add commentary
- Output only the corrected transcript"""

def correct_transcript(raw_text: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=_SYSTEM,
        messages=[{"role": "user", "content": raw_text}],
    )
    return msg.content[0].text
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_correction.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/correction.py tests/test_correction.py
git commit -m "feat: add LLM transcript correction"
```

---

## Task 11: Summarizer Module

**Files:**
- Create: `eval/summarizer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_summarizer.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_summarizer.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement summarizer**

```python
# eval/summarizer.py
import anthropic

_SYSTEM = """You are a Bitcoin conference talk summarizer. Given a talk transcript, produce:
1. A 2-3 sentence abstract
2. 3-5 key points as bullet points
3. Any notable technical claims or proposals

Output plain text. Be concise and accurate."""

def summarize(transcript: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": transcript}],
    )
    return msg.content[0].text
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_summarizer.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/summarizer.py tests/test_summarizer.py
git commit -m "feat: add LLM summarizer"
```

---

## Task 12: CSV Exporter

**Files:**
- Create: `eval/csv_exporter.py`
- Create: `tests/test_csv_exporter.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_csv_exporter.py
import csv
from pathlib import Path
from eval.csv_exporter import export_results, COLUMNS

def test_export_creates_csv(tmp_path):
    rows = [
        {
            "video_slug": "test-talk",
            "title": "Test Talk",
            "speaker": "Alice",
            "conference": "TestConf",
            "year": 2025,
            "provider": "openai-whisper-1",
            "raw_transcript": "bitcon is grate",
            "corrected_transcript": "Bitcoin is great",
            "summary": "Bitcoin is great.",
            "wer": 0.33,
            "cer": 0.12,
            "audio_duration_seconds": 3600,
        }
    ]
    out = tmp_path / "results.csv"
    export_results(rows, out)
    assert out.exists()
    with open(out) as f:
        reader = csv.DictReader(f)
        data = list(reader)
    assert len(data) == 1
    assert data[0]["video_slug"] == "test-talk"
    assert data[0]["provider"] == "openai-whisper-1"

def test_export_uses_correct_columns(tmp_path):
    out = tmp_path / "results.csv"
    export_results([], out)
    with open(out) as f:
        header = f.readline().strip().split(",")
    assert header == COLUMNS
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_csv_exporter.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement CSV exporter**

```python
# eval/csv_exporter.py
import csv
from pathlib import Path

COLUMNS = [
    "video_slug",
    "title",
    "speaker",
    "conference",
    "year",
    "provider",
    "raw_transcript",
    "corrected_transcript",
    "summary",
    "wer",
    "cer",
    "audio_duration_seconds",
]

def export_results(rows: list[dict], output_path: Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_csv_exporter.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/csv_exporter.py tests/test_csv_exporter.py
git commit -m "feat: add CSV exporter"
```

---

## Task 13: Evaluator Orchestrator

**Files:**
- Create: `eval/evaluator.py`

This ties together: download → ground truth → transcribe (all providers) → correct → summarize → measure.

- [ ] **Step 1: Write failing test**

```python
# tests/test_evaluator.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from eval.evaluator import evaluate_video
from eval.video_list import VideoEntry

def make_entry():
    return VideoEntry(
        slug="test-talk", youtube_url="https://yt.be/x",
        title="Test", speaker="Bob", conference="C", year=2025, gt_slug=None,
    )

def test_evaluate_video_returns_rows_per_provider(tmp_path):
    entry = make_entry()
    audio = tmp_path / "test-talk.mp3"
    audio.write_bytes(b"fake")
    fake_provider = MagicMock()
    fake_provider.name = "test-provider"
    fake_provider.transcribe.return_value = "raw text here"
    with patch("eval.evaluator.download_audio", return_value=audio), \
         patch("eval.evaluator.fetch_ground_truth", return_value=None), \
         patch("eval.evaluator.correct_transcript", return_value="corrected text"), \
         patch("eval.evaluator.summarize", return_value="summary text"):
        rows = evaluate_video(
            entry,
            providers=[fake_provider],
            anthropic_api_key="sk-ant-test",
            audio_dir=tmp_path,
            gt_cache_dir=tmp_path,
        )
    assert len(rows) == 1
    assert rows[0]["provider"] == "test-provider"
    assert rows[0]["raw_transcript"] == "raw text here"
    assert rows[0]["corrected_transcript"] == "corrected text"
    assert rows[0]["wer"] is None  # no ground truth
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_evaluator.py -v
```

Expected: `ImportError`.

- [ ] **Step 3: Implement evaluator**

```python
# eval/evaluator.py
from pathlib import Path
from eval.downloader import download_audio
from eval.ground_truth import fetch_ground_truth
from eval.correction import correct_transcript
from eval.summarizer import summarize
from eval import metrics as m

def evaluate_video(
    entry,
    providers: list,
    anthropic_api_key: str,
    audio_dir: Path = Path("data/audio"),
    gt_cache_dir: Path = Path("data/ground_truth"),
) -> list[dict]:
    audio_path = download_audio(entry, output_dir=audio_dir)
    ground_truth = fetch_ground_truth(entry, cache_dir=gt_cache_dir)
    results = []
    for provider in providers:
        raw = provider.transcribe(audio_path)
        corrected = correct_transcript(raw, api_key=anthropic_api_key)
        summary = summarize(corrected, api_key=anthropic_api_key)
        metric = m.compute(ground_truth, raw)
        results.append({
            "video_slug": entry.slug,
            "title": entry.title,
            "speaker": entry.speaker,
            "conference": entry.conference,
            "year": entry.year,
            "provider": provider.name,
            "raw_transcript": raw,
            "corrected_transcript": corrected,
            "summary": summary,
            "wer": metric.wer,
            "cer": metric.cer,
            "audio_duration_seconds": None,
        })
    return results
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_evaluator.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add eval/evaluator.py tests/test_evaluator.py
git commit -m "feat: add evaluation orchestrator"
```

---

## Task 14: CLI Entry Point

**Files:**
- Create: `eval/run_eval.py`

- [ ] **Step 1: Write the CLI script**

```python
# eval/run_eval.py
import os
from pathlib import Path
from dotenv import load_dotenv
from eval.video_list import VIDEOS
from eval.providers.openai_stt import OpenAIProvider
from eval.providers.gemini_stt import GeminiProvider
from eval.providers.sarvam_stt import SarvamProvider
from eval.evaluator import evaluate_video
from eval.csv_exporter import export_results

load_dotenv()

def main():
    providers = [
        OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"]),
        GeminiProvider(api_key=os.environ["GEMINI_API_KEY"]),
        SarvamProvider(api_key=os.environ["SARVAM_API_KEY"]),
    ]
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    all_rows = []
    for i, entry in enumerate(VIDEOS, 1):
        print(f"[{i}/{len(VIDEOS)}] {entry.slug}")
        rows = evaluate_video(
            entry,
            providers=providers,
            anthropic_api_key=anthropic_key,
        )
        all_rows.extend(rows)
        print(f"  done — {len(rows)} rows")
    out = Path("results/results.csv")
    export_results(all_rows, out)
    print(f"\nWrote {len(all_rows)} rows to {out}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create .env from template**

```bash
cp .env.example .env
# Then fill in real API keys in .env
```

- [ ] **Step 3: Run full test suite**

```bash
pytest -v
```

Expected: all tests PASS.

- [ ] **Step 4: Dry-run with one video**

Edit `eval/run_eval.py` temporarily to slice `VIDEOS[:1]` to test one video end-to-end before full run. Verify `.mp3` downloads to `data/audio/`, CSV writes to `results/results.csv`.

```bash
python -m eval.run_eval
```

Expected: `data/audio/<slug>.mp3` created, `results/results.csv` with 3 rows (one per provider).

- [ ] **Step 5: Restore full video list and run complete eval**

Remove the `[:1]` slice. Run:

```bash
python -m eval.run_eval
```

Expected: 30 rows in CSV (10 videos × 3 providers). Check no errors. Check WER/CER columns populate where ground truth exists, `None` where it doesn't.

- [ ] **Step 6: Commit final results**

```bash
git add eval/run_eval.py results/results.csv
git commit -m "feat: add CLI entry point and include eval results CSV"
```

---

## Task 15: Full Test Run and Validation

- [ ] **Step 1: Run full test suite one final time**

```bash
pytest -v --tb=short
```

Expected: all tests PASS, 0 failures.

- [ ] **Step 2: Validate CSV schema**

```bash
python -c "
import csv
from eval.csv_exporter import COLUMNS
with open('results/results.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
print(f'Rows: {len(rows)}')
print(f'Columns match: {reader.fieldnames == COLUMNS}')
# print WER/CER summary
import statistics
wers = [float(r['wer']) for r in rows if r['wer'] not in ('', 'None')]
if wers:
    print(f'WER mean={statistics.mean(wers):.3f} min={min(wers):.3f} max={max(wers):.3f}')
else:
    print('No WER data (no ground truth available)')
"
```

Expected: 30 rows, columns match, WER stats print (or note explaining no ground truth).

- [ ] **Step 3: Upload CSV to Google Sheets or GitHub Gist**

Upload `results/results.csv` to a publicly accessible location. Copy the URL — this goes directly in the proposal.

```bash
# Option A: GitHub Gist
gh gist create results/results.csv --public --desc "Genesis KB Competency Test Results"

# Option B: commit to a public fork of transcription_engine or your own repo
```

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete competency test evaluation pipeline"
```

---

## Self-Review

### Spec coverage

| Requirement | Covered by |
|------------|-----------|
| Set up transcription pipeline | Task 1 (deps install) + Tasks 3–8 (pipeline components) |
| Run on 10 Bitcoin 2025 videos | Task 2 (video list) + Task 14 (CLI run) |
| Benchmark OpenAI, Gemini, Sarvam | Tasks 6, 7, 8 |
| WER, CER metrics | Task 9 |
| Correction step | Task 10 |
| Summarization step | Task 11 |
| CSV with metadata + metrics | Tasks 12, 14 |
| Shareable CSV link | Task 15 Step 3 |

**Gap:** The spec says to use the `genesis-kb/transcription_engine` existing pipeline, not just build a new one. This plan wraps three external providers for benchmarking — the genesis-kb pipeline itself should also be one of the providers compared. **Add Task 16 below.**

---

## Task 16: Genesis KB Pipeline Provider Wrapper

**Files:**
- Create: `eval/providers/genesis_kb.py`

This wraps the upstream pipeline so it competes in the same benchmark.

- [ ] **Step 1: Clone the upstream repo**

```bash
git clone https://github.com/genesis-kb/transcription_engine.git vendor/transcription_engine
```

- [ ] **Step 2: Install its dependencies**

```bash
pip install -r vendor/transcription_engine/requirements.txt
```

- [ ] **Step 3: Write failing test**

Add to `tests/test_providers.py`:

```python
from unittest.mock import patch, MagicMock
from eval.providers.genesis_kb import GenesisPipelineProvider

def test_genesis_pipeline_provider_returns_string(tmp_path):
    audio = tmp_path / "test.mp3"
    audio.write_bytes(b"fake")
    with patch("eval.providers.genesis_kb.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="transcript output")
        p = GenesisPipelineProvider(pipeline_dir="vendor/transcription_engine")
        result = p.transcribe(audio)
    assert isinstance(result, str)
```

- [ ] **Step 4: Run test to verify it fails**

```bash
pytest tests/test_providers.py::test_genesis_pipeline_provider_returns_string -v
```

Expected: `ImportError`.

- [ ] **Step 5: Inspect genesis-kb pipeline entrypoint**

```bash
ls vendor/transcription_engine/
cat vendor/transcription_engine/README.md | head -60
```

Note the CLI command to run transcription (typically `python main.py` or similar). Update the implementation below to match.

- [ ] **Step 6: Implement wrapper**

```python
# eval/providers/genesis_kb.py
import subprocess
from pathlib import Path
from eval.providers import Provider

class GenesisPipelineProvider(Provider):
    def __init__(self, pipeline_dir: str = "vendor/transcription_engine"):
        super().__init__(name="genesis-kb-pipeline")
        self._dir = Path(pipeline_dir)

    def transcribe(self, audio_path: Path) -> str:
        # Adjust command based on README inspection in Step 5
        result = subprocess.run(
            ["python", "main.py", "--audio", str(audio_path.resolve()), "--output", "stdout"],
            cwd=self._dir,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Pipeline failed: {result.stderr}")
        return result.stdout.strip()
```

> **Note:** After reading the actual genesis-kb README in Step 5, update the `subprocess.run` command arguments to match their actual CLI interface. The interface above is a placeholder that must be corrected.

- [ ] **Step 7: Add to CLI providers list**

In `eval/run_eval.py`, add:

```python
from eval.providers.genesis_kb import GenesisPipelineProvider

# In main(), add to providers list:
providers = [
    GenesisPipelineProvider(),
    OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"]),
    GeminiProvider(api_key=os.environ["GEMINI_API_KEY"]),
    SarvamProvider(api_key=os.environ["SARVAM_API_KEY"]),
]
```

Now the CSV will have 40 rows (10 videos × 4 providers) and directly benchmarks genesis-kb against alternatives.

- [ ] **Step 8: Run tests**

```bash
pytest tests/test_providers.py -v
```

Expected: all PASS.

- [ ] **Step 9: Commit**

```bash
git add eval/providers/genesis_kb.py vendor/ eval/run_eval.py tests/test_providers.py
git commit -m "feat: add genesis-kb pipeline as benchmark provider"
```

---

*Plan complete.*
