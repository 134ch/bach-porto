# PGA Blog to Markdown (htmltomd_pgablogonly.py)

This script is designed to process the output of `getblog.py`. It converts HTML articles into high-quality Markdown while specifically addressing text encoding issues and simplifying layout elements.

## Prerequisites
```bash
pip install beautifulsoup4 markdownify
```

## Usage
1. Ensure your HTML files are in the `pga_articles/` folder.
2. Run the script: `python htmltomd_pgablogonly.py`
3. The converted Markdown files will appear in the `pga_markdown/` folder.

## Features
- **Mojibake Fixer**: Automatically corrects common encoding errors (e.g., `â€™` becomes `'`).
- **Media-to-Text**: Converts complex `<figure>` images and videos into a simple `"Caption" (URL = ...)` format.
- **Clean extraction**: Uses `markdownify` for standard conversion but strips decorative spans and scripts.
