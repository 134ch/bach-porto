#!/usr/bin/env python3
"""
vidlink.py

Scans a directory of Markdown files to extract and catalog video links
(YouTube, Loom, Vimeo, etc.) into a single CSV or text file.
"""

import os
import re
import csv
import argparse
from pathlib import Path
from tqdm import tqdm

def extract_module_number(filename: str):
    """Extract the numeric index from the start of the filename."""
    match = re.match(r'^(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def extract_first_heading(md_content: str) -> str:
    """Find the first # heading in the file."""
    for line in md_content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "No Title"

def detect_video_source(url: str) -> str:
    """Identify the platform host for a given URL."""
    u = url.lower()
    if 'youtube.com' in u or 'youtu.be' in u: return 'YouTube'
    if 'loom.com' in u: return 'Loom'
    if 'vimeo.com' in u: return 'Vimeo'
    if 'wistia' in u: return 'Wistia'
    if 'vidyard' in u: return 'Vidyard'
    if 'streamable' in u: return 'Streamable'
    return 'Other'

def extract_video_links(md_content: str) -> list:
    """Extract all video links using multiple regex patterns."""
    links = []
    
    # 1. Custom [Video: ...](URL) patterns
    links.extend(re.findall(r'\[Video:?\s*[^\]]*\]\(([^\)]+)\)', md_content))
    
    # 2. Markdown links that reference video domains
    domains = r'youtube\.com|youtu\.be|loom\.com|vimeo\.com|wistia|vidyard|streamable'
    links.extend(re.findall(rf'\[[^\]]+\]\((https?://[^\)]*(?:{domains})[^\)]+)\)', md_content))
    
    # 3. Bare URLs
    links.extend(re.findall(rf'(https?://(?:www\.)?(?:{domains})/[^\s\)]+)', md_content))
    
    # Deduplicate while preserving order
    seen = set()
    return [l for l in links if not (l in seen or seen.add(l))]

def process_files(input_dir: str):
    """Iterate through MD files and build the dataset."""
    input_path = Path(input_dir)
    md_files = sorted(list(input_path.glob("*.md")))
    results = []
    
    if not md_files:
        return results

    for md_file in tqdm(md_files, desc="Scanning", unit="file"):
        module_num = extract_module_number(md_file.name)
        # If no number, we still process but keep it as a string
        idx = module_num if module_num is not None else 999
        
        try:
            content = md_file.read_text(encoding="utf-8")
            title = extract_first_heading(content)
            links = extract_video_links(content)
            
            if not links:
                results.append({
                    'module': idx,
                    'display': str(idx),
                    'link': '',
                    'title': title,
                    'source': 'N/A'
                })
                continue
                
            for i, link in enumerate(links, 1):
                display = str(idx) if len(links) == 1 else f"{idx}.{i}"
                results.append({
                    'module': idx,
                    'display': display,
                    'link': link,
                    'title': title,
                    'source': detect_video_source(link)
                })
        except Exception as e:
            tqdm.write(f"Error reading {md_file.name}: {e}")
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Extract video links from Markdown files.")
    parser.add_argument("--input", default="output_md", help="Directory containing .md files.")
    parser.add_argument("--output", default="video_links.csv", help="Output CSV filename.")
    args = parser.parse_args()

    ipath = Path(args.input)
    if not ipath.exists():
        ipath.mkdir(parents=True, exist_ok=True)
        sample = ipath / "001_sample.md"
        sample.write_text("# Sample Page\n\n[Video: YouTube](https://youtube.com)", encoding="utf-8")
        print(f"Created input directory '{args.input}' with a sample file.")

    data = process_files(args.input)
    if not data:
        print("No video links found.")
        return

    # Sort primarily by module number
    data.sort(key=lambda x: (x['module'], x['display']))
    
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Video URL', 'Lesson Title', 'Platform'])
        for item in data:
            writer.writerow([item['display'], item['link'], item['title'], item['source']])

    v_count = sum(1 for d in data if d['link'])
    print(f"\nDone! Extracted {v_count} video(s) into '{args.output}'.")

if __name__ == "__main__":
    main()