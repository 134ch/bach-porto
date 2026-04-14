# Markdown to PDF (mdtopdf.py)

Converts Markdown files into beautifully styled PDF documents. It includes a custom design system with margins, typography, and special blocks for video links.

## Prerequisites
```bash
pip install markdown weasyprint
```

## Usage
1. Run the script: `python mdtopdf.py`
2. Enter the input folder (defaults to `output_md`).
3. Enter the output folder (defaults to `output_pdf`).
4. The script will generate styled PDFs for every Markdown file found.

## Features
- **Premium Styling**: Includes a built-in CSS theme with modern fonts and clean layout.
- **Video Callouts**: Specifically transforms `[Video: Platform](URL)` links into a highlighted, clickable box with a 🎥 icon.
- **Full Support**: Handles tables, code blocks (with syntax highlighting), and images.
