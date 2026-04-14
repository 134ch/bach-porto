# Markdown to PDF Converter (mdtopdf.py)

A professional tool to batch convert Markdown files into beautifully styled PDFs, optimized for course materials and guides. This tool is designed to work seamlessly with the output from `html2md` and `html2md-blog`.

## Prerequisites
```bash
pip install -r requirements.txt
```

> [!IMPORTANT]
> **WeasyPrint Dependency:** 
> WeasyPrint requires external libraries (GTK+ on Windows, or Cairo/Pango on macOS/Linux) to be installed on your system. If you see errors related to `cairo` or `gobject`, please refer to the [official installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html).

## Usage

### Basic Usage
Place your `.md` files in a folder named `output_md` and run:
```bash
python mdtopdf.py
```

### Options
Specify custom paths via command line:
```bash
python mdtopdf.py --input my_content --output final_pdfs
```

### Command Line Arguments
- `--input`: Source directory of Markdown files (default: `output_md`).
- `--output`: Destination directory for PDF files (default: `output_pdf`).

## Features
- **Premium Styling**: Includes a curated CSS theme with elegant headings, sidebar markers, and clear typography.
- **Page Numbering**: Automatically adds page numbers to the bottom-right of every page.
- **Video CTAs**: Converts Markdown video links into eye-catching dashed blocks that are easy to find and click.
- **Robust Layout**: Handles complex elements like tables, blockquotes, and fenced code blocks gracefully.
