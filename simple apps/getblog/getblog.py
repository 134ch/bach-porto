#!/usr/bin/env python3
"""
getblog.py

Downloads blog articles from a list of URLs and saves them as raw HTML
and cleaned text.

Features:
- CLI support for input file and output directory
- Progress bar using tqdm
- Session-based requests for efficiency
- URL slugification for safe filenames
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm

def slugify(url: str) -> str:
    """
    Turn a URL into a safe filename base.
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if not path:
        base = "index"
    else:
        base = path.split("/")[-1] or "index"

    safe = []
    for ch in base:
        if ch.isalnum() or ch in ("-", "_"):
            safe.append(ch)
        else:
            safe.append("_")
    result = "".join(safe)
    if not result:
        result = "page"
    return result

def extract_main_text(html: str) -> str:
    """
    Try to grab the main article text.
    Falls back to body text if no article or main tag exists.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try article tag first
    article = soup.find("article")
    if article is None:
        # Try main tag
        article = soup.find("main")
    if article is None:
        # Fall back to whole body
        article = soup.body or soup

    text = article.get_text("\n", strip=True)
    return text

def load_urls(file_path: str) -> list:
    """
    Load URLs from a text file.
    """
    path = Path(file_path)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def download_blog(url, session, output_dir, index, total):
    """
    Download a single blog post and save it.
    """
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        return False, str(exc)

    html = response.text
    base_name = f"{index:03d}_{slugify(url)}"

    # Save raw HTML
    html_path = output_dir / f"{base_name}.html"
    html_path.write_text(html, encoding="utf-8")

    # Save cleaned text
    text = extract_main_text(html)
    text_path = output_dir / f"{base_name}.txt"
    text_path.write_text(text, encoding="utf-8")

    return True, None

def main():
    parser = argparse.ArgumentParser(description="Download blog articles from a list of URLs.")
    parser.add_argument("--file", default="urls.txt", help="Path to the text file containing URLs.")
    parser.add_argument("--output", default="downloaded_blogs", help="Directory to save the downloaded articles.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds.")
    
    args = parser.parse_args()

    urls = load_urls(args.file)
    if not urls:
        print(f"No URLs found in {args.file}. Please provide a file with one URL per line.")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Starting download of {len(urls)} blogs into '{args.output}'...")
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    with tqdm(total=len(urls), desc="Downloading", unit="blog") as pbar:
        for i, url in enumerate(urls, start=1):
            success, error = download_blog(url, session, output_dir, i, len(urls))
            if not success:
                pbar.write(f"Error fetching {url}: {error}")
            pbar.update(1)
            time.sleep(args.delay)

    print("\nDownload complete!")

if __name__ == "__main__":
    main()
