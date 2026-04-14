A professional automation tool to download Skool community posts and lessons as HTML files. It handles authentication, dynamic content loading, and automated batch processing.

> [!TIP]
> **Next Step:** After downloading, use [**`html2md`**](../html2md/) to convert these HTML files into clean Markdown.

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

---

> [!TIP]
> **Pro Tip: Link Collection**
> To quickly gather all classroom or post URLs from a community, use the [Link Grabber](https://chromewebstore.google.com/detail/link-grabber/caodelkhipncidmoebgbbeemedohcdma) Chrome extension. It can extract every link on the page in seconds, which you can then paste into the downloader or save to a `urls.txt` file.

> [!NOTE]
> **Output Style**
> The downloaded HTML files are "raw" and may appear visually broken (ugly) when opened in a browser because external stylesheets are not saved. The primary goal of this tool is to reliably capture **all text, structure, and video links** for further conversion (e.g., to Markdown or PDF).
