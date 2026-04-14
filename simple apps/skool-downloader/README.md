# Skool Downloader (skool_downloader.py)

A powerful automation tool to download Skool community posts and lessons as HTML files. It handles authentication and dynamic content loading.

## Prerequisites
```bash
pip install selenium webdriver-manager tqdm
```

## Usage
1. Run the script: `python skool_downloader.py`
2. Enter your Skool credentials (password entry is hidden).
3. Paste the URLs you want to download (one per line, then an empty line to finish).
4. The script will log in, navigate to each page, scroll to trigger lazy loading, and save the content.

## Features
- **Smart Waiting**: Only saves the page once the main content body has fully loaded (checked by character count).
- **Auto-Scroll**: Automatically scrolls to the bottom to ensure images and late-loading content are captured.
- **Sanitized Filenames**: Names files based on the actual page title and adds a unique hash to prevent overwriting.
- **Retry Logic**: Automatically retries if it hits a challenge or redirect.
