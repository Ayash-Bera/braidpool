from pathlib import Path
import yt_dlp

def download_audio(entry, output_dir: Path = Path("data/audio")) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f"{entry.slug}.mp3"
    if dest.exists():
        return dest
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / f"{entry.slug}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([entry.youtube_url])
    return dest
