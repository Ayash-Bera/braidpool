# Bitcoin Conference STT Evaluation Pipeline
**Submitted by:** Ayash Bera | ayashbera@gmail.com | April 25, 2026

---

## What this is

The Bitcoin conference circuit produces some of the most substantive conversations happening anywhere in finance right now. Saylor, Mallers, Ramaswamy — these talks run anywhere from 12 to 77 minutes and cover everything from sovereign Bitcoin adoption to compound interest to self-custody law. They are also entirely in English, which means they are entirely inaccessible to the roughly 600 million Hindi speakers in India who are actively engaging with Bitcoin as a savings layer.

This pipeline transcribes those talks and translates them into Hindi, automatically, for any conference video on YouTube.

---

## How it works

The pipeline pulls audio from YouTube via yt-dlp, sends it to a speech-to-text provider, then passes the transcript through Sarvam's translation API. Every run writes a 13-column CSV: video metadata, the raw English transcript, an LLM-corrected version (when an Anthropic key is present), a summary, the full Hindi translation, WER/CER accuracy scores against ground truth, and audio duration.

Two STT providers are implemented:

**Sarvam (saarika:v2.5)** — a model built for Indian English. Audio gets chunked into 25-second segments via ffmpeg (Sarvam's API limit is 30 seconds), transcribed chunk by chunk, then rejoined. The translation step uses Sarvam's mayura:v1 model, which handles financial and political vocabulary well.

**Gemini (gemini-2.0-flash)** — handles full audio in a single call, no chunking needed. Retry logic uses exponential backoff starting at 10 seconds on 429 errors. Requires billing to be enabled in Google Cloud Console; the free tier quota is effectively zero for audio workloads of this size.

Any provider without an API key gets skipped at startup. The pipeline runs with whatever is available. Results flush to CSV after each video, so partial data is always recoverable.

---

## What came out

We ran the pipeline on Vivek Ramaswamy's 12-minute keynote from Bitcoin 2025 — "Ending America's Crisis." 729 seconds of audio.

Sarvam produced a complete English transcript. 10,693 characters. The compound interest slides, the Ohio industrial history, the argument that Bitcoin should be the hurdle rate for risk investments — all of it came through coherently. Bitcoin-specific terminology ("self-custody", "blockchain", "finite supply") handled correctly with no hallucinations.

The translator then split that into 14 chunks and returned the full Hindi translation. Terms like "Bitcoin" (बिटकॉइन), "compound interest" (चक्रवृद्धि ब्याज), and "self-custody" (स्व-संग्रहण) are preserved or correctly translated. A Hindi speaker can read the full speech, not a summary of it.

Sample from the English transcript:

> "The difference between the wealthy and everybody else in the country is whether or not you own an asset that compounds... If we're really targeting 15% returns, compounding for the next generation of Americans at a rate that actually matters, there's no version of that in the 21st century that does not include a serious discussion about the inclusion of Bitcoin."

Same passage in Hindi (output from mayura:v1):

> "देश में अमीर और बाकी सभी लोगों के बीच अंतर यह है कि क्या आपके पास ऐसी कोई संपत्ति है जो चक्रवृद्धि होती है... यदि हम वास्तव में 15% रिटर्न का लक्ष्य रख रहे हैं, तो 21वीं सदी में उस संस्करण में बिटकॉइन और भविष्य की परिसंपत्तियों को शामिल करने के बारे में एक गंभीर चर्चा शामिल नहीं है।"

The WER and CER columns are empty for now. Bitcointranscripts.com hasn't published ground truth for the 2025 conference yet. The scoring code runs automatically when they do.

---

## Why this matters for the ecosystem

Bitcoin conferences are where the serious arguments get made. The case for sovereign adoption, the legal frameworks for self-custody, the on-chain transparency arguments — this is where that reasoning gets developed and stress-tested in public. But the audience who can actually engage with it is currently limited to people who are comfortable with dense, technical English spoken at pace.

India has one of the fastest-growing Bitcoin communities in the world. A significant portion of that community does not follow conference-level English easily. Making this content available in Hindi — not translated summaries, but full transcripts — extends the actual conversation, not a filtered version of it.

The pipeline is also designed to scale. Adding a new language is one parameter change in the translator. Adding a new STT provider means implementing a six-line abstract class. The CSV output is structured for analysis: once ground truth exists, WER comparisons between providers run automatically. The correction and summarization columns (via LLM) give a path toward higher-quality outputs once an Anthropic key is available.

---

## Pipeline outputs (per video, per provider)

| Column | Contents |
|--------|----------|
| `video_slug` | Unique identifier |
| `title` | Talk title |
| `speaker` | Speaker name |
| `conference` | Conference name |
| `year` | Year |
| `provider` | STT provider used |
| `raw_transcript` | Full English transcript |
| `corrected_transcript` | LLM-corrected version (if Anthropic key set) |
| `summary` | 200-word domain summary (if Anthropic key set) |
| `hindi_transcript` | Full Hindi translation via Sarvam mayura:v1 |
| `wer` | Word Error Rate vs ground truth |
| `cer` | Character Error Rate vs ground truth |
| `audio_duration_seconds` | Audio length |

---

## Code structure

```
eval/
├── video_list.py       — 10 Bitcoin 2025 talks with YouTube URLs
├── downloader.py       — yt-dlp download, skip if cached
├── ground_truth.py     — fetches from bitcointranscripts.com
├── providers/
│   ├── gemini_stt.py   — Gemini multimodal + exponential backoff
│   ├── sarvam_stt.py   — Sarvam + ffmpeg chunking
│   ├── openai_stt.py   — Whisper-1
│   └── genesis_kb.py   — upstream pipeline wrapper
├── translator.py       — Sarvam mayura:v1, 900-char chunk/rejoin
├── metrics.py          — WER/CER via jiwer
├── correction.py       — LLM transcript correction
├── summarizer.py       — LLM summarization
├── evaluator.py        — per-video orchestration
└── run_eval.py         — entry point (--test, --video flags)
```

21/21 tests passing.

---

## Running it

```bash
pip install -r requirements.txt

# .env needs at minimum one of:
SARVAM_API_KEY=...
GEMINI_API_KEY=...   # requires billing enabled in Google Cloud Console

# single video
python -m eval.run_eval --video bitcoin-2025-vivek-ramaswamy

# full eval
python -m eval.run_eval
```
