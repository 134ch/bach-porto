#!/usr/bin/env python3
"""
html2md.py

Converts Skool-specific HTML files into clean Markdown documents.
Automates extraction of titles, video embeds (YouTube, Loom, Vimeo, Wistia),
and formatted text.
"""

import os
import re
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

def clean_text(text):
    """Clean up text content, removing excessive whitespace."""
    if not text:
        return ""
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def extract_video_embeds(soup):
    """Extract video embed URLs (YouTube, Loom, Vimeo, Wistia, etc.)"""
    videos = []
    iframes = soup.find_all('iframe')
    for iframe in iframes:
        src = iframe.get('src', '')
        # Filter out non-video iframes (like Stripe or social widgets)
        if any(domain in src for domain in ['youtube.com', 'loom.com', 'vimeo.com', 'wistia']):
            videos.append(src)
    return videos

def process_element(element):
    """Recursively convert HTML elements to Markdown."""
    if element.name is None:  # Text node
        return element.string if element.string else ""
    
    markdown = ""
    
    # Headings
    if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(element.name[1])
        text = element.get_text(strip=True)
        markdown = f"\n\n{'#' * level} {text}\n\n"
    
    # Paragraphs and text formatting
    elif element.name == 'p':
        text = ""
        for child in element.children:
            text += process_element(child)
        markdown = f"{clean_text(text)}\n\n"
    
    elif element.name in ['strong', 'b']:
        markdown = f"**{element.get_text(strip=True)}**"
    
    elif element.name in ['em', 'i']:
        markdown = f"*{element.get_text(strip=True)}*"
    
    elif element.name == 'a':
        link_text = element.get_text(strip=True)
        link_url = element.get('href', '')
        markdown = f"[{link_text}]({link_url})"
    
    elif element.name == 'code':
        markdown = f"`{element.get_text(strip=True)}`"
    
    # Lists
    elif element.name in ['ul', 'ol']:
        prefix = "- " if element.name == 'ul' else "1. "
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            li_prefix = prefix if element.name == 'ul' else f"{i}. "
            li_text = "".join(process_element(c) for c in li.children).strip()
            markdown += f"{li_prefix}{li_text}\n"
        markdown += "\n"
    
    # Structural elements
    elif element.name == 'hr':
        markdown = "\n---\n\n"
    
    elif element.name == 'blockquote':
        text = element.get_text(strip=True)
        markdown = "\n".join([f"> {line}" for line in text.split('\n') if line.strip()]) + "\n\n"
    
    elif element.name == 'pre':
        markdown = f"\n```\n{element.get_text(strip=True)}\n```\n\n"
    
    elif element.name == 'img':
        src = element.get('src', '')
        alt = element.get('alt', 'Image')
        if src:
            markdown = f"\n![{alt}]({src})\n\n"
    
    # Generic container handling (recurse into children)
    else:
        for child in element.children:
            markdown += process_element(child)
            
    return markdown

def extract_main_content(soup):
    """Target Skool-specific editors or fallback content areas."""
    # Preferred Skool editor container
    main = soup.find('div', class_=lambda x: x and 'skool-editor2' in x)
    if not main:
        main = soup.find('article') or soup.find('main') or soup.body
    
    if not main:
        return ""

    markdown = ""
    for child in main.children:
        if child.name:
            markdown += process_element(child)
    return clean_text(markdown)

def extract_title(soup):
    """Find the lesson title using Skool classes or the <title> tag."""
    title_elem = soup.find('div', class_=lambda x: x and 'ModuleTitle' in x)
    if title_elem:
        return title_elem.get_text(strip=True)
    
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        # Clean common Skool title suffixes
        title = re.split(r'[·|-]', title)[0].strip()
        return title
    
    return "Untitled Lesson"

def convert(html_content):
    """Assemble the Markdown document."""
    soup = BeautifulSoup(html_content, 'html.parser')
    title = extract_title(soup)
    videos = extract_video_embeds(soup)
    content = extract_main_content(soup)
    
    doc = f"# {title}\n\n"
    if videos:
        for vid in videos:
            label = "Video"
            if "youtube.com" in vid: label = "YouTube"
            elif "loom.com" in vid: label = "Loom"
            doc += f"[{label} Embed]({vid})\n\n"
    
    doc += content
    return doc

def main():
    parser = argparse.ArgumentParser(description="Convert Skool HTML files to Markdown.")
    parser.add_argument("--input", default="input_html", help="Directory containing HTML files.")
    parser.add_argument("--output", default="output_md", help="Directory for the generated Markdown files.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input directory '{args.input}' not found.")
        return

    output_path.mkdir(parents=True, exist_ok=True)
    html_files = list(input_path.glob("*.html"))
    
    if not html_files:
        print("No HTML files found in the input directory.")
        return

    print(f"Converting {len(html_files)} files from '{args.input}' to '{args.output}'...")
    
    for html_file in tqdm(html_files, desc="Converting", unit="file"):
        try:
            content = html_file.read_text(encoding="utf-8")
            markdown = convert(content)
            
            output_file = output_path / (html_file.stem + ".md")
            output_file.write_text(markdown, encoding="utf-8")
        except Exception as e:
            tqdm.write(f"Error processing {html_file.name}: {e}")

    print("\nConversion complete!")

if __name__ == "__main__":
    main()