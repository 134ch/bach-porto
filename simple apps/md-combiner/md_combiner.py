#!/usr/bin/env python3
"""
md_combiner.py

Merges multiple Markdown files into a single master document.
Supports natural sorting (001, 002, etc.) and custom separators.
"""

import re
import argparse
from pathlib import Path
from tqdm import tqdm

def natural_sort_key(filename: str):
    """Sort strings containing numbers in the way humans expect."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', filename)]

def combine_md_files(input_dir, output_file, separator="\n\n---\n\n"):
    """Reads all MD files in a directory and writes them to a single file."""
    ipath = Path(input_dir)
    md_files = sorted([f for f in ipath.glob("*.md")], key=lambda x: natural_sort_key(x.name))

    if not md_files:
        print(f"Error: No .md files found in '{input_dir}'.")
        return False

    print(f"Combining {len(md_files)} files into '{output_file}'...")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, file_path in enumerate(tqdm(md_files, desc="Merging", unit="file")):
            try:
                content = file_path.read_text(encoding='utf-8')
                outfile.write(content)
                if i < len(md_files) - 1:
                    outfile.write(separator)
            except Exception as e:
                tqdm.write(f"Error reading {file_path.name}: {e}")

    return True

def main():
    parser = argparse.ArgumentParser(description="Combine multiple Markdown files into one.")
    parser.add_argument("--input", default="output_md", help="Directory containing .md files.")
    parser.add_argument("--output", default="combined_output.md", help="Name of the combined file.")
    parser.add_argument("--separator", default="\n\n---\n\n", help="Separator between files.")
    args = parser.parse_args()

    if combine_md_files(args.input, args.output, args.separator):
        print(f"\nDone! Combined file saved to: {args.output}")

if __name__ == "__main__":
    main()