from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import requests
import json
import re
from datetime import timedelta
from transcript_helper import get_transcript_with_fallback

def get_video_info(video_id):
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

def process_transcript(transcript):
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

def extract_video_id(url):
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

def save_transcript(formatted_transcript, filename, extension):
    with open(f"{filename}.{extension}", 'w', encoding='utf-8') as f:
        f.write(formatted_transcript)

def main():
    print("📜 YouTube Transcript Downloader CLI")
    print("-" * 40)
    
    # Get video URL/ID
    while True:
        video_url = input("🔗 Enter YouTube Video URL or Video ID: ").strip()
        video_id = extract_video_id(video_url)
        if video_id:
            break
        print("❌ Invalid YouTube URL or Video ID. Please try again.")
    
    try:
        # Get video info
        video_info = get_video_info(video_id)
        print(f"\n📺 Video: {video_info['title']}")
        print(f"👤 Channel: {video_info['author_name']}")
        
        # Get available languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = [transcript.language_code for transcript in transcript_list]
        
        print("\n🗣️ Available languages:")
        for i, lang in enumerate(languages, 1):
            print(f"{i}. {lang}")
        
        # Select language
        while True:
            try:
                lang_idx = int(input("\nSelect language number: ")) - 1
                if 0 <= lang_idx < len(languages):
                    selected_language = languages[lang_idx]
                    break
                print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Get transcript
        transcript = get_transcript_with_fallback(video_id, selected_language)
        paragraphs = process_transcript(transcript)
        
        # Select export format
        print("\n📂 Available export formats:")
        formats = ["Markdown", "Plain Text", "JSON"]
        for i, fmt in enumerate(formats, 1):
            print(f"{i}. {fmt}")
        
        while True:
            try:
                fmt_idx = int(input("\nSelect format number: ")) - 1
                if 0 <= fmt_idx < len(formats):
                    export_format = formats[fmt_idx]
                    break
                print("❌ Invalid selection. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Get filename
        filename = input("\n📝 Enter file name (without extension): ").strip() or "transcript"
        
        # Format and save transcript
        if export_format == "Markdown":
            formatted_transcript = f"# {video_info['title']}\n\n"
            formatted_transcript += "\n\n".join(paragraphs)
            extension = "md"
        elif export_format == "Plain Text":
            formatted_transcript = f"{video_info['title']}\n\n"
            formatted_transcript += "\n\n".join(paragraphs)
            extension = "txt"
        else:  # JSON
            formatted_transcript = json.dumps({
                "title": video_info['title'],
                "author": video_info['author_name'],
                "paragraphs": paragraphs
            }, indent=2)
            extension = "json"
        
        save_transcript(formatted_transcript, filename, extension)
        print(f"\n✅ Transcript saved as {filename}.{extension}")
        
    except TranscriptsDisabled:
        print("❌ Transcripts are disabled for this video.")
    except NoTranscriptFound:
        print("❌ No transcripts found for the selected language.")
    except VideoUnavailable:
        print("❌ The video is unavailable. Please check the Video ID or URL.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()