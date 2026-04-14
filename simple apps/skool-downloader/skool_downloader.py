#!/usr/bin/env python3
"""
skool_downloader.py

Downloads Skool community pages as HTML files.
- Handles login and session verification robustly
- Waits for content to fully render before saving
- Scrolls to trigger lazy-loaded content
- Supports CLI arguments, .env files, and URL batch files
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

def safe_getpass(prompt: str = "Password: ") -> str:
    """
    Cross-platform password reader.
    `getpass.getpass()` in Git Bash (MinGW) silently breaks stdin for all
    subsequent input() calls. This function reads the password safely and
    then restores stdin so the rest of the script works normally.
    """
    try:
        pwd = getpass.getpass(prompt)
    except Exception:
        # Fallback: plain input with a warning (no masking)
        print("[warning] Secure password input unavailable, typing will be visible.")
        pwd = input(prompt)

    # Git Bash fix: after getpass, stdin may be broken — reattach it
    if sys.platform == "win32":
        try:
            sys.stdin = open("CONIN$", "r")  # Windows raw console input
        except Exception:
            pass
    else:
        try:
            sys.stdin = open("/dev/tty", "r")
        except Exception:
            pass

    return pwd

from tqdm import tqdm
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load .env if present
load_dotenv()

# Selectors where Skool renders the main article body.
CONTENT_SELECTORS = [
    "article",
    ".ProseMirror",
    ".prose",
    "[data-editor-root]",
    "[class*='content']",
    "[class*='editor']",
]

_ILLEGAL_CHARS = r'[\\/:*?"<>|\x00-\x1F]'

# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────

def sanitize_title_to_filename(title: str, url: str, maxlen: int = 150) -> str:
    base = re.sub(r"\s+", " ", title).strip() if title else "page"
    base = re.sub(_ILLEGAL_CHARS, "_", base)[:maxlen].rstrip(" .")
    short = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
    return f"{base}__{short}.html" if base else f"page__{short}.html"

def setup_chrome(
    user_data_dir: Optional[str] = None,
    headless: bool = False,
    window_size=(1400, 900)
) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    if user_data_dir:
        options.add_argument(f"--user-data-dir={os.path.abspath(user_data_dir)}")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")

    options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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
    """Wait for document.readyState == 'complete'."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception:
        pass
    deadline = time.time() + timeout
    while time.time() < deadline:
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

def content_ready(driver, min_chars=600) -> bool:
    script = """
    const sels = arguments[0] || [];
    for (const sel of sels) {
      const el = document.querySelector(sel);
      if (el) {
        const txt = (el.innerText || el.textContent || "").trim();
        if (txt.length >= arguments[1]) return true;
      }
    }
    return false;
    """
    try:
        return bool(driver.execute_script(script, CONTENT_SELECTORS, int(min_chars)))
    except Exception:
        return False

def wait_content_ready(driver, timeout=20, min_chars=600) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if content_ready(driver, min_chars=min_chars):
            return True
        time.sleep(0.3)
    return False

# ─────────────────────────────────────────────
# Auth helpers  (fixed)
# ─────────────────────────────────────────────

def is_on_auth_page(driver) -> bool:
    """Return True if browser is on a login / sign-in / challenge page."""
    try:
        cur = driver.current_url.lower()
    except Exception:
        return True
    return any(x in cur for x in ["/login", "/signin", "accounts.google.com"])

def has_session(driver) -> bool:
    """
    Strict check: we are on skool.com, NOT on an auth page,
    AND a password input is NOT visible (i.e., the login form is gone).
    """
    try:
        cur = driver.current_url.lower()
    except Exception:
        return False

    if "skool.com" not in cur:
        return False

    if is_on_auth_page(driver):
        return False

    # Make sure login form is not still visible
    try:
        pwd_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if any(f.is_displayed() for f in pwd_fields):
            return False
    except Exception:
        pass

    return True

def login_to_skool(driver, email: str, password: str) -> bool:
    """
    Navigate to Skool login, fill credentials, submit, and wait for a real
    redirect away from the auth page before declaring success.
    """
    print("  → Opening Skool login page…")
    print("    ⚠  Do NOT click or type in the browser window — the script handles it.")

    try:
        driver.get("https://www.skool.com/login")
        wait_page_ready(driver, timeout=15)
    except Exception as e:
        print(f"  ✗ Could not load login page: {e}")
        return False

    # Already logged in from a cached profile?
    if not is_on_auth_page(driver):
        print("  → Session already active.")
        return True

    # ── Find email field ───────────────────────
    email_input = None
    for how, sel in [
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[name='email']"),
        (By.XPATH, "//input[contains(@autocomplete,'email')]"),
    ]:
        try:
            el = WebDriverWait(driver, 8).until(EC.visibility_of_element_located((how, sel)))
            email_input = el
            break
        except Exception:
            continue

    if not email_input:
        print("  ✗ Email field not found on login page.")
        return False

    # ── Find password field ────────────────────
    pwd_input = None
    try:
        pwd_input = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
    except Exception:
        print("  ✗ Password field not found on login page.")
        return False

    # ── Find submit button ─────────────────────
    # Strategy: try specific selectors first, then fall back to any visible button in a form
    submit_btn = None
    button_strategies = [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.CSS_SELECTOR, "form button"),
        (By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'log')]"),
        (By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sign')]"),
        (By.XPATH, "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'continue')]"),
        (By.XPATH, "//input[@type='submit']"),
    ]
    for how, sel in button_strategies:
        try:
            el = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((how, sel)))
            if el.is_displayed():
                submit_btn = el
                break
        except Exception:
            continue

    # Last resort: grab all visible buttons and pick the first one
    if not submit_btn:
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            visible = [b for b in all_buttons if b.is_displayed() and b.is_enabled()]
            if visible:
                print(f"  ⚠  Using fallback: found {len(visible)} visible button(s): {[b.text.strip() for b in visible]}")
                submit_btn = visible[-1]  # Usually the last button is submit
        except Exception:
            pass

    if not submit_btn:
        print("  ✗ Submit button not found on login page.")
        return False

    # ── Fill & submit ──────────────────────────
    print("  → Filling credentials…")
    email_input.clear()
    email_input.send_keys(email)
    time.sleep(0.4)
    pwd_input.clear()
    pwd_input.send_keys(password)
    time.sleep(0.4)
    submit_btn.click()

    print("  → Waiting for post-login redirect…")

    # Wait up to 25 s for the URL to leave the login/signin page
    try:
        WebDriverWait(driver, 25).until(
            lambda d: not is_on_auth_page(d)
        )
    except TimeoutException:
        # Wrong password, or 2FA, or slow network
        print(f"  ✗ Still on auth page after 25 s. "
              f"Current URL: {driver.current_url}")
        print("    Check your credentials or complete any 2FA in the browser.")
        return False

    # Let the dashboard settle
    time.sleep(2)
    wait_page_ready(driver, timeout=10)

    if has_session(driver):
        print(f"  [✔] Authenticated. Current page: {driver.current_url}")
        return True

    print(f"  ✗ Redirected but session check failed. URL: {driver.current_url}")
    return False

# ─────────────────────────────────────────────
# Download helpers
# ─────────────────────────────────────────────

def save_current_page(driver, url: str, out_dir: Path) -> str:
    try:
        title = driver.title or "page"
    except Exception:
        title = "page"
    fname = sanitize_title_to_filename(title, url)
    out_path = out_dir / fname
    out_path.write_text(driver.page_source, encoding="utf-8")
    return str(out_path)

def fetch_and_save(driver, url: str, out_dir: Path, min_chars: int = 600) -> str:
    for attempt in range(2):
        driver.get(url)
        wait_page_ready(driver, timeout=25)

        # Redirect back to login = session expired
        if is_on_auth_page(driver):
            if attempt == 0:
                time.sleep(2)
                continue
            raise RuntimeError("Redirected to auth page — session may have expired.")

        scroll_to_bottom(driver)
        ready = wait_content_ready(driver, timeout=18, min_chars=min_chars)

        if not ready and attempt == 0:
            scroll_to_bottom(driver, step=1200, pause=0.2)
            time.sleep(1)
            continue

        time.sleep(0.8)
        return save_current_page(driver, url, out_dir)

    raise RuntimeError("Content did not load after two attempts.")

def load_urls_from_file(file_path: str) -> List[str]:
    p = Path(file_path)
    if not p.exists():
        print(f"Error: URL file '{file_path}' not found.")
        return []
    with open(p, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]

def prompt_urls() -> List[str]:
    print("\nPaste URLs (one per line). Finish with an empty line:")
    urls = []
    while True:
        line = input().strip()
        if not line:
            break
        urls.append(line)
    return urls

def download_batch(driver, urls: List[str], out_dir: str):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    failed = []

    with tqdm(total=len(urls), desc="Downloading", unit="pg") as bar:
        for url in urls:
            try:
                saved = fetch_and_save(driver, url, out_path)
                bar.set_postfix_str(f"✔ {Path(saved).name[:30]}")
            except Exception as e:
                bar.set_postfix_str(f"✗ {str(e)[:35]}")
                failed.append((url, str(e)))
            finally:
                bar.update(1)

    if failed:
        print(f"\n⚠  {len(failed)} URL(s) failed:")
        for u, err in failed:
            print(f"   {u}\n     → {err}")

# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Skool Page Downloader — saves community/classroom pages as HTML"
    )
    parser.add_argument("--email",    help="Skool email  (or env SKOOL_EMAIL)")
    parser.add_argument("--password", help="Skool password (or env SKOOL_PASSWORD)")
    parser.add_argument("--file",     help="Text file with one URL per line")
    parser.add_argument("--output",   default="skool_downloads", help="Output folder")
    parser.add_argument("--headless", action="store_true",
                        help="Run Chrome in background (no visible window)")
    parser.add_argument("--profile",  help="Existing Chrome user-data-dir (reuse session)")
    args = parser.parse_args()

    print("=== Skool Downloader ===\n")

    # Credentials: CLI → .env → interactive
    email = args.email or os.getenv("SKOOL_EMAIL") or input("Skool email: ").strip()
    password = args.password or os.getenv("SKOOL_PASSWORD") or safe_getpass("Skool password: ")

    if not email or not password:
        print("Email and password are required.")
        sys.exit(1)

    # URLs: file → interactive
    urls: List[str] = []
    if args.file:
        urls = load_urls_from_file(args.file)
        if not urls:
            print("No valid URLs found in file, switching to interactive input.")
    if not urls:
        urls = prompt_urls()
    if not urls:
        print("No URLs provided. Exiting.")
        sys.exit(1)

    # Launch browser
    try:
        driver = setup_chrome(user_data_dir=args.profile, headless=args.headless)
    except WebDriverException as e:
        print(f"Failed to launch Chrome: {e}")
        sys.exit(1)

    try:
        if not login_to_skool(driver, email, password):
            print("\n[✖] Login failed. Exiting.")
            sys.exit(2)

        print(f"\n→ Starting download of {len(urls)} URL(s) → '{args.output}'/\n")
        download_batch(driver, urls, args.output)
        print("\n[✔] Done.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
