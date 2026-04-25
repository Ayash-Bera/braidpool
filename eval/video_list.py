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
