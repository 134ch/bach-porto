#!/usr/bin/env python3
"""
skool_downloader.py

Enhanced version with:
- Environment variable support (.env)
- Command-line arguments (headless mode, output dir, input file)
- Wait for CONTENT READY logic
- Automated batch processing
"""

import os
import sys
import re
import time
import hashlib
import getpass
import argparse
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables from .env if present
load_dotenv()

# Heuristic selectors where Skool renders the article body.
CONTENT_SELECTORS = [
    "article",
    ".ProseMirror",              # rich editor body
    ".prose",                    # common tailwind prose wrapper
    "[data-editor-root]",        # generic editor root
    "[class*='content']",
    "[class*='editor']",
]

_ILLEGAL_CHARS = r'[\\/:*?"<>|\x00-\x1F]'

def sanitize_title_to_filename(title: str, url: str, maxlen: int = 150) -> str:
    if not title:
        base = "page"
    else:
        base = re.sub(r"\s+", " ", title).strip()
        base = re.sub(_ILLEGAL_CHARS, "_", base)
    base = base[:maxlen].rstrip(" .")
    short = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
    return f"{base}__{short}.html" if base else f"page__{short}.html"

def setup_chrome(user_data_dir: Optional[str] = None, headless: bool = False, window_size=(1400, 900)) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if user_data_dir:
        options.add_argument(f"--user-data-dir={os.path.abspath(user_data_dir)}")
    if headless:
        options.add_argument("--headless=new")
    
    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
    except Exception:
        pass
    return driver

def wait_page_ready(driver, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except:
        pass
    end = time.time() + timeout
    while time.time() < end:
        try:
            if driver.execute_script("return document.readyState") == "complete":
                time.sleep(0.2)
                return
        except Exception:
            pass
        time.sleep(0.15)

def scroll_to_bottom(driver, step=800, pause=0.15, max_steps=40):
    last_y = -1
    for _ in range(max_steps):
        driver.execute_script("window.scrollBy(0, arguments[0]);", step)
        time.sleep(pause)
        y = driver.execute_script("return window.scrollY")
        if y == last_y:
            break
        last_y = y
    time.sleep(0.3)

def content_ready(driver, min_chars=800) -> bool:
    script = """
    const sels = arguments[0] || [];
    for (const sel of sels) {
      const el = document.querySelector(sel);
      if (el) {
        const txt = el.innerText || el.textContent || "";
        if (txt.trim().length >= arguments[1]) return true;
      }
    }
    return false;
    """
    try:
        return bool(driver.execute_script(script, CONTENT_SELECTORS, int(min_chars)))
    except Exception:
        return False

def wait_content_ready(driver, timeout=20, min_chars=800):
    end = time.time() + timeout
    while time.time() < end:
        if content_ready(driver, min_chars=min_chars):
            return True
        time.sleep(0.25)
    return False

def looks_like_login_or_challenge(url_lower: str, driver) -> bool:
    if any(x in url_lower for x in ["accounts.google.com", "signin", "login"]):
        return True
    try:
        html = driver.page_source.lower()
        if "challenge" in html and "waf" in html:
            return True
    except Exception:
        pass
    return False

def is_logged_in_to_skool(driver) -> bool:
    try:
        cur = driver.current_url.lower()
    except Exception:
        return False
    if ("accounts.google.com" in cur) or ("signin" in cur) or ("login" in cur and "skool.com" not in cur):
        return False
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        sign_elems = driver.find_elements(
            By.XPATH,
            "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'log in') or "
            "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign in')]"
        )
        if any(e.is_displayed() for e in sign_elems):
            return False
    except Exception:
        pass
    return "skool.com" in cur

def login_to_skool(driver, email: str, password: str) -> bool:
    login_urls = [
        "https://www.skool.com/login",
        "https://www.skool.com/signin",
    ]
    last_err = None
    for url in login_urls:
        try:
            driver.get(url)
            wait_page_ready(driver, timeout=15)
            if is_logged_in_to_skool(driver):
                return True

            email_input = pwd_input = submit_btn = None

            for how, sel in [
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='email']"),
                (By.XPATH, "//input[contains(@autocomplete,'email')]"),
            ]:
                try:
                    el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((how, sel)))
                    if el.is_displayed():
                        email_input = el; break
                except: continue

            for how, sel in [
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.XPATH, "//input[contains(@type,'password')]"),
            ]:
                try:
                    el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((how, sel)))
                    if el.is_displayed():
                        pwd_input = el; break
                except: continue

            for how, sel in [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'log in') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign in')]"),
            ]:
                try:
                    el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((how, sel)))
                    if el.is_displayed():
                        submit_btn = el; break
                except: continue

            if not email_input or not pwd_input or not submit_btn:
                if is_logged_in_to_skool(driver): return True
                last_err = "Could not locate login form fields."
                continue

            email_input.clear(); email_input.send_keys(email)
            pwd_input.clear();   pwd_input.send_keys(password)
            submit_btn.click()

            for _ in range(15):
                if is_logged_in_to_skool(driver): return True
                time.sleep(0.8)

            last_err = "Login redirection timeout."
        except Exception as e:
            last_err = str(e)
            continue

    print(f"[✖] Login failed: {last_err or 'unknown reason'}")
    return False

def save_current_page_as_html(driver, url: str, out_dir: Path) -> str:
    try:
        title = driver.title or "page"
    except:
        title = "page"
    filename = sanitize_title_to_filename(title, url)
    out_path = out_dir / filename
    html = driver.page_source
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)

def fetch_and_save(driver, url: str, out_dir: Path, min_chars=600) -> str:
    for attempt in range(2):
        driver.get(url)
        wait_page_ready(driver, timeout=25)

        if looks_like_login_or_challenge(driver.current_url.lower(), driver):
            if attempt == 0:
                time.sleep(2)
                continue
            else:
                raise RuntimeError(f"Redirected to login/challenge at {driver.current_url}")

        scroll_to_bottom(driver)
        ready = wait_content_ready(driver, timeout=15, min_chars=min_chars)
        if not ready and attempt == 0:
            scroll_to_bottom(driver, step=1200, pause=0.2)
            continue

        time.sleep(0.8)
        return save_current_page_as_html(driver, url, out_dir)

    raise RuntimeError("Content failed to load after retries")

def prompt_urls() -> List[str]:
    print("\nPaste URLs (one per line). Finish with an empty line:")
    urls = []
    while True:
        line = input().strip()
        if not line: break
        urls.append(line)
    return urls

def load_urls_from_file(file_path: str) -> List[str]:
    p = Path(file_path)
    if not p.exists():
        print(f"Error: URL file {file_path} not found.")
        return []
    with open(p, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def download_batch(driver, urls: List[str], out_dir: str):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    with tqdm(total=len(urls), desc="Job Progress", unit="pg") as bar:
        for url in urls:
            try:
                saved = fetch_and_save(driver, url, out_path)
                bar.set_postfix_str(f"OK: {Path(saved).name[:25]}...")
            except Exception as e:
                bar.set_postfix_str(f"ERR: {str(e)[:25]}")
            finally:
                bar.update(1)

def main():
    parser = argparse.ArgumentParser(description="Skool Article Downloader")
    parser.add_argument("--email", help="Skool email (or set SKOOL_EMAIL env)")
    parser.add_argument("--password", help="Skool password (or set SKOOL_PASSWORD env)")
    parser.add_argument("--file", help="Path to text file containing URLs to download")
    parser.add_argument("--output", default="skool_downloads", help="Output directory")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    parser.add_argument("--profile", help="Path to existing Chrome user-data-dir")
    
    args = parser.parse_args()

    print("=== Skool Downloader Pro ===\n")

    # Resolve credentials
    email = args.email or os.getenv("SKOOL_EMAIL")
    if not email:
        email = input("Skool email: ").strip()
    
    password = args.password or os.getenv("SKOOL_PASSWORD")
    if not password:
        password = getpass.getpass("Skool password: ")

    # Resolve URLs
    urls = []
    if args.file:
        urls = load_urls_from_file(args.file)
    
    if not urls:
        if args.file:
            print("No URLs found in file. Falling back to manual entry.")
        urls = prompt_urls()

    if not urls:
        print("No URLs provided. Exiting.")
        return

    try:
        driver = setup_chrome(user_data_dir=args.profile, headless=args.headless)
    except Exception as e:
        print(f"Failed to launch Chrome: {e}")
        return

    try:
        print("\n--- Authenticating ---")
        if not login_to_skool(driver, email, password):
            print("Authentication failed.")
            return
        
        print(f"[✔] Logged in. Starting batch of {len(urls)} URLs...")
        download_batch(driver, urls, args.output)
        print("\n[✔] All tasks completed.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
