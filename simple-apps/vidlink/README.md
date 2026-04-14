# Video Link Extractor (vidlink.py)

Scans a directory of Markdown files and extracts all video URLs into a clean CSV file for asset auditing or bulk downloading.

## Prerequisites
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Place your `.md` files (e.g., from `html2md` or `html2md-blog`) in a folder named `output_md` and run:
```bash
python vidlink.py
```

### Options
Specify custom paths via command line:
```bash
python vidlink.py --input my_content --output links.csv
```

### Command Line Arguments
- `--input`: Source directory of Markdown files (default: `output_md`).
- `--output`: Name of the CSV file to generate (default: `video_links.csv`).

## Features
- **Broad Detection**: Identifies video links from YouTube, Loom, Vimeo, Wistia, Vidyard, and Streamable.
- **Auto-Indexing**: Detects module numbers from filenames to keep your video list in the correct order.
- **Titled Lists**: Pulls the first `#` heading from your Markdown as the lesson title.
- **Progress Tracking**: Shows a visual progress bar while scanning large directories.
 Introduction.md" becomes Module 3).
- **Platform Detection**: Identifies if a link is from YouTube, Loom, Vimeo, Wistia, Vidyard, or Streamable.
- **Title Extraction**: Automatically pulls the first `#` heading as the course/lesson title.
- **CSV Export**: Creates a clean spreadsheet with Module Number, Link, Title, and Source.
