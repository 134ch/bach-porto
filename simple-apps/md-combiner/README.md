# Markdown Combiner (md_combiner.py)

A simple utility to merge multiple Markdown files into a single master document. Perfect for creating e-books, full course guides, or preparing content for bulk printing.

## Prerequisites
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Place your `.md` files in a folder named `output_md` and run:
```bash
python md_combiner.py
```

### Options
Specify custom paths and separators via command line:
```bash
python md_combiner.py --input my_chapters --output My_Ebook.md --separator "\n\n# NEXT CHAPTER\n\n"
```

### Command Line Arguments
- `--input`: Source directory of Markdown files (default: `output_md`).
- `--output`: Name of the combined file to create (default: `combined_output.md`).
- `--separator`: String inserted between each file's content (default: a horizontal rule `---`).

## Features
- **Natural Sorting**: Intelligently handles numbered files (e.g., `1.md`, `10.md`, `2.md` are correctly ordered as 1, 2, 10).
- **Customizable**: Allows you to change the transition between files.
- **Progress Tracking**: Shows a visual progress bar during the merge process.
- **Lossless**: Combines files with full UTF-8 encoding support.
