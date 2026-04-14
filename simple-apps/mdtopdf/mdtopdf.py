#!/usr/bin/env python3
"""
mdtopdf.py

Converts Markdown files into professional, styled PDF documents.
Uses WeasyPrint for high-quality PDF rendering and supports custom CSS.
"""

import re
import argparse
import markdown
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from tqdm import tqdm

def create_pdf_styles():
    """Returns a curated CSS string for professional PDF output."""
    return """
    @page {
        size: A4;
        margin: 2cm;
        @bottom-right {
            content: counter(page);
            font-size: 9pt;
            color: #95a5a6;
        }
    }
    
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        margin: 0 auto;
    }
    
    h1 {
        font-size: 28pt;
        font-weight: bold;
        margin-top: 0;
        margin-bottom: 30px;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 12px;
    }
    
    h2 {
        font-size: 20pt;
        font-weight: bold;
        margin-top: 40px;
        margin-bottom: 15px;
        color: #34495e;
        border-left: 5px solid #3498db;
        padding-left: 15px;
    }
    
    h3 {
        font-size: 16pt;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 12px;
        color: #2c3e50;
    }
    
    p { margin-bottom: 15px; text-align: left; }
    
    a { color: #3498db; text-decoration: none; }
    
    ul, ol { margin-bottom: 20px; padding-left: 30px; }
    li { margin-bottom: 8px; }
    
    code {
        background-color: #f8f9fa;
        padding: 2px 5px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        border: 1px solid #e9ecef;
    }
    
    pre {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
        white-space: pre-wrap;
    }
    
    blockquote {
        margin: 25px 0;
        padding: 15px 25px;
        background-color: #fdfdfd;
        border-left: 5px solid #ecf0f1;
        font-style: italic;
        color: #7f8c8d;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 30px auto;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 25px;
    }
    
    table th, table td {
        border: 1px solid #dee2e6;
        padding: 12px;
    }
    
    table th {
        background-color: #f8f9fa;
        font-weight: bold;
    }
    
    .video-link {
        display: block;
        padding: 20px;
        background-color: #f0f7fa;
        border: 2px dashed #3498db;
        border-radius: 10px;
        margin: 25px 0;
        text-align: center;
        text-decoration: none;
    }
    
    .video-link strong { color: #2980b9; display: block; margin-bottom: 5px; }
    .video-link small { color: #7f8c8d; font-size: 0.85em; }
    """

def preprocess_markdown(md_content):
    """Converts custom video tags into styled HTML blocks."""
    pattern = r'\[Video:?\s*([^\]]+)\]\(([^\)]+)\)'
    def replace_video(match):
        platform, url = match.groups()
        return f'\n<a class="video-link" href="{url}" target="_blank"><strong>🎥 Watch Video on {platform}</strong> <small>{url}</small></a>\n'
    return re.sub(pattern, replace_video, md_content)

def convert_md_to_pdf(md_path, pdf_path):
    """Processes a single MD file and renders it to PDF."""
    try:
        content = md_path.read_text(encoding='utf-8')
        content = preprocess_markdown(content)
        
        html_body = markdown.markdown(content, extensions=[
            'extra', 'codehilite', 'nl2br', 'sane_lists', 'toc'
        ])
        
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="utf-8"></head>
        <body>{html_body}</body>
        </html>
        """
        
        font_config = FontConfiguration()
        css = CSS(string=create_pdf_styles(), font_config=font_config)
        HTML(string=full_html).write_pdf(
            pdf_path,
            stylesheets=[css],
            font_config=font_config
        )
        return True
    except Exception as e:
        tqdm.write(f"Error converting {md_path.name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Batch convert Markdown files to PDF.")
    parser.add_argument("--input", default="output_md", help="Directory of .md files.")
    parser.add_argument("--output", default="output_pdf", help="Output directory for PDFs.")
    args = parser.parse_args()

    ipath = Path(args.input)
    opath = Path(args.output)
    
    # Create input directory and a sample file if it doesn't exist
    if not ipath.exists():
        ipath.mkdir(parents=True, exist_ok=True)
        sample = ipath / "001_sample.md"
        sample.write_text("# Sample Page\n\nThis is a sample markdown file.\n\n[Video: YouTube](https://youtube.com)", encoding="utf-8")
        print(f"Created input directory '{args.input}' with a sample file.")

    opath.mkdir(parents=True, exist_ok=True)
    md_files = sorted(list(ipath.glob("*.md")))
    
    if not md_files:
        print("No Markdown files found.")
        return

    print(f"Converting {len(md_files)} files into PDF...")
    success = 0
    for md_file in tqdm(md_files, desc="Converting", unit="file"):
        pdf_file = opath / (md_file.stem + ".pdf")
        if convert_md_to_pdf(md_file, pdf_file):
            success += 1

    print(f"\nDone! Successfully created {success} PDF(s) in '{args.output}'.")

if __name__ == "__main__":
    main()