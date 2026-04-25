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
