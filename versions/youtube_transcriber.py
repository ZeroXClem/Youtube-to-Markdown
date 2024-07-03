import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from markdownify import markdownify as md

# Title of the Web App
st.title("YouTube Transcript Downloader")

# Get the URL Input
video_url = st.text_input("Enter YouTube Video URL or YouTube Video ID :")

# Download Button
download = st.button("Download Transcript")

# YouTube Transcript API to download the transcript in SRT format
def download_transcript(video_url):
    # Get the transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_url)

    # Convert transcript to markdown
    transcript_text = '\n'.join([fragment['text'] for fragment in transcript])
    transcript_md = md(transcript_text)
    
    # Write to markdown file
    with open('transcript.md', 'w') as f:
        f.write(transcript_md)

    st.markdown("Transcript Downloaded")

    # Download the generated markdown file
    st.download_button("Download Markdown", 'transcript.md')

# Download Transcript       
if download:
    # Extract the Video ID from the URL
    splits = video_url.split("watch?v=")
    if len(splits) > 1:
        video_id = splits[-1]
    else:
        video_id = video_url

    download_transcript(video_id)
