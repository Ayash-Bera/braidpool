# Running the evaluation

1. Copy .env.example to .env and fill in API keys
2. Replace placeholder YouTube URLs in eval/video_list.py with real conference video URLs
3. Run: python -m eval.run_eval
4. Results appear in results/results.csv (40 rows: 10 videos × 4 providers)

# Providers benchmarked
- genesis-kb-pipeline (upstream transcription_engine)
- openai-whisper-1
- gemini-1.5-flash
- sarvam-stt-v1

# Metrics
- WER: Word Error Rate (requires ground truth from bitcointranscripts)
- CER: Character Error Rate (requires ground truth from bitcointranscripts)
- Note: 2025 conference videos may not yet have ground truth — WER/CER will be None
