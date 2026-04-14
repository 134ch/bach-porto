This script automates the process of downloading blog articles from a list of URLs and saving them in both raw HTML and cleaned text formats.

> [!TIP]
> **Next Step:** After downloading, use [**`html2md-blog`**](../html2md-blog/) to convert these HTML files into high-quality, LLM-friendly Markdown.

## Prerequisites
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Place your URLs in a file named `urls.txt` (one URL per line) and run:
```bash
python getblog.py
```

### Advanced Usage
You can specify a custom input file or output directory:
```bash
python getblog.py --file my_urls.txt --output pga_blogs --delay 2.0
```

### Command Line Arguments
- `--file`: Path to the text file containing URLs (default: `urls.txt`).
- `--output`: Directory to save the downloaded articles (default: `blog_html`).
- `--delay`: Delay between requests in seconds to be polite to the server (default: `1.0`).

## Features
- **Clean Extraction**: Attempts to extract only the main article text, falling back to body content if necessary.
- **Safe Filenames**: Automatically cleans URLs to create safe, descriptive filenames.
- **Progress Feedback**: Shows a real-time progress bar using `tqdm`.
- **Efficient**: Uses a persistent session for multiple requests to the same domain.
- **Retry Logic**: Handles network errors and skips failed URLs gracefully.
