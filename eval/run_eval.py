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
