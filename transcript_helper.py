import os

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

try:  # proxy support was added in youtube-transcript-api 1.0
    from youtube_transcript_api.proxies import WebshareProxyConfig, GenericProxyConfig
except Exception:  # pragma: no cover - older versions (< 1.0) lack proxy support
    WebshareProxyConfig = None
    GenericProxyConfig = None


def _build_proxy_config():
    """Return a proxy config built from environment variables, or ``None``.

    YouTube frequently blocks requests coming from cloud/datacenter IPs, which
    surfaces as an empty response ("no element found" / ``RequestBlocked``).
    Routing transcript requests through a proxy works around it. Configure ONE
    of the following sets of environment variables:

    * Webshare residential proxies (recommended for hosted apps):
      ``WEBSHARE_PROXY_USERNAME`` + ``WEBSHARE_PROXY_PASSWORD``
    * A generic HTTP/HTTPS proxy:
      ``YT_HTTP_PROXY`` and/or ``YT_HTTPS_PROXY``
    """
    if WebshareProxyConfig is not None:
        ws_user = os.environ.get("WEBSHARE_PROXY_USERNAME")
        ws_pass = os.environ.get("WEBSHARE_PROXY_PASSWORD")
        if ws_user and ws_pass:
            return WebshareProxyConfig(proxy_username=ws_user, proxy_password=ws_pass)

    if GenericProxyConfig is not None:
        http_url = os.environ.get("YT_HTTP_PROXY")
        https_url = os.environ.get("YT_HTTPS_PROXY")
        if http_url or https_url:
            return GenericProxyConfig(http_url=http_url, https_url=https_url)

    return None


def _build_api():
    """Return a configured ``YouTubeTranscriptApi`` instance (v1.x), or ``None``.

    Returns ``None`` on youtube-transcript-api < 1.0, which exposes the legacy
    static-method API and has no proxy support.
    """
    if hasattr(YouTubeTranscriptApi, "list_transcripts"):
        return None  # youtube-transcript-api < 1.0
    proxy_config = _build_proxy_config()
    if proxy_config is not None:
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()


def list_transcripts(video_id):
    """Return a ``TranscriptList`` for *video_id*.

    Works across youtube-transcript-api versions: v1.0 removed the
    ``YouTubeTranscriptApi.list_transcripts`` static method in favour of the
    instance method ``YouTubeTranscriptApi().list``. When a proxy is configured
    (see :func:`_build_proxy_config`) it is applied transparently here, and the
    transcripts it returns reuse the same proxied session for ``fetch()``.
    """
    api = _build_api()
    if api is None:
        return YouTubeTranscriptApi.list_transcripts(video_id)  # < 1.0
    return api.list(video_id)


def available_language_codes(video_id):
    """Return the list of available transcript language codes for *video_id*."""
    return [transcript.language_code for transcript in list_transcripts(video_id)]


def get_transcript_with_fallback(video_id, target_language='en'):
    """Attempts multiple methods to retrieve transcript with fallbacks."""
    try:
        transcript_list = list_transcripts(video_id)

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

        # Try to get any available transcript and translate it to the target language
        available = [transcript.language_code for transcript in transcript_list]
        if available:
            transcript = transcript_list.find_transcript(available)
            if target_language not in available and getattr(transcript, "is_translatable", False):
                try:
                    return transcript.translate(target_language).fetch()
                except Exception:
                    pass
            return transcript.fetch()

        raise Exception(f'No transcript found for video {video_id}')

    except Exception as e:
        raise Exception(f'Failed to retrieve transcript: {str(e)}')
