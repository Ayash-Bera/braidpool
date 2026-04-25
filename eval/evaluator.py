from pathlib import Path
from typing import Optional
from eval.downloader import download_audio
from eval.ground_truth import fetch_ground_truth
from eval.correction import correct_transcript
from eval.summarizer import summarize
from eval.translator import translate_to_hindi
from eval import metrics as m

def evaluate_video(
    entry,
    providers: list,
    anthropic_api_key: Optional[str],
    sarvam_api_key: Optional[str] = None,
    audio_dir: Path = Path("data/audio"),
    gt_cache_dir: Path = Path("data/ground_truth"),
) -> list[dict]:
    audio_path = download_audio(entry, output_dir=audio_dir)
    ground_truth = fetch_ground_truth(entry, cache_dir=gt_cache_dir)
    results = []
    for provider in providers:
        try:
            raw = provider.transcribe(audio_path)
        except Exception as e:
            print(f"    [{provider.name}] transcription failed: {e}")
            continue
        if anthropic_api_key:
            corrected = correct_transcript(raw, api_key=anthropic_api_key)
            summary = summarize(corrected, api_key=anthropic_api_key)
        else:
            corrected = None
            summary = None
        if sarvam_api_key:
            try:
                hindi = translate_to_hindi(raw, api_key=sarvam_api_key)
            except Exception as e:
                print(f"    [{provider.name}] translation failed: {e}")
                hindi = None
        else:
            hindi = None
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
            "hindi_transcript": hindi,
            "wer": metric.wer,
            "cer": metric.cer,
            "audio_duration_seconds": None,
        })
    return results
