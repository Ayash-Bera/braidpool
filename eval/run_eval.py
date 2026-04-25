import os
from pathlib import Path
from dotenv import load_dotenv
from eval.video_list import VIDEOS
from eval.evaluator import evaluate_video
from eval.csv_exporter import export_results

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
        print("GEMINI_API_KEY not set — skipping gemini-1.5-flash")
    if os.getenv("SARVAM_API_KEY"):
        from eval.providers.sarvam_stt import SarvamProvider
        providers.append(SarvamProvider(api_key=os.environ["SARVAM_API_KEY"]))
    else:
        print("SARVAM_API_KEY not set — skipping sarvam-stt-v1")
    return providers

def main():
    providers = _build_providers()
    if not providers:
        print("No providers available. Set at least one API key in .env")
        return
    print(f"Running with providers: {[p.name for p in providers]}\n")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ANTHROPIC_API_KEY not set — correction and summarization will be skipped\n")
    all_rows = []
    for i, entry in enumerate(VIDEOS, 1):
        print(f"[{i}/{len(VIDEOS)}] {entry.slug}")
        try:
            rows = evaluate_video(
                entry,
                providers=providers,
                anthropic_api_key=anthropic_key,
            )
            all_rows.extend(rows)
            print(f"  done — {len(rows)} rows")
        except Exception as e:
            print(f"  ERROR: {e}")
    out = Path("results/results.csv")
    export_results(all_rows, out)
    print(f"\nWrote {len(all_rows)} rows to {out}")

if __name__ == "__main__":
    main()
