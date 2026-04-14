#!/usr/bin/env python3
"""
skool_downloader.py

What changed:
- Wait for CONTENT READY, not just document.readyState.
- Scroll the page to trigger lazy content, then small idle delay.
- Retry once on redirect/challenge.
- Save as .html using sanitized page title + short URL hash.

Requirements:
    pip install selenium webdriver-manager tqdm
"""

import os, sys, re, time, hashlib, getpass
from pathlib import Path
from typing import List, Optional

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Heuristic selectors where Skool renders the article body.
# Add or reorder if you notice variants.
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

def setup_chrome(user_data_dir: Optional[str] = None, window_size=(1400, 900)) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if user_data_dir:
        options.add_argument(f"--user-data-dir={os.path.abspath(user_data_dir)}")
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
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
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
    # small settle
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
    # Common challenge hints in HTML
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
        "https://www.skool.com/"
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
                except TimeoutException:
                    continue

            for how, sel in [
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.XPATH, "//input[contains(@type,'password')]"),
            ]:
                try:
                    el = WebDriverWait(driver, 5).until(EC.presence_of_element_located((how, sel)))
                    if el.is_displayed():
                        pwd_input = el; break
                except TimeoutException:
                    continue

            for how, sel in [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'log in') or contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign in')]"),
                (By.XPATH, "//input[@type='submit']"),
            ]:
                try:
                    el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((how, sel)))
                    if el.is_displayed():
                        submit_btn = el; break
                except TimeoutException:
                    continue

            if not email_input or not pwd_input or not submit_btn:
                if is_logged_in_to_skool(driver):
                    return True
                last_err = "Could not locate login form."
                continue

            email_input.clear(); email_input.send_keys(email)
            pwd_input.clear();   pwd_input.send_keys(password)
            submit_btn.click()

            wait_page_ready(driver, timeout=20)
            for _ in range(12):
                if is_logged_in_to_skool(driver):
                    return True
                time.sleep(0.6)

            last_err = "Login did not complete."
        except Exception as e:
            last_err = str(e)
            continue

    print(f"[✖] Login failed: {last_err or 'unknown reason'}")
    return False

def save_current_page_as_html(driver, url: str, out_dir: Path) -> str:
    try:
        title = driver.title or "page"
    except Exception:
        title = "page"
    filename = sanitize_title_to_filename(title, url)
    out_path = out_dir / filename
    html = driver.page_source
    out_path.write_text(html, encoding="utf-8")
    return str(out_path)

def fetch_and_save(driver, url: str, out_dir: Path, min_chars=800) -> str:
    """Navigate, wait for content, scroll, idle, then save. Retry once if needed."""
    for attempt in range(2):  # 0, 1
        driver.get(url)
        wait_page_ready(driver, timeout=25)

        cur = driver.current_url.lower()
        if looks_like_login_or_challenge(cur, driver):
            if attempt == 0:
                time.sleep(1.2)
                continue
            else:
                raise RuntimeError(f"Redirected to login or challenge: {cur}")

        # Trigger lazy loads
        scroll_to_bottom(driver)
        # Wait for content body to have “enough” text
        ready = wait_content_ready(driver, timeout=12, min_chars=min_chars)
        if not ready and attempt == 0:
            # small extra scroll and retry loop
            scroll_to_bottom(driver, step=1200, pause=0.1, max_steps=20)
            time.sleep(0.8)
            continue

        # small settle to allow late images or code blocks to render
        time.sleep(0.6)
        return save_current_page_as_html(driver, url, out_dir)

    # If we reach here, both attempts failed
    raise RuntimeError("Content not ready after retries")

def prompt_nonempty(prompt_text: str) -> str:
    s = ""
    while not s.strip():
        s = input(prompt_text).strip()
    return s

def prompt_urls() -> List[str]:
    print("\nPaste URLs to download. one per line. finish with an empty line.")
    urls = []
    while True:
        line = input().strip()
        if not line:
            break
        urls.append(line)
    if not urls:
        print("You must provide at least one URL.")
        return prompt_urls()
    return urls

def download_batch(driver, urls: List[str], out_dir: str):
    out_path = Path(out_dir); out_path.mkdir(parents=True, exist_ok=True)
    with tqdm(total=len(urls), desc="Downloading", unit="page") as bar:
        for url in urls:
            note = ""
            try:
                saved = fetch_and_save(driver, url, out_path, min_chars=800)
                note = f"saved: {Path(saved).name}"
            except Exception as e:
                # Save whatever DOM we have as a fallback, plus a note
                try:
                    fname = f"FAILED__{hashlib.md5(url.encode()).hexdigest()[:6]}.html"
                    (out_path / fname).write_text(driver.page_source, encoding="utf-8")
                except Exception:
                    pass
                note = f"error: {str(e)[:60]}"
            finally:
                bar.set_postfix_str(note[:40]); bar.update(1)

def main():
    print("=== Skool Downloader, content-ready HTML, single browser ===\n")

    email = prompt_nonempty("Skool email: ")
    password = getpass.getpass("Skool password (hidden): ")

    reuse = input("Reuse an existing Chrome profile? (y/N): ").strip().lower() == "y"
    user_data_dir = None
    if reuse:
        user_data_dir = prompt_nonempty("Chrome user-data-dir path: ").strip()
        print("Close all Chrome windows before continuing.\n")

    try:
        driver = setup_chrome(user_data_dir=user_data_dir)
    except WebDriverException as e:
        print("Failed to launch Chrome:", e); sys.exit(1)

    print("\n--- Logging in to Skool ---")
    if not login_to_skool(driver, email, password):
        print("Exiting due to failed login.")
        driver.quit(); sys.exit(2)
    print("[✔] Successfully logged in to skool.com")

    try:
        while True:
            urls = prompt_urls()
            out_dir = input("Output folder [skool_downloads_html]: ").strip() or "skool_downloads_html"
            print(f"\nSaving {len(urls)} page(s) to: {out_dir}")
            download_batch(driver, urls, out_dir)
            print("\n[✔] Finished downloading this batch.")
            again = input("Download more links? (y/N): ").strip().lower()
            if again != "y":
                print("Done. exiting.")
                break
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
