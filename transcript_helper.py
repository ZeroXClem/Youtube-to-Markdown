from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

def get_transcript_with_fallback(video_id, target_language='en'):
    """Attempts multiple methods to retrieve transcript with fallbacks."""
    try:
        # First try: Get transcript in target language
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get manual transcript first
        try:
            transcript = transcript_list.find_manually_created_transcript([target_language])
            return transcript.fetch()
        except NoTranscriptFound:
            pass
            
        # Try to get auto-generated transcript
        try:
            transcript = transcript_list.find_generated_transcript([target_language])
            return transcript.fetch()
        except NoTranscriptFound:
            pass
            
        # Try to get any available transcript and translate it
        try:
            transcript = transcript_list.find_transcript(transcript_list.transcript_data.keys())
            translated = transcript.translate(target_language)
            return translated.fetch()
        except Exception:
            pass
            
        # Final attempt: Get any available transcript
        available_transcripts = list(transcript_list.transcript_data.keys())
        if available_transcripts:
            transcript = transcript_list.find_transcript([available_transcripts[0]])
            return transcript.fetch()
            
        raise NoTranscriptFound(f'No transcript found for video {video_id}')
        
    except Exception as e:
        raise Exception(f'Failed to retrieve transcript: {str(e)}')