import re
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md


INPUT_DIR = Path("pga_articles")
OUTPUT_DIR = Path("pga_markdown")


def fix_text_encoding(text: str) -> str:
    """
    Fix mojibake like:
    - donât -> don't
    - youâll -> you'll
    - ârelationship equityâ -> "relationship equity"
    And similar issues.
    We do this by direct string replacement instead of re-decoding.
    """

    # Core mojibake fragments -> correct characters
    replacements = {
        "â": "'",   # apostrophe
        "â": "'",   # opening single quote
        "â": '"',   # opening double quote
        "â": '"',   # closing double quote
        "â": "-",   # en dash
        "â": "-",   # em dash
        "â¦": "...", # ellipsis
        "Â\xa0": " ", # non breaking space
        "Â ": " ",    # stray Â
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Optional clean up for extra spaces or weird spacing
    text = re.sub(r"[ \t]+", " ", text)
    return text



def convert_figure_to_text(fig, soup):
    """
    Turn a <figure> containing a video or image into a simple <p> node:
    - "Caption" (URL = https://...)
    If no caption, use "video" or "picture".
    """
    iframe = fig.find("iframe")
    img = fig.find("img")

    if iframe is not None:
        url = iframe.get("src", "").strip()
        caption = iframe.get("title") or "video"
        caption = caption.strip() or "video"
        text = f"\"{caption}\" (URL = {url})"
    elif img is not None:
        url = img.get("src", "").strip()
        # Try figcaption first
        figcaption = fig.find("figcaption")
        if figcaption and figcaption.get_text(strip=True):
            caption = figcaption.get_text(strip=True)
        else:
            # Fallback to alt, then placeholder
            caption = img.get("alt") or "picture"
        caption = caption.strip() or "picture"
        text = f"\"{caption}\" (URL = {url})"
    else:
        # Not a video or image we care about
        return

    new_p = soup.new_tag("p")
    new_p.string = text
    fig.replace_with(new_p)


def convert_inline_img_to_text(img, soup):
    """
    Handle <img> tags that are not inside <figure>,
    convert them to the same "Caption" (URL = ...) format.
    """
    url = img.get("src", "").strip()
    caption = img.get("alt") or "picture"
    caption = caption.strip() or "picture"
    text = f"\"{caption}\" (URL = {url})"

    new_p = soup.new_tag("p")
    new_p.string = text
    img.replace_with(new_p)


def extract_article_html(html: str) -> str:
    """
    Extract the inner HTML of the article content only
    (the richtext block inside <article>).
    """
    soup = BeautifulSoup(html, "html.parser")

    # The main article content lives inside:
    # <article class="blogcontent"> ... <div class="blogstyling w-richtext">...</div>
    article_richtext = soup.select_one("article .blogstyling")
    if article_richtext is None:
        # Fallback: try any .blogstyling if this selector fails
        article_richtext = soup.select_one(".blogstyling")

    if article_richtext is None:
        # Nothing to extract
        return ""

    # Work on a copy so we can safely mutate
    work_soup = BeautifulSoup(str(article_richtext), "html.parser")

    # Remove scripts and styles
    for tag in work_soup(["script", "style"]):
        tag.decompose()

    # Replace <figure> blocks containing videos or images
    for fig in work_soup.find_all("figure"):
        convert_figure_to_text(fig, work_soup)

    # Handle any remaining <img> tags directly inside the article content
    for img in work_soup.find_all("img"):
        convert_inline_img_to_text(img, work_soup)

    # Optionally remove embedded tweet wrappers (if you do not want them)
    for embed_div in work_soup.select("div.w-embed"):
        embed_div.decompose()

    # Return the cleaned inner HTML
    return "".join(str(child) for child in work_soup.contents)


def html_to_markdown(html: str) -> str:
    """
    Extract article HTML, convert to Markdown, then fix encoding issues.
    """
    article_html = extract_article_html(html)
    if not article_html:
        return ""

    # Convert HTML -> Markdown
    markdown = md(
        article_html,
        heading_style="ATX",
        strip=["span"],  # strip decorative spans if any
    )

    # Fix mojibake and punctuation issues
    markdown = fix_text_encoding(markdown)

    # Trim leading/trailing whitespace
    return markdown.strip() + "\n"


def process_file(path: Path):
    print(f"Converting {path.name}...")
    html = path.read_text(encoding="utf-8", errors="ignore")
    markdown = html_to_markdown(html)

    if not markdown.strip():
        print(f"  Warning: no article content found in {path.name}")
        return

    out_path = OUTPUT_DIR / (path.stem + ".md")
    out_path.write_text(markdown, encoding="utf-8")
    print(f"  -> Saved {out_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    html_files = sorted(INPUT_DIR.glob("*.html"))
    if not html_files:
        print(f"No .html files found in {INPUT_DIR.resolve()}")
        return

    for path in html_files:
        process_file(path)

    print("Done converting all HTML files to Markdown.")


if __name__ == "__main__":
    main()
