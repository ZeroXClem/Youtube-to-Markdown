import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import re

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return video_id.group(1) if video_id else None

def fetch_transcript(video_id):
    """
    Fetch the transcript for the given video ID.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript_list
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def transcript_to_markdown(transcript):
    """
    Convert the transcript to markdown format.
    """
    markdown = ""
    for entry in transcript:
        time = entry['start']
        minutes, seconds = divmod(time, 60)
        formatted_time = f"{int(minutes)}:{int(seconds):02d}"
        markdown += f"**[{formatted_time}]** {entry['text']}\n\n"
    return markdown

def main():
    st.title("YouTube Transcript to Markdown")

    url = st.text_input("Enter YouTube Video URL")
    
    if url:
        video_id = get_video_id(url)
        if video_id:
            transcript = fetch_transcript(video_id)
            if transcript:
                markdown = transcript_to_markdown(transcript)
                st.markdown(markdown)
                
                st.download_button(
                    label="Download Transcript as Markdown",
                    data=markdown,
                    file_name="transcript.md",
                    mime="text/markdown"
                )
        else:
            st.error("Invalid YouTube URL")

if __name__ == "__main__":
    main()

