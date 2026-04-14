# Skool Downloader (skool_downloader.py)

A professional automation tool to download Skool community posts and lessons as HTML files. It handles authentication, dynamic content loading, and automated batch processing.

## Prerequisites
```bash
pip install -r requirements.txt
```

## Setup
You can avoid typing your credentials every time by creating a `.env` file in this folder:
```env
SKOOL_EMAIL=your@email.com
SKOOL_PASSWORD=your_password
```

## Usage

### Interactive Mode
Simply run the script and follow the prompts:
```bash
python skool_downloader.py
```

### Automated Batch Mode
Provide a text file with one URL per line:
```bash
python skool_downloader.py --file urls.txt --output my_course_files --headless
```

### Command Line Arguments
- `--email`: Your Skool email.
- `--password`: Your Skool password.
- `--file`: Path to a text file containing URLs to download.
- `--output`: Directory where HTML files will be saved (default: `skool_downloads`).
- `--headless`: Run the browser in the background (no window will open).
- `--profile`: Path to an existing Chrome user profile to reuse login sessions.

## Features
- **Smart Waiting**: Verifies content is actually rendered before saving.
- **Auto-Scroll**: Triggers lazy-loading of images and embedded content.
- **Headless Support**: Run automation silently in the background.
- **Error Recovery**: Automatic retries for redirects or slow-loading pages.
