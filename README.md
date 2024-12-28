# 🎥 YouTube to Markdown Converter 📝

Convert YouTube video transcripts into easily readable Markdown format! This Streamlit app allows you to download and format YouTube video transcripts with just a few clicks.

## 🌟 Features

- 🔗 Support for YouTube video URLs and IDs
- 🌍 Multiple language support for transcripts
- 📊 Export options: Markdown, Plain Text, and JSON
- 🎨 Dark mode toggle for better user experience
- 📑 Automatic paragraph formatting for improved readability
- 👁️ Transcript preview functionality

## 🛠️ Installation

### Recommended Setup

1. Create and activate a virtual environment:
   ```bash
   # Using conda (recommended)
   conda create -n youtube-md python=3.10
   conda activate youtube-md

   # OR using venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install UV (recommended for faster package installation):
   ```bash
   pip install uv
   ```

3. Clone this repository:
   ```bash
   git clone https://github.com/ZeroXClem/YouTube-to-Markdown.git
   ```

4. Navigate to the project directory:
   ```bash
   cd YouTube-to-Markdown
   ```

5. Install dependencies (choose one method):
   ```bash
   # Using UV (recommended)
   uv pip install -r requirements.txt

   # OR using pip
   pip install -r requirements.txt
   ```

## 🚀 Usage

1. Run the Streamlit app:
   ```
   streamlit run youtube-transcript-downloader2.py
   ```
2. Open your web browser and go to the provided local URL (usually `http://localhost:8501`)
3. Enter a YouTube video URL or ID
4. Select your preferred options (file name, save path, export format)
5. Click "Download Transcript"

## 🖥️ CLI Version

A command-line interface version is also available for users who prefer terminal-based operations:

1. Run the CLI version:
   ```
   python youtube_transcript_cli.py
   ```
2. Follow the interactive prompts to:
   - Enter YouTube video URL or ID
   - Select transcript language
   - Choose export format
   - Specify output filename

The CLI version provides the same core functionality as the web interface but in a terminal-friendly format.

6. View the transcript preview and use the download button to save the formatted transcript

## 📁 Project Structure

```
.
├── .git
├── requirements.txt
├── versions
└── youtube-transcript-downloader2.py
```

- `requirements.txt`: List of Python packages required for the project
- `versions/`: Directory containing different versions of the script
- `youtube-transcript-downloader2.py`: Main Streamlit application script

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/ZeroXClem/YouTube-to-Markdown/issues).

## 📜 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 👏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the awesome web app framework
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for making transcript retrieval easy

---

Made with ❤️ by [ZeroXClem]
