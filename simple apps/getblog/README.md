# Blog Scraper (getblog.py)

A specialized scraper designed to download articles from a list of URLs. It saves both the full HTML for archival purposes and a cleaned text version for easy reading or further processing.

## Prerequisites
```bash
pip install requests beautifulsoup4
```

## Usage
1. Open `getblog.py` in an editor.
2. Update the `URLS` list with the links you want to download.
3. Run the script: `python getblog.py`
4. The articles will be saved in a new folder named `pga_articles/`.

## Features
- **Dual Output**: Saves `.html` (original) and `.txt` (cleaned text) for every URL.
- **Slugified Filenames**: Automatically converts URL paths into safe, readable filenames.
- **Polite Scraping**: Includes a 1-second delay between requests to avoid server strain.
- **Deep Extraction**: Targets `<article>` or `<main>` tags first to ensure content quality over page clutter.
