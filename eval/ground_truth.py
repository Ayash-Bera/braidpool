import requests
from pathlib import Path

_BASE = "https://raw.githubusercontent.com/bitcointranscripts/bitcointranscripts/master"

def _strip_frontmatter(text: str) -> str:
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
