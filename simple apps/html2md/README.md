# HTML to Markdown Converter (html2md.py)

Converts HTML files into clean Markdown. While it works generally, it contains specific logic to handle Skool-based rich text editors and assets.

## Prerequisites
```bash
pip install beautifulsoup4
```

## Usage
1. Run the script: `python html2md.py`
2. Specify the input folder containing `.html` files (defaults to `input_html`).
3. Specify the output folder for `.md` files (defaults to `output_md`).
4. The script will convert all files while preserving formatting and video embeds.

## Features
- **Video Embed Support**: Converts `<iframe>` embeds (YouTube, Loom, etc.) into Markdown video links.
- **Rich Text Handling**: Correctly processes headers, bold/italic text, lists (ordered/unordered), and blockquotes.
- **Image Preservation**: Detects and maintains Skool asset image links.
- **Clean Output**: Uses regex to strip excessive whitespace and normalize formatting.
