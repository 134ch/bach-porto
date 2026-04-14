# Video Link Extractor (Vidlink.py)

This tool scans a folder of Markdown files, extracts video URLs (YouTube, Loom, Vimeo, etc.), and organizes them into a CSV file. It is particularly useful for cataloging course videos or lesson content.

## Prerequisites
- Python 3.x
- No external libraries required (uses `os`, `re`, `csv`, `pathlib`).

## Usage
1. Run the script: `python Vidlink.py`
2. Enter the input folder path containing your `.md` files (defaults to `output_md`).
3. Enter the desired output CSV filename (defaults to `video_links.csv`).
4. The script will process the files and generate a summary of modules and videos found.

## Features
- **Automatic Module Detection**: Extracts module numbers from filenames (e.g., "3. Introduction.md" becomes Module 3).
- **Platform Detection**: Identifies if a link is from YouTube, Loom, Vimeo, Wistia, Vidyard, or Streamable.
- **Title Extraction**: Automatically pulls the first `#` heading as the course/lesson title.
- **CSV Export**: Creates a clean spreadsheet with Module Number, Link, Title, and Source.
