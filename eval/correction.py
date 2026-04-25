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
