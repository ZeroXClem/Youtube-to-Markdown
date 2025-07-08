# 🎥 YouTube to Markdown Converter 📝

This project provides both a web-based (Streamlit) and command-line (CLI) tools to convert YouTube video transcripts into easily readable Markdown, Plain Text, or JSON formats.

## 🌟 Features

- 🔗 Supports YouTube video URLs, IDs, and **Playlists** (batch processing CLI).
- 🌍 Multiple language support for transcripts.
- 📊 Export options: Markdown, Plain Text, and JSON.
- 📁 **Batch processing** from a file of URLs/IDs (`batch_processing_yt.py`).
- 🎨 Dark mode toggle for better UX (Streamlit app).
- 📑 Automatic paragraph formatting for readability.
- 👁️ Transcript preview (Streamlit app).
- 📂 User-specified output directory.
- ✅ *Sanitized, Linux-friendly, kebab-case filename generation* based on video title.

---

## 🛠️ Installation (Web App and CLIs)

### Recommended Setup

1️⃣ Create and activate a virtual environment:

```bash
# Conda (recommended)
conda create -n youtube-md python=3.10
conda activate youtube-md

# OR using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2️⃣ Install UV (recommended for faster installation):

```bash
pip install uv
```

3️⃣ Clone this repository:

```bash
git clone https://github.com/ZeroXClem/YouTube-to-Markdown.git
cd YouTube-to-Markdown
```

4️⃣ Install dependencies:

```bash
# Using UV
uv pip install -r requirements.txt

# Or pip
pip install -r requirements.txt
```

> **Note:** If any issues arise, install these individually: `youtube-transcript-api`, `yt-dlp`, `requests`.

---

## 🚀 Usage (Web App)

Run the Streamlit app:

```bash
streamlit run youtube-transcript-downloader2.py
```

Then in your browser:

- Enter a YouTube video URL or ID.
- Select your language and format.
- Click **Download Transcript**.

---

## 🖥️ Usage (CLI: Interactive Single Video)

### `youtube_cli.py`

1️⃣ Run:

```bash
python youtube_cli.py
```

2️⃣ Follow prompts to:

- Enter video URL/ID.
- Choose transcript language.
- Pick export format (md, txt, json).
- Specify output directory.

✅ Features:
- Step-by-step guided experience.
- Auto-formatted paragraphs.
- Clean **Linux-friendly**, kebab-case, ASCII-only filename generation.

---

## 🖥️ Usage (CLI: Batch Processing)

### `batch_processing_yt.py`

For multiple videos or playlists:

```bash
python batch_processing_yt.py <input> [-l language] [-f format] [-o output_directory]
```

**Arguments:**

- `input` (required): Single video URL/ID, playlist URL, or text file with multiple URLs/IDs.
- `-l`, `--language`: Language code (default: `en`).
- `-f`, `--format`: Output (`txt`, `md`, `json`, default: `txt`).
- `-o`, `--output`: Output directory (default: current).

**Examples:**

✅ Single Video:

```bash
python batch_processing_yt.py https://www.youtube.com/watch?v=dQw4w9WgXcQ -l en -f md -o my_transcripts
```

✅ Playlist:

```bash
python batch_processing_yt.py "https://www.youtube.com/playlist?list=PLQVv..." -l en -f json -o playlist_transcripts
```

✅ From a File:

`video_list.txt` contents:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
another_video_id
https://www.youtube.com/playlist?list=PLQVv...
```

Run:

```bash
python batch_processing_yt.py video_list.txt -l fr -f md -o my_transcripts
```

✅ Help:

```bash
python batch_processing_yt.py --help
```

---

## 📁 Project Structure

```
├── .git/
├── requirements.txt
├── transcript_helper.py
├── versions/
├── batch_processing_yt.py
├── youtube_cli.py
└── youtube-transcript-downloader2.py
```

- `requirements.txt`: Python dependencies.
- `transcript_helper.py`: Shared helper functions.
- `batch_processing_yt.py`: CLI for batch processing.
- `youtube_cli.py`: Interactive CLI with Linux-friendly filename sanitation.
- `youtube-transcript-downloader2.py`: Streamlit web app.

---

## 🤝 Contributing

Contributions, issues, and feature requests welcome!  
Check the [issues page](https://github.com/ZeroXClem/YouTube-to-Markdown/issues).

---

## 📜 License

MIT License. See [LICENSE](https://choosealicense.com/licenses/mit/).

---

## 👏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the app framework.
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for reliable video and playlist info.

---

Made with ❤️ by [ZeroXClem]

