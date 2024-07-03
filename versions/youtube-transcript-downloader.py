import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from markdownify import markdownify as md
import os
import json
import requests
from datetime import timedelta

# Function to get video info
def get_video_info(video_id):
    url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
    data = requests.get(url).json()
    return {
        "title": data.get("title", "Unknown Title"),
        "author_name": data.get("author_name", "Unknown Channel"),
        "thumbnail_url": data.get("thumbnail_url", "")
    }

# Function to format time
def format_time(seconds):
    return str(timedelta(seconds=int(seconds)))

# Title of the Web App
st.title("YouTube Transcript Downloader")

# Dark mode toggle
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

dark_mode = st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Get the URL Input
video_url = st.text_input("Enter YouTube Video URL or YouTube Video ID:")

# File name and save location inputs
file_name = st.text_input("Enter file name (without extension):", "transcript")
save_path = st.text_input("Enter save path (leave empty for current directory):", "")

# Export format selection
export_format = st.selectbox("Select export format:", ["Markdown", "Plain Text", "SRT", "JSON"])

# Download Button
download = st.button("Download Transcript")

# YouTube Transcript API to download the transcript and format it
def download_transcript(video_url, file_name, save_path, export_format):
    try:
        # Extract the Video ID from the URL
        if "youtube.com" in video_url:
            video_id = video_url.split("v=")[-1].split("&")[0]
        elif "youtu.be" in video_url:
            video_id = video_url.split("/")[-1]
        else:
            video_id = video_url

        # Get video info
        video_info = get_video_info(video_id)
        st.image(video_info['thumbnail_url'], caption=f"{video_info['title']} - {video_info['author_name']}")

        # Get available transcript languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = [transcript.language_code for transcript in transcript_list]
        selected_language = st.selectbox("Select transcript language:", languages)

        # Get the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language])

        # Format the transcript based on the selected export format
        if export_format == "Markdown":
            formatted_transcript = "# " + video_info['title'] + "\n\n"
            for fragment in transcript:
                formatted_transcript += f"**[{format_time(fragment['start'])}]** {fragment['text']}\n\n"
            file_extension = "md"
        elif export_format == "Plain Text":
            formatted_transcript = video_info['title'] + "\n\n"
            for fragment in transcript:
                formatted_transcript += f"[{format_time(fragment['start'])}] {fragment['text']}\n\n"
            file_extension = "txt"
        elif export_format == "SRT":
            formatted_transcript = ""
            for i, fragment in enumerate(transcript, 1):
                start = format_time(fragment['start'])
                end = format_time(fragment['start'] + fragment['duration'])
                formatted_transcript += f"{i}\n{start},000 --> {end},000\n{fragment['text']}\n\n"
            file_extension = "srt"
        else:  # JSON
            formatted_transcript = json.dumps(transcript, indent=2)
            file_extension = "json"

        # Determine the full file path
        if save_path and not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, f"{file_name}.{file_extension}")

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)

        st.success("Transcript Downloaded")

        # Provide download link
        with open(file_path, 'r', encoding='utf-8') as f:
            st.download_button(
                label=f"Download {export_format}",
                data=f.read(),
                file_name=f"{file_name}.{file_extension}",
                mime=f"text/{file_extension}"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Download Transcript
if download:
    download_transcript(video_url, file_name, save_path, export_format)
