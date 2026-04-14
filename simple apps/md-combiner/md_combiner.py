import os
import re
import tkinter as tk
from tkinter import filedialog

def natural_sort_key(filename):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', filename)]

def combine_md_files(folder_path, output_filename="combined_output.md", separator="\n\n---\n\n"):
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]

    if not md_files:
        print("No .md files found in the specified folder.")
        return

    md_files.sort(key=natural_sort_key)

    print(f"Found {len(md_files)} .md files. Combining in this order:")
    for i, f in enumerate(md_files, 1):
        print(f"  {i:>3}. {f}")

    output_path = os.path.join(folder_path, output_filename)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        for i, filename in enumerate(md_files):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
            outfile.write(content)
            if i < len(md_files) - 1:
                outfile.write(separator)

    print(f"\nDone! Combined file saved to:\n  {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    print("Opening folder picker...")
    folder = filedialog.askdirectory(title="Select folder containing .md files")

    if not folder:
        print("No folder selected. Exiting.")
    else:
        combine_md_files(folder)