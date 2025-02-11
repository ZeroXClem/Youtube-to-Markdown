import argparse
import json
import re
import os
from typing import List, Optional
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import requests
# Assuming transcript_helper.py is in the same directory
from transcript_helper import get_transcript_with_fallback


def sanitize_filename(title: str) -> str:
    """Sanitizes a string to be a valid filename."""
    s = re.sub(r'[\\/*?:"<>|]', "", title)
    s = s.replace(" ", "_")
    return s

def get_video_info(video_id: str) -> dict:
    """Fetches video info using noembed.  Returns a dictionary."""
    try:
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "title": data.get("title", "Unknown Title"),
            "author_name": data.get("author_name", "Unknown Channel")
        }
    except requests.RequestException:
        return {
            "title": "Unknown Title",
            "author_name": "Unknown Channel"
        }

def process_transcript(transcript: List[dict]) -> List[str]:
    """Processes the transcript into paragraphs."""
    full_text = ' '.join([fragment['text'] for fragment in transcript])
    full_text = re.sub(r'\[?[0-9]+:[0-9]+\]?', '', full_text)
    sentences = re.split(r'(?<=[.!?]) +', full_text)

    paragraphs = []
    current_paragraph = []
    for sentence in sentences:
        current_paragraph.append(sentence)
        if len(current_paragraph) >= 3:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    return paragraphs

def extract_video_id(url: str) -> Optional[str]:
    """Extracts the video ID from a YouTube URL, or returns None."""
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

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


def save_transcript(formatted_transcript: str, filename: str, extension: str, output_directory: str):
    """Saves the transcript to a file."""
    file_path = os.path.join(output_directory, f"{filename}.{extension}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted_transcript)

def get_playlist_video_ids(playlist_url: str) -> List[str]:
    """Extracts video IDs from a YouTube playlist using yt-dlp."""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'dump_single_json': True,
            'playlistend': 500,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(playlist_url, download=False)
            if 'entries' in result:
                return [entry['id'] for entry in result['entries'] if entry]
            else:
                return []
    except yt_dlp.utils.DownloadError as e:
        print(f"Error extracting playlist: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while extracting playlist: {e}")
        return[]


def download_single_transcript(video_id: str, language: str, export_format: str, output_dir: str):
    """Downloads and saves a single transcript."""
    try:
        transcript = get_transcript_with_fallback(video_id, language)
        video_info = get_video_info(video_id)  # Use your existing function
        video_title = video_info['title']
        filename = sanitize_filename(video_title)
        paragraphs = process_transcript(transcript) #processes transcript

        if export_format == "Markdown":
            formatted_transcript = f"# {video_title}\n\n"
            formatted_transcript += "\n\n".join(paragraphs)
            extension = "md"
        elif export_format == "Plain Text":
            formatted_transcript = f"{video_title}\n\n"
            formatted_transcript += "\n\n".join(paragraphs)
            extension = "txt"
        else:  # JSON
            formatted_transcript = json.dumps({
                "title": video_info['title'],
                "author": video_info['author_name'],
                "paragraphs": paragraphs
            }, indent=2, ensure_ascii=False)
            extension = "json"

        save_transcript(formatted_transcript, filename, extension, output_dir)
        print(f"\n✅ Transcript saved as {filename}.{extension} in {output_dir}")

    except VideoUnavailable:
        print(f"❌ Video {video_id} is unavailable.")
    except TranscriptsDisabled:
        print(f"❌ Transcripts are disabled for video {video_id}.")
    except NoTranscriptFound:
        print(f"❌ No transcripts found for the selected language for video {video_id}.")
    except Exception as e:
        print(f"❌ An unexpected error occurred for video {video_id}: {e}")


def process_batch(video_ids: List[str], language: str, export_format: str, output_dir: str):
    """Processes a batch of video IDs."""
    for video_id in video_ids:
        if "playlist" not in video_id.lower():
            download_single_transcript(video_id, language, export_format, output_dir)
        else: #Handles playlist links passed from a file
            ids_from_playlist = get_playlist_video_ids(video_id)
            if ids_from_playlist:
                for extracted_id in ids_from_playlist:
                    download_single_transcript(extracted_id, language, export_format, output_dir)



def main():
    parser = argparse.ArgumentParser(description="Download YouTube video transcripts.")
    parser.add_argument("input", help="YouTube video URL/ID, playlist URL, or path to a file containing URLs/IDs")
    parser.add_argument("-l", "--language", default="en", help="Transcript language code (default: en)")
    parser.add_argument("-f", "--format", default="txt", choices=["txt", "md", "json"], help="Output format (txt, md, json)")
    parser.add_argument("-o", "--output", help="Output directory (default: current directory)")
    args = parser.parse_args()

    output_dir = args.output if args.output else "."
    if not os.path.isdir(output_dir):
        print("❌ Invalid output directory.")
        return

    available_formats = {
     "txt": "Plain Text",
     "md": "Markdown",
     "json": "JSON",
    }
    export_format = available_formats.get(args.format)

    if os.path.isfile(args.input):
        try:
            with open(args.input, "r", encoding="utf-8") as file:
                video_ids = [line.strip() for line in file if line.strip()]  #handles files and playlists
                # Extract video IDs, handling potential playlist URLs within the file
                cleaned_ids = []
                for vid_or_url in video_ids:
                    extracted_id = extract_video_id(vid_or_url)
                    if extracted_id:
                        cleaned_ids.append(extracted_id)
                    elif "playlist" in vid_or_url.lower():
                         playlist_ids = get_playlist_video_ids(vid_or_url)
                         if playlist_ids:
                            cleaned_ids.extend(playlist_ids)

                process_batch(cleaned_ids, args.language, export_format, output_dir)

        except Exception as e:
            print(f"Error processing file: {e}")

    elif "playlist" in args.input.lower():
        video_ids = get_playlist_video_ids(args.input)
        if video_ids:
            process_batch(video_ids, args.language, export_format, output_dir)
    else:
        video_id = extract_video_id(args.input)
        if video_id:
            download_single_transcript(video_id, args.language, export_format, output_dir)



if __name__ == "__main__":
    main()

