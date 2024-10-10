import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import json
import requests
from datetime import timedelta
import re
import base64

# Function to get video info
def get_video_info(video_id):
    try:
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "title": data.get("title", "Unknown Title"),
            "author_name": data.get("author_name", "Unknown Channel"),
            "thumbnail_url": data.get("thumbnail_url", "")
        }
    except requests.RequestException:
        return {
            "title": "Unknown Title",
            "author_name": "Unknown Channel",
            "thumbnail_url": ""
        }

# Function to format time
def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

# Function to process transcript and create paragraphs
def process_transcript(transcript):
    # Combine all text fragments
    full_text = ' '.join([fragment['text'] for fragment in transcript])

    # Remove any remaining timestamps (if any)
    full_text = re.sub(r'\[?[0-9]+:[0-9]+\]?', '', full_text)

    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', full_text)

    # Group sentences into paragraphs (every 3-5 sentences)
    paragraphs = []
    current_paragraph = []
    for sentence in sentences:
        current_paragraph.append(sentence)
        if len(current_paragraph) >= 3:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []

    # Add any remaining sentences as a paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))

    return paragraphs

# Title of the Web App
st.title("📜 YouTube Transcript Downloader")

# Dark mode toggle
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    a {
        color: #1e90ff;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    a {
        color: #1e90ff;
    }
    </style>
    """, unsafe_allow_html=True)

# Get the URL Input
video_url = st.text_input("🔗 Enter YouTube Video URL or YouTube Video ID:")

# File name input
file_name = st.text_input("📝 Enter file name (without extension):", "transcript")

# Export format selection
export_format = st.selectbox("📂 Select export format:", ["Markdown", "Plain Text", "JSON"])

# Download Button
download = st.button("⬇️ Download Transcript")

# YouTube Transcript API to download the transcript and format it
def download_transcript(video_url, file_name, export_format):
    try:
        # Extract the Video ID from the URL
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("❌ Invalid YouTube URL or Video ID.")
            return

        # Get video info
        video_info = get_video_info(video_id)
        if video_info['thumbnail_url']:
            st.image(video_info['thumbnail_url'], caption=f"{video_info['title']} - {video_info['author_name']}")
        else:
            st.warning("⚠️ Unable to fetch video thumbnail.")

        # Get available transcript languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = [transcript.language_code for transcript in transcript_list]
        selected_language = st.selectbox("🗣️ Select transcript language:", languages)

        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language])

        # Process the transcript
        paragraphs = process_transcript(transcript)

        # Format the transcript based on the selected export format
        if export_format == "Markdown":
            formatted_transcript = f"# {video_info['title']}\n\n"
            for paragraph in paragraphs:
                formatted_transcript += f"{paragraph}\n\n"
            file_extension = "md"
            mime_type = "text/markdown"
        elif export_format == "Plain Text":
            formatted_transcript = f"{video_info['title']}\n\n"
            for paragraph in paragraphs:
                formatted_transcript += f"{paragraph}\n\n"
            file_extension = "txt"
            mime_type = "text/plain"
        else:  # JSON
            formatted_transcript = json.dumps({
                "title": video_info['title'],
                "author": video_info['author_name'],
                "paragraphs": paragraphs
            }, indent=2)
            file_extension = "json"
            mime_type = "application/json"

        # Encode the transcript for download
        b64 = base64.b64encode(formatted_transcript.encode()).decode()

        href = f'<a href="data:{mime_type};base64,{b64}" download="{file_name}.{file_extension}">📥 Click here to download your transcript</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Display a preview of the transcript
        st.subheader("📝 Transcript Preview")
        preview_length = 1000
        preview_text = formatted_transcript[:preview_length] + "..." if len(formatted_transcript) > preview_length else formatted_transcript
        if export_format == "JSON":
            st.json(json.loads(formatted_transcript)) if len(formatted_transcript) <= preview_length else st.text(preview_text)
        else:
            st.text(preview_text)

    except TranscriptsDisabled:
        st.error("❌ Transcripts are disabled for this video.")
    except NoTranscriptFound:
        st.error("❌ No transcripts found for the selected language.")
    except VideoUnavailable:
        st.error("❌ The video is unavailable. Please check the Video ID or URL.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)}")

def extract_video_id(url):
    """
    Extract the YouTube video ID from a URL or return the ID if it's already provided.
    """
    # If the input is already a video ID (11 characters)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    # Define regex patterns for YouTube URLs
    regex_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in regex_patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

# Download Transcript
if download:
    if not video_url:
        st.error("❌ Please enter a YouTube Video URL or Video ID.")
    elif not file_name:
        st.error("❌ Please enter a valid file name.")
    else:
        download_transcript(video_url.strip(), file_name.strip(), export_format)