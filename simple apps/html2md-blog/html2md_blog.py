#!/usr/bin/env python3
"""
html2md_blog.py

Specialized HTML to Markdown converter for blog articles (PGA specifically).
Features:
- Fixes specific text encoding issues (mojibake).
- Converts images and videos into descriptive text labels with URLs.
- Uses markdownify for robust HTML conversion.
- CLI support and progress tracking.
"""

import re
import argparse
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from tqdm import tqdm

def fix_text_encoding(text: str) -> str:
    """
    Fix mojibake like donâ€™t -> don't, etc.
    """
    replacements = {
        "â€™": "'",   # apostrophe
        "â€˜": "'",   # opening single quote
        "â€œ": '"',   # opening double quote
        "â€ ": '"',   # closing double quote
        "â€“": "-",   # en dash
        "â€”": "-",   # em dash
        "â€¦": "...", # ellipsis
        "Â\xa0": " ", # non breaking space
        "Â ": " ",    # stray Â
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Clean up extra spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text

def convert_figure_to_text(fig, soup):
    """
    Turn a <figure> containing a video or image into a simple <p> node:
    "Caption" (URL = https://...)
    """
    iframe = fig.find("iframe")
    img = fig.find("img")

    if iframe is not None:
        url = iframe.get("src", "").strip()
        caption = iframe.get("title") or "video"
        caption = caption.strip() or "video"
        text = f"\"{caption}\" (URL = {url})"
    elif img is not None:
        url = img.get("src", "").strip()
        figcaption = fig.find("figcaption")
        if figcaption and figcaption.get_text(strip=True):
            caption = figcaption.get_text(strip=True)
        else:
            caption = img.get("alt") or "picture"
        caption = caption.strip() or "picture"
        text = f"\"{caption}\" (URL = {url})"
    else:
        return

    new_p = soup.new_tag("p")
    new_p.string = text
    fig.replace_with(new_p)

def convert_inline_img_to_text(img, soup):
    """Handle <img> tags not inside <figure>."""
    url = img.get("src", "").strip()
    caption = img.get("alt") or "picture"
    caption = caption.strip() or "picture"
    text = f"\"{caption}\" (URL = {url})"

    new_p = soup.new_tag("p")
    new_p.string = text
    img.replace_with(new_p)

def extract_article_html(html: str) -> str:
    """Extract and clean the main blog article HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Target PGA blog selectors
    article_richtext = soup.select_one("article .blogstyling") or soup.select_one(".blogstyling")
    
    if article_richtext is None:
        return ""

    # Clone for mutation
    work_soup = BeautifulSoup(str(article_richtext), "html.parser")

    for tag in work_soup(["script", "style"]):
        tag.decompose()

    for fig in work_soup.find_all("figure"):
        convert_figure_to_text(fig, work_soup)

    for img in work_soup.find_all("img"):
        convert_inline_img_to_text(img, work_soup)

    for embed_div in work_soup.select("div.w-embed"):
        embed_div.decompose()

    return "".join(str(child) for child in work_soup.contents)

def html_to_markdown(html: str) -> str:
    """Main conversion pipeline."""
    article_html = extract_article_html(html)
    if not article_html:
        return ""

    markdown = md(
        article_html,
        heading_style="ATX",
        strip=["span"],
    )

    markdown = fix_text_encoding(markdown)
    return markdown.strip() + "\n"

def main():
    parser = argparse.ArgumentParser(description="Specialized Blog HTML to Markdown converter.")
    parser.add_argument("--input", default="pga_articles", help="Input directory of HTML files.")
    parser.add_argument("--output", default="pga_markdown", help="Output directory for MD files.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input directory '{args.input}' not found.")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)
    html_files = sorted(input_path.glob("*.html"))

    if not html_files:
        print(f"No .html files found in {args.input}")
        return

    print(f"Processing {len(html_files)} blog articles...")

    for path in tqdm(html_files, desc="Converting", unit="art"):
        try:
            html = path.read_text(encoding="utf-8", errors="ignore")
            markdown = html_to_markdown(html)

            if not markdown.strip():
                continue

            out_path = output_path / (path.stem + ".md")
            out_path.write_text(markdown, encoding="utf-8")
        except Exception as e:
            tqdm.write(f"Error converting {path.name}: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()
