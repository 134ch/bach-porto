A specialized tool for converting Skool-specific HTML files into clean Markdown documents. It extracts titles, preserves formatting, and captures video embeds from popular platforms.

> [!NOTE]
> Designed to process the output from [**`skool-downloader`**](../skool-downloader/).

## Prerequisites
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Place your HTML files in a folder named `input_html` and run:
```bash
python html2md.py
```

### Options
You can specify custom input and output directories:
```bash
python html2md.py --input skool_downloads --output classroom_markdown
```

### Command Line Arguments
- `--input`: Directory containing HTML files to convert (default: `input_html`).
- `--output`: Directory where Markdown files will be saved (default: `output_md`).

## Features
- **Skool Optimized**: Targets specific CSS classes (like `skool-editor2`) used by Skool's rich text editor for high-fidelity extraction.
- **Video Capture**: Automatically identifies and lists embeds from YouTube, Loom, Vimeo, and Wistia.
- **Wait-Free Conversion**: Processes local files instantly with a visual progress bar.
- **Clean Formatting**: Recursively processes nested elements (bold, italic, links, lists) to produce readable Markdown.
