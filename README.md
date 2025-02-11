# 🎥 YouTube to Markdown Converter 📝

This project provides both a web-based (Streamlit) and two command-line (CLI) tools to convert YouTube video transcripts into easily readable Markdown, Plain Text, or JSON formats.

## 🌟 Features

-   🔗 Support for YouTube video URLs, IDs, and **Playlists** (batch processing CLI).
-   🌍 Multiple language support for transcripts.
-   📊 Export options: Markdown, Plain Text, and JSON.
-   📁 **Batch processing** from a file containing a list of URLs/IDs (`batch_processing_yt.py`).
-   🎨 Dark mode toggle for better user experience (Streamlit app).
-   📑 Automatic paragraph formatting for improved readability.
-   👁️ Transcript preview functionality (Streamlit app).
-   📂 User-specified output directory.
-   ✅ Automatic, sanitized filename generation based on video title.

## 🛠️ Installation (Both Web App and CLIs)

### Recommended Setup

1.  Create and activate a virtual environment:

    ```bash
    # Using conda (recommended)
    conda create -n youtube-md python=3.10
    conda activate youtube-md

    # OR using venv
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2.  Install UV (recommended for faster package installation):

    ```bash
    pip install uv
    ```

3.  Clone this repository:

    ```bash
    git clone https://github.com/ZeroXClem/YouTube-to-Markdown.git
    ```

4.  Navigate to the project directory:

    ```bash
    cd YouTube-to-Markdown
    ```

5.  Install dependencies (choose one method):
    *Note: requirements may be slightly different for each tool. If you encounter issues, try installing `youtube-transcript-api`, `yt-dlp`, and `requests` individually.*

    ```bash
    # Using UV (recommended)
    uv pip install -r requirements.txt

    # OR using pip
    pip install -r requirements.txt
    ```

## 🚀 Usage (Web App)

1.  Run the Streamlit app:

    ```bash
    streamlit run youtube-transcript-downloader2.py
    ```

2.  Open your web browser and go to the provided local URL (usually `http://localhost:8501`).

3.  Enter a YouTube video URL or ID.

4.  Select your preferred options (language, export format).

5.  Click "Download Transcript".

## 🖥️ Usage (Easiest CLI Version - Interactive)

The original CLI, `youtube_cli.py`, provides a step-by-step interactive experience for downloading single transcripts.

1.  Run the CLI:

    ```bash
    python youtube_cli.py
    ```

2.  Follow the on-screen prompts to enter the video URL/ID, select the language, choose the export format, and specify the output directory.

## 🖥️ Usage (CLI Version - Batch Processing)

The `batch_processing_yt.py` CLI offers batch processing capabilities, using command-line arguments for a more streamlined workflow.

1.  Run the CLI version with the desired options:

    ```bash
    python batch_processing_yt.py <input> [-l language] [-f format] [-o output_directory]
    ```

2.  **Arguments:**

    *   `input`:  This is a **required** argument. It can be:
        *   A single YouTube video URL or ID.
        *   A YouTube playlist URL.
        *   The path to a text file containing a list of video URLs/IDs (one per line). The file can *also* contain playlist URLs, which will be expanded.

    *   `-l` or `--language`:  The transcript language code (e.g., `en`, `fr`, `es`).  Defaults to `en`.

    *   `-f` or `--format`:  The output format (`txt`, `md`, or `json`).  Defaults to `txt`.

    *   `-o` or `--output`: The output directory.  Defaults to the current directory (`.`).

3.  **Examples:**

    *   **Single Video:**

        ```bash
        python batch_processing_yt.py https://www.youtube.com/watch?v=dQw4w9WgXcQ -l en -f md -o my_transcripts
        ```

    *   **Playlist:**

        ```bash
        python batch_processing_yt.py https://www.youtube.com/playlist?list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v -l en -f json -o playlist_transcripts
        ```

    *   **File with URLs/IDs:**

        Create a file named `video_list.txt` with the following content (or any list of URLs/IDs):

        ```
        https://www.youtube.com/watch?v=dQw4w9WgXcQ
        another_video_id
        https://www.youtube.com/playlist?list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v
        ```

        Then run:

        ```bash
        python batch_processing_yt.py video_list.txt -l fr -f md -o my_transcripts
        ```

    *   **Help:**

        ```bash
        python batch_processing_yt.py --help
        ```

## 📁 Project Structure

```
├── .git/
├── requirements.txt
├── transcript_helper.py
├── versions/
├── batch_processing_yt.py      <-- Batch processing CLI
├── youtube_cli.py   <-- Interactive CLI
└── youtube-transcript-downloader2.py  <-- Streamlit app
```

-   `requirements.txt`: List of Python packages required for the project.
-   `transcript_helper.py`: Helper functions for transcript processing and formatting.
-   `versions/`: Directory containing different versions of the script (optional).
-   `batch_processing_yt.py`: Command-line interface for batch processing.
-   `youtube_cli.py`: Command-line interface for interactive single downloads.
-   `youtube-transcript-downloader2.py`: Main Streamlit application script.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/ZeroXClem/YouTube-to-Markdown/issues).

## 📜 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 👏 Acknowledgements

-   [Streamlit](https://streamlit.io/) for the awesome web app framework.
-   [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for making transcript retrieval easy.
-    [yt-dlp](https://github.com/yt-dlp/yt-dlp) A fork of youtube-dl for reliable video and playlist information extraction.

---

Made with ❤️ by [ZeroXClem]

