#!/usr/bin/env python3
"""
YouTube Transcript Downloader – v1.1 (Linux‑friendly filenames)

Changes:
• sanitize_filename() now produces simple ASCII‑only, kebab‑case names that
  play nicely with Linux tools (`ComfyUI_Tutorial` → `comfyui-tutorial`).
• Rest of the CLI unchanged from the previous working version.
"""

import json
import os
import re
import unicodedata
from datetime import datetime

import requests
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from transcript_helper import get_transcript_with_fallback  # local helper

# ---------------------------------------------------------------------------
def sanitize_filename(title: str) -> str:
    """Return a safe, predictable filename.

    • ASCII‑only (strip accents / symbols)
    • lower‑case kebab‑case
    • max 100 chars
    • keeps dots so you can append an extension later
    """
    # Normalize & transliterate to ASCII
    slug = (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # Replace ampersands with 'and'
    slug = slug.replace("&", "and")
    # Turn whitespace into single dashes
    slug = re.sub(r"\s+", "-", slug)
    # Remove anything not alphanum, dash, underscore or dot
    slug = re.sub(r"[^0-9A-Za-z._-]", "", slug)
    # Collapse multiple dashes
    slug = re.sub(r"-{2,}", "-", slug)
    # Trim leading/trailing punctuation
    slug = slug.strip("-_.").lower()
    return slug[:100]  # 100 chars is plenty


def get_video_info(video_id: str) -> dict[str, str]:
    url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
    try:
        data = requests.get(url, timeout=10).json()
    except requests.RequestException:
        data = {}
    return {
        "title": data.get("title", "unknown-title"),
        "author_name": data.get("author_name", "unknown-channel"),
    }


def process_transcript(transcript):
    texts = [
        getattr(snippet, "text", snippet.get("text", "")) for snippet in transcript
    ]
    full_text = " ".join(texts)
    full_text = re.sub(r"\[?[0-9]+:[0-9]+\]?", "", full_text)

    sentences = re.split(r"(?<=[.!?]) +", full_text)
    paras, current = [], []
    for sent in sentences:
        current.append(sent)
        if len(current) >= 3:
            paras.append(" ".join(current))
            current = []
    if current:
        paras.append(" ".join(current))
    return paras


def extract_video_id(url_or_id: str):
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url_or_id):
        return url_or_id
    pats = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ]
    for pat in pats:
        m = re.match(pat, url_or_id)
        if m:
            return m.group(1)
    return None


def save_transcript(content: str, name: str, ext: str, out_dir: str = "."):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.{ext}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ---------------------------------------------------------------------------
def main():
    print("\n📜 YouTube Transcript Downloader CLI\n" + "-" * 40)

    while True:
        vid_input = input("🔗 Enter YouTube Video URL or Video ID: ").strip()
        vid = extract_video_id(vid_input)
        if vid:
            break
        print("❌ Invalid YouTube URL or Video ID. Please try again.")

    try:
        info = get_video_info(vid)
        print(f"\n📺 Video: {info['title']}")
        print(f"👤 Channel: {info['author_name']}")

        tlist = YouTubeTranscriptApi.list_transcripts(vid)
        langs = [t.language_code for t in tlist]
        print("\n🗣️ Available languages:")
        for i, l in enumerate(langs, 1):
            print(f"{i}. {l}")
        while True:
            try:
                idx = int(input("\nSelect language number: ")) - 1
                if 0 <= idx < len(langs):
                    lang = langs[idx]
                    break
            except ValueError:
                pass
            print("❌ Invalid selection. Please try again.")

        transcript = get_transcript_with_fallback(vid, lang)
        if hasattr(transcript, "to_raw_data"):
            transcript = transcript.to_raw_data()
        paras = process_transcript(transcript)

        fmts = ["Markdown", "Plain Text", "JSON"]
        print("\n📂 Available export formats:")
        for i, f in enumerate(fmts, 1):
            print(f"{i}. {f}")
        while True:
            try:
                fidx = int(input("\nSelect format number: ")) - 1
                if 0 <= fidx < len(fmts):
                    target_fmt = fmts[fidx]
                    break
            except ValueError:
                pass
            print("❌ Invalid selection. Please try again.")

        out_dir = input("\n📁 Enter output directory (blank = current): ").strip() or "."
        fname = sanitize_filename(info['title']) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")  # type: ignore

        if target_fmt == "Markdown":
            content = f"# {info['title']}\n\n" + "\n\n".join(paras)
            ext = "md"
        elif target_fmt == "Plain Text":
            content = f"{info['title']}\n\n" + "\n\n".join(paras)
            ext = "txt"
        else:
            content = json.dumps(
                {"title": info['title'], "author": info['author_name'], "paragraphs": paras},
                indent=2,
            )
            ext = "json"

        path = save_transcript(content, fname, ext, out_dir)
        print(f"\n✅ Transcript saved to {path}\n")

    except TranscriptsDisabled:
        print("❌ Transcripts are disabled for this video.")
    except NoTranscriptFound:
        print("❌ No transcripts found for the selected language.")
    except VideoUnavailable:
        print("❌ The video is unavailable.")
    except Exception as ex:
        print(f"❌ An unexpected error occurred: {ex}")


if __name__ == "__main__":
    main()

