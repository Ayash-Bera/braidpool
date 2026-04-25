import os
import csv
import argparse
from pathlib import Path
from dotenv import load_dotenv
from eval.video_list import VIDEOS
from eval.evaluator import evaluate_video
from eval.csv_exporter import COLUMNS

load_dotenv()

def _build_providers():
    providers = []
    if os.getenv("GENESIS_KB_ENABLED"):
        from eval.providers.genesis_kb import GenesisPipelineProvider
        providers.append(GenesisPipelineProvider())
    if os.getenv("OPENAI_API_KEY"):
        from eval.providers.openai_stt import OpenAIProvider
        providers.append(OpenAIProvider(api_key=os.environ["OPENAI_API_KEY"]))
    else:
        print("OPENAI_API_KEY not set — skipping openai-whisper-1")
    if os.getenv("GEMINI_API_KEY"):
        from eval.providers.gemini_stt import GeminiProvider
        providers.append(GeminiProvider(api_key=os.environ["GEMINI_API_KEY"]))
    else:
        print("GEMINI_API_KEY not set — skipping gemini-2.0-flash")
    if os.getenv("SARVAM_API_KEY"):
        from eval.providers.sarvam_stt import SarvamProvider
        providers.append(SarvamProvider(api_key=os.environ["SARVAM_API_KEY"]))
    else:
        print("SARVAM_API_KEY not set — skipping sarvam-stt-v2.5")
    return providers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Run on first video only")
    parser.add_argument("--video", help="Run on a specific video slug only")
    args = parser.parse_args()

    providers = _build_providers()
    if not providers:
        print("No providers available. Set at least one API key in .env")
        return
    print(f"Running with providers: {[p.name for p in providers]}\n")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ANTHROPIC_API_KEY not set — correction and summarization will be skipped\n")
    sarvam_key = os.getenv("SARVAM_API_KEY")

    if args.video:
        videos = [v for v in VIDEOS if v.slug == args.video]
        if not videos:
            print(f"No video found with slug: {args.video}")
            return
    elif args.test:
        videos = VIDEOS[:1]
    else:
        videos = VIDEOS

    out = Path("results/results.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        total = 0
        for i, entry in enumerate(videos, 1):
            print(f"[{i}/{len(videos)}] {entry.slug}")
            try:
                rows = evaluate_video(
                    entry,
                    providers=providers,
                    anthropic_api_key=anthropic_key,
                    sarvam_api_key=sarvam_key,
                )
                writer.writerows(rows)
                f.flush()
                total += len(rows)
                print(f"  done — {len(rows)} rows (total so far: {total})")
            except Exception as e:
                print(f"  ERROR: {e}")
    print(f"\nWrote {total} rows to {out}")

if __name__ == "__main__":
    main()
