#!/usr/bin/env python3
"""
Streamlit YouTube Transcript Downloader — fixed for youtube-transcript-api v1.x
------------------------------------------------------------------------------

• Accepts either list[dict] *or* FetchedTranscriptSnippet objects.
• Converts to raw data if the helper returns a FetchedTranscript.
• Dual‑compatible `process_transcript()`.

Save as `youtube-transcript-downloader2.py`, then run:

    streamlit run youtube-transcript-downloader2.py
"""

import base64
import json
import re
from datetime import timedelta

import requests
import streamlit as st
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

# ---- helper: fetch with fallback -------------------------------------------
from transcript_helper import get_transcript_with_fallback


def get_video_info(video_id: str):
    url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
    try:
        data = requests.get(url, timeout=10).json()
    except requests.RequestException:
        data = {}
    return {
        "title": data.get("title", "Unknown Title"),
        "author_name": data.get("author_name", "Unknown Channel"),
        "thumbnail_url": data.get("thumbnail_url", ""),
    }


def format_time(seconds: int):
    return str(timedelta(seconds=int(seconds)))


def process_transcript(transcript):
    """Return paragraphs from *transcript*.

    Accepts either dicts or FetchedTranscriptSnippet objects."""
    texts = [
        getattr(frag, "text", frag.get("text", "")) for frag in transcript
    ]
    full_text = " ".join(texts)
    full_text = re.sub(r"\[?[0-9]+:[0-9]+\]?", "", full_text)

    sentences = re.split(r"(?<=[.!?]) +", full_text)

    paragraphs, current = [], []
    for sentence in sentences:
        current.append(sentence)
        if len(current) >= 3:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def extract_video_id(url: str):
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url
    pats = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ]
    for pat in pats:
        m = re.match(pat, url)
        if m:
            return m.group(1)
    return None


# ---- Streamlit UI -----------------------------------------------------------
st.title("📜 YouTube Transcript Downloader")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# simple inline css
st.markdown(
    """<style>
    .stApp {background-color:%s; color:%s;}
    a {color:#1e90ff;}
    </style>""" % ("#2b2b2b" if dark_mode else "#ffffff", "#ffffff" if dark_mode else "#000000"),  # noqa: E501
    unsafe_allow_html=True,
)

video_url = st.text_input("🔗 Enter YouTube Video URL or Video ID:")
file_name = st.text_input("📝 Enter file name (without extension):", "transcript")
export_format = st.selectbox("📂 Select export format:", ["Markdown", "Plain Text", "JSON"])
download = st.button("⬇️ Download Transcript")


def download_transcript(url: str, fname: str, fmt: str):
    try:
        vid = extract_video_id(url)
        if not vid:
            st.error("❌ Invalid YouTube URL or Video ID.")
            return

        info = get_video_info(vid)
        if info["thumbnail_url"]:
            st.image(info["thumbnail_url"], caption=f"{info['title']} – {info['author_name']}")  # noqa: E501

        tlist = YouTubeTranscriptApi.list_transcripts(vid)
        langs = [tr.language_code for tr in tlist]
        sel_lang = st.selectbox("🗣️ Select transcript language:", langs)

        transcript = get_transcript_with_fallback(vid, sel_lang)

        # if helper returned a FetchedTranscript, convert:
        if hasattr(transcript, "to_raw_data"):
            transcript = transcript.to_raw_data()

        paragraphs = process_transcript(transcript)

        if fmt == "Markdown":
            content = f"# {info['title']}\n\n" + "\n\n".join(paragraphs)
            ext = "md"
            mime = "text/markdown"
        elif fmt == "Plain Text":
            content = f"{info['title']}\n\n" + "\n\n".join(paragraphs)
            ext = "txt"
            mime = "text/plain"
        else:
            content = json.dumps(
                {"title": info['title'], "author": info['author_name'], "paragraphs": paragraphs},
                indent=2,
            )
            ext = "json"
            mime = "application/json"

        b64 = base64.b64encode(content.encode()).decode()
        href = f'<a href="data:{mime};base64,{b64}" download="{fname}.{ext}">📥 Click here to download your transcript</a>'  # noqa: E501
        st.markdown(href, unsafe_allow_html=True)

        # preview
        st.subheader("📝 Transcript Preview")
        preview_len = 1000
        if fmt == "JSON" and len(content) <= preview_len:
            st.json(json.loads(content))
        else:
            st.text((content[:preview_len] + "...") if len(content) > preview_len else content)

    except TranscriptsDisabled:
        st.error("❌ Transcripts are disabled for this video.")
    except NoTranscriptFound:
        st.error("❌ No transcripts found for the selected language.")
    except VideoUnavailable:
        st.error("❌ The video is unavailable.")
    except Exception as exc:
        st.error(f"❌ An unexpected error occurred: {exc}")


if download:
    if not video_url:
        st.error("❌ Please enter a YouTube Video URL or Video ID.")
    elif not file_name:
        st.error("❌ Please enter a valid file name.")
    else:
        download_transcript(video_url.strip(), file_name.strip(), export_format)

