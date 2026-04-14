# Markdown Combiner (md_combiner.py)

A simple utility to merge many Markdown files into one large document. Perfect for creating "Master" files or e-books from individual lessons.

## Prerequisites
- Python 3.x
- Uses `tkinter` (usually bundled with Python on Windows).

## Usage
1. Run the script: `python md_combiner.py`
2. A folder picker window will open. Select the folder containing your `.md` files.
3. The script will sort the files naturally (1, 2, 10 instead of 1, 10, 2) and combine them.
4. The result is saved as `combined_output.md` in the same folder.

## Features
- **Natural Sorting**: Correctly orders numbered files.
- **Visual Separators**: Automatically adds `---` (horizontal rules) between files.
- **GUI Selection**: Easy-to-use folder picker.
