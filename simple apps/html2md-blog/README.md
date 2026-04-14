A specialized tool for converting blog articles into an LLM-friendly Markdown format.

> [!NOTE]
> Designed to process the output from [**`getblog`**](../getblog/).

## Prerequisites
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Place your HTML files (e.g., from `getblog.py`) in a folder named `blog_html` and run:
```bash
python html2md_blog.py
```

### Options
Specify custom paths via command line:
```bash
python html2md_blog.py --input my_blogs --output my_markdown
```

### Command Line Arguments
- `--input`: Source directory of HTML files (default: `blog_html`).
- `--output`: Destination directory for Markdown files (default: `blog_markdown`).

## Special Features
- **LLM-Ready Output**: Instead of Markdown image tags, it converts images and videos into descriptive text labels like `"Action Shoot" (URL = https://...)`. This is often more useful for feeding content into AI models.
- **Encoding Fixes**: Automatically detects and repairs "mojibake" (corrupted characters like `â€™` instead of `'`).
- **Clean Structure**: Strips scripts, styles, and decorative elements to focus strictly on the article content.
