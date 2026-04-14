# Bach Portfolio (porto-bach)

This repository is a showcase of my development work, featuring a collection of production-grade Python utilities and a modern front-end landing page. It is deployed live at [bachwidy.site](https://bachwidy.site).

## 🚀 The AI-Enhanced Suite

Inside the [`simple apps/`](simple%20apps/) directory is a collection of professionalized tools focused on content extraction, conversion, and asset management.

### 📥 Downloaders
- **[Skool Downloader](simple%20apps/skool-downloader/)**: Automates downloading community content. Handles multi-step login and dynamic content.
- **[Blog Crawler](simple%20apps/getblog/)**: Fetches and cleans articles from the web with session persistence.

### 🔄 Converters
- **[HTML to Markdown](simple%20apps/html2md/)**: Converts HTML files into clean Markdown, preservation formatting and video embeds.
- **[Blog to Markdown](simple%20apps/html2md-blog/)**: Specialized for AI-readiness. Fixes text encoding and converts media to descriptive labels.
- **[Markdown to PDF](simple%20apps/mdtopdf/)**: Generates premium, styled PDFs with page numbers and custom CSS.

### 🛠 Utilities
- **[Video Link Extractor](simple%20apps/vidlink/)**: Scans content to extract and catalog video links (YouTube, Loom, etc.) into CSV format.
- **[Markdown Combiner](simple%20apps/md-combiner/)**: Merges multiple Markdown files into a single master document based on natural sorting.

---

## ☁️ Deployment (Cloudflare Pages)

The landing page (`index.html`) is designed to be hosted on **Cloudflare Pages**. 

### How to deploy:
1.  **Connect GitHub**: Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/) and go to "Workers & Pages".
2.  **Create Project**: Select "Connect to Git" and choose this repository (`porto-bach`).
3.  **Build Settings**:
    *   **Framework Preset**: None (Static site)
    *   **Build command**: (Leave empty)
    *   **Build output directory**: `/` (root)
4.  **Custom Domain**: Go to the "Custom Domains" tab and add `bachwidy.site`.

---

## 🛠 Engineering Standards
Every tool in this repository follows a standardized engineering pattern:
- **CLI-Driven**: All scripts use `argparse` for professional command-line interaction.
- **Environment Aware**: Scripts use `.env` files for secure credential management.
- **Visual Feedback**: Real-time progress tracking via `tqdm`.
- **Robustness**: Automated creation of input folders and sample files for new users.
