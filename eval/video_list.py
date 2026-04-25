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
    # Bitcoin 2025 — Las Vegas, May 2025 (individual clips from Bitcoin Magazine YouTube)
    VideoEntry(
        slug="bitcoin-2025-saylor-21-ways",
        youtube_url="https://www.youtube.com/watch?v=reVebuAf_Cs",
        title="21 Ways To Wealth",
        speaker="Michael Saylor",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-jd-vance-keynote",
        youtube_url="https://www.youtube.com/watch?v=hMK2ULrVq6A",
        title="JD Vance Keynote",
        speaker="JD Vance",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-jack-mallers-hodlrs-dilemma",
        youtube_url="https://www.youtube.com/watch?v=RoRZE2DpEzE",
        title="The HODLers Dilemma",
        speaker="Jack Mallers",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-vivek-ramaswamy",
        youtube_url="https://www.youtube.com/watch?v=XgyF29388EE",
        title="Ending America's Crisis",
        speaker="Vivek Ramaswamy",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-ross-ulbricht",
        youtube_url="https://www.youtube.com/watch?v=8ZZGRA-8ZMU",
        title="Freedom, Decentralization, Unity",
        speaker="Ross Ulbricht",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-saylor-corporations",
        youtube_url="https://www.youtube.com/watch?v=3-vBBYEXv6M",
        title="Bitcoin for Corporations",
        speaker="Michael Saylor",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bitcoin-2025-saylor-why-bitcoin-qa",
        youtube_url="https://www.youtube.com/watch?v=AH236XOWNiI",
        title="Why Bitcoin Q+A",
        speaker="Michael Saylor",
        conference="Bitcoin 2025",
        year=2025,
        gt_slug=None,
    ),
    # Baltic Honeybadger 2025 — Riga, August 2025
    # NOTE: Day 1 is a full-day livestream (~8h). Consider trimming with yt-dlp --download-sections.
    VideoEntry(
        slug="bh-2025-day1-livestream",
        youtube_url="https://www.youtube.com/watch?v=W2TJuQ1TWYs",
        title="Day 1 Livestream",
        speaker="Various",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-ark-powered",
        youtube_url="https://www.youtube.com/watch?v=qPkgs1sLaX0",
        title="Everything Powered by Ark",
        speaker="Various",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
    VideoEntry(
        slug="bh-2025-panel-willy-woo-pysh",
        youtube_url="https://www.youtube.com/watch?v=-Mgy1_0l0Ms",
        title="Panel: Willy Woo, Max Kei, Efrat Fenigson, Preston Pysh",
        speaker="Willy Woo, Max Kei, Efrat Fenigson, Preston Pysh",
        conference="Baltic Honeybadger 2025",
        year=2025,
        gt_slug=None,
    ),
]
