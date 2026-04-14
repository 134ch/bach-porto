import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
import time

# Put all your URLs here
URLS = [
    "http://www.premiumghostwritingacademy.com/post/how-free-work-helps-you-land-your-first-high-paying-ghostwriting-client",
    "https://www.premiumghostwritingacademy.com/post/the-ship-30-for-30-case-study-our-2-000-000-asset",
    "http://www.premiumghostwritingacademy.com/post/my-3-000-000-cold-outreach-framework",
    "http://www.premiumghostwritingacademy.com/post/do-all-public-facing-people-need-a-ghostwriter-and-why-ghostwriting-isnt-saturated",
    "http://www.premiumghostwritingacademy.com/post/how-to-create-an-irresistible-ghostwriting-offer-and-charge-more-for-your-services",
    "http://www.premiumghostwritingacademy.com/post/the-simple-idea-that-helped-me-escape-my-9-to-5",
    "http://www.premiumghostwritingacademy.com/post/how-much-should-you-charge-as-a-ghostwriter-3-easy-questions-to-ask",
    "http://www.premiumghostwritingacademy.com/post/4-ways-to-build-trust-as-a-ghostwriter-without-being-an-internet-celebrity",
    "http://www.premiumghostwritingacademy.com/post/how-to-create-location-and-time-freedom-with-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/who-would-pay-a-ghostwriter-5-000",
    "http://www.premiumghostwritingacademy.com/post/7-rules-for-delighting-clients-this-is-the-secret-to-protecting-your-career-for-decades",
    "https://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-susheel-kumar",
    "http://www.premiumghostwritingacademy.com/post/7-reasons-why-every-writer-should-be-a-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-maria-jose-rodriguez",
    "https://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-joe-wuebben",
    "https://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-charlie-dice",
    "https://www.premiumghostwritingacademy.com/post/i-had-no-clue-no-experience-no-contacts-then-i-found-pga",
    "http://www.premiumghostwritingacademy.com/post/do-you-need-a-portfolio-to-get-ghostwriting-clients",
    "https://www.premiumghostwritingacademy.com/post/i-lost-70-pounds-doubled-my-annual-income-while-working-a-full-time-day-job-with-a-newborn",
    "https://www.premiumghostwritingacademy.com/post/youre-never-too-old-to-chart-a-new-course",
    "https://www.premiumghostwritingacademy.com/post/i-was-broke-depressed-and-out-of-options-now-i-live-my-dream-life-in-the-mediterranean-thanks-to-pga",
    "https://www.premiumghostwritingacademy.com/post/linkedin-ghostwriter-get-started-in-5-simple-steps",
    "https://www.premiumghostwritingacademy.com/post/3-simple-ways-to-structure-ghostwriting-deals",
    "https://www.premiumghostwritingacademy.com/post/ghostwriting-crash-course-5-must-watch-videos",
    "http://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-susheel-kumar",
    "http://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-maria-jose-rodriguez",
    "http://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-joe-wuebben",
    "https://www.premiumghostwritingacademy.com/post/how-to-land-your-first-ghostwriting-client",
    "https://www.premiumghostwritingacademy.com/post/make-money-writing-online-5-skills-to-make-you-dangerously-profitable-as-a-writer",
    "https://www.premiumghostwritingacademy.com/post/ghostwriting-sales-5-tips-to-help-you-land-more-high-paying-clients",
    "https://www.premiumghostwritingacademy.com/post/how-to-ghostwrite-and-nail-your-clients-voice",
    "https://www.premiumghostwritingacademy.com/post/do-ghostwriters-make-money",
    "https://www.premiumghostwritingacademy.com/post/i-spent-6-000-on-one-book-and-it-taught-me-two-life-changing-lessons-about-ghostwriting",
    "https://www.premiumghostwritingacademy.com/blog/blog?b9ddebee_page=2",
    "https://www.premiumghostwritingacademy.com/post/do-you-need-a-portfolio-to-get-ghostwriting-clients",
    "https://www.premiumghostwritingacademy.com/post/the-best-solopreneurship-business-is-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/i-had-no-clue-no-experience-no-contacts-then-i-found-pga",
    "http://www.premiumghostwritingacademy.com/post/premium-ghostwriting-academy-review-charlie-dice",
    "http://www.premiumghostwritingacademy.com/post/i-lost-70-pounds-doubled-my-annual-income-while-working-a-full-time-day-job-with-a-newborn",
    "https://www.premiumghostwritingacademy.com/post/5-million-dollar-lessons-i-learned-as-a-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/how-free-work-helps-you-land-your-first-high-paying-ghostwriting-client",
    "http://www.premiumghostwritingacademy.com/post/youre-never-too-old-to-chart-a-new-course",
    "https://www.premiumghostwritingacademy.com/post/how-to-create-an-irresistible-ghostwriting-offer-and-charge-more-for-your-services",
    "https://www.premiumghostwritingacademy.com/post/how-much-should-you-charge-as-a-ghostwriter-3-easy-questions-to-ask",
    "http://www.premiumghostwritingacademy.com/post/i-was-broke-depressed-and-out-of-options-now-i-live-my-dream-life-in-the-mediterranean-thanks-to-pga",
    "https://www.premiumghostwritingacademy.com/post/7-rules-for-delighting-clients-this-is-the-secret-to-protecting-your-career-for-decades",
    "https://www.premiumghostwritingacademy.com/post/break-these-8-faulty-beliefs-to-become-a-rich-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/12-tools-for-your-ghostwriting-business",
    "https://www.premiumghostwritingacademy.com/post/5-skills-to-become-a-profitable-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/how-to-ghostwrite-anything-for-anyone-even-if-you-dont-consider-yourself-a-writer",
    "https://www.premiumghostwritingacademy.com/post/7-reasons-why-every-writer-should-be-a-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/the-art-business-of-ghostwriting-7-lessons-from-ghostwriting-for-300-industry-leaders",
    "https://www.premiumghostwritingacademy.com/post/8-questions-every-beginner-ghostwriter-asks",
    "https://www.premiumghostwritingacademy.com/post/ghostwriting-pricing-strategy-every-service-should-follow-this-framework",
    "https://www.premiumghostwritingacademy.com/post/do-all-public-facing-people-need-a-ghostwriter-and-why-ghostwriting-isnt-saturated",
    "https://www.premiumghostwritingacademy.com/post/9-ai-tools-for-ghostwriters",
    "https://www.premiumghostwritingacademy.com/post/my-3-000-000-cold-outreach-framework",
    "https://www.premiumghostwritingacademy.com/post/a-proven-3-step-ghostwriting-onboarding-process",
    "http://www.premiumghostwritingacademy.com/post/3-simple-ways-to-structure-ghostwriting-deals",
    "http://www.premiumghostwritingacademy.com/post/linkedin-ghostwriter-get-started-in-5-simple-steps",
    "http://www.premiumghostwritingacademy.com/post/ghostwriting-crash-course-5-must-watch-videos",
    "http://www.premiumghostwritingacademy.com/post/how-to-land-your-first-ghostwriting-client",
    "http://www.premiumghostwritingacademy.com/post/make-money-writing-online-5-skills-to-make-you-dangerously-profitable-as-a-writer",
    "http://www.premiumghostwritingacademy.com/post/ghostwriting-sales-5-tips-to-help-you-land-more-high-paying-clients",
    "http://www.premiumghostwritingacademy.com/post/how-to-ghostwrite-and-nail-your-clients-voice",
    "http://www.premiumghostwritingacademy.com/post/i-spent-6-000-on-one-book-and-it-taught-me-two-life-changing-lessons-about-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/do-ghostwriters-make-money",
    "https://www.premiumghostwritingacademy.com/post/4-ways-to-build-trust-as-a-ghostwriter-without-being-an-internet-celebrity",
    "https://www.premiumghostwritingacademy.com/post/3-myths-and-misconceptions-about-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/the-ship-30-for-30-case-study-our-2-000-000-asset",
    "https://www.premiumghostwritingacademy.com/post/3-questions-to-find-the-most-profitable-writing-niche",
    "https://www.premiumghostwritingacademy.com/post/how-to-make-more-money-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/3-questions-to-find-the-most-profitable-writing-niche",
    "https://www.premiumghostwritingacademy.com/post/should-i-change-my-niche-as-a-ghostwriter-riding-the-genius-idiot-rollercoaster",
    "https://www.premiumghostwritingacademy.com/post/3-mindset-shifts-to-stop-making-excuses-and-start-taking-action",
    "https://www.premiumghostwritingacademy.com/post/why-ghostwriting-is-the-perfect-remote-job",
    "https://www.premiumghostwritingacademy.com/post/how-to-answer-ghostwriting-client-questions",
    "https://www.premiumghostwritingacademy.com/post/how-much-does-the-premium-ghostwriting-academy-cost",
    "https://www.premiumghostwritingacademy.com/post/3-reasons-why-ai-wont-replace-ghostwriters",
    "https://www.premiumghostwritingacademy.com/post/the-one-mistake-keeping-freelance-writers-underpaid-and-overworked",
    "http://www.premiumghostwritingacademy.com/post/break-these-8-faulty-beliefs-to-become-a-rich-ghostwriter",
    "http://www.premiumghostwritingacademy.com/post/the-best-solopreneurship-business-is-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/the-art-business-of-ghostwriting-7-lessons-from-ghostwriting-for-300-industry-leaders",
    "http://www.premiumghostwritingacademy.com/post/8-questions-every-beginner-ghostwriter-asks",
    "http://www.premiumghostwritingacademy.com/post/ghostwriting-pricing-strategy-every-service-should-follow-this-framework",
    "http://www.premiumghostwritingacademy.com/blog?b9ddebee_page=3",
    "http://www.premiumghostwritingacademy.com/post/should-i-change-my-niche-as-a-ghostwriter-riding-the-genius-idiot-rollercoaster",
    "http://www.premiumghostwritingacademy.com/post/5-million-dollar-lessons-i-learned-as-a-ghostwriter",
    "http://www.premiumghostwritingacademy.com/post/5-skills-to-become-a-profitable-ghostwriter",
    "https://www.premiumghostwritingacademy.com/post/who-would-pay-a-ghostwriter-5-000",
    "https://www.premiumghostwritingacademy.com/post/how-to-create-location-and-time-freedom-with-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/9-ai-tools-for-ghostwriters",
    "https://www.premiumghostwritingacademy.com/post/how-to-start-a-ghostwriting-business-from-scratch",
    "https://www.premiumghostwritingacademy.com/post/the-2-ways-to-grow-your-ghostwriting-business",
    "http://www.premiumghostwritingacademy.com/post/3-mindset-shifts-to-stop-making-excuses-and-start-taking-action",
    "http://www.premiumghostwritingacademy.com/post/how-to-make-more-money-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/12-tools-for-your-ghostwriting-business",
    "http://www.premiumghostwritingacademy.com/post/why-ghostwriting-is-the-perfect-remote-job",
    "http://www.premiumghostwritingacademy.com/post/how-much-does-the-premium-ghostwriting-academy-cost",
    "http://www.premiumghostwritingacademy.com/post/the-one-mistake-keeping-freelance-writers-underpaid-and-overworked",
    "http://www.premiumghostwritingacademy.com/post/how-to-answer-ghostwriting-client-questions",
    "https://www.premiumghostwritingacademy.com/post/the-5-pillar-premium-ghostwriting-business-audit",
    "http://www.premiumghostwritingacademy.com/post/3-reasons-why-ai-wont-replace-ghostwriters",
    "https://www.premiumghostwritingacademy.com/post/the-simple-idea-that-helped-me-escape-my-9-to-5",
    "http://www.premiumghostwritingacademy.com/post/a-proven-3-step-ghostwriting-onboarding-process",
    "http://www.premiumghostwritingacademy.com/post/the-5-pillar-premium-ghostwriting-business-audit",
    "http://www.premiumghostwritingacademy.com/post/how-to-ghostwrite-anything-for-anyone-even-if-you-dont-consider-yourself-a-writer",
    "http://www.premiumghostwritingacademy.com/post/3-myths-and-misconceptions-about-ghostwriting",
    "http://www.premiumghostwritingacademy.com/post/how-to-start-a-ghostwriting-business-from-scratch",
    "http://www.premiumghostwritingacademy.com/post/the-2-ways-to-grow-your-ghostwriting-business"
]

OUTPUT_DIR = Path("pga_articles")


def slugify(url: str) -> str:
    """
    Turn a URL into a safe filename base.
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if not path:
        base = "index"
    else:
        base = path.split("/")[-1] or "index"

    safe = []
    for ch in base:
        if ch.isalnum() or ch in ("-", "_"):
            safe.append(ch)
        else:
            safe.append("_")
    result = "".join(safe)
    if not result:
        result = "page"
    return result


def extract_main_text(html: str) -> str:
    """
    Try to grab the main article text.
    Falls back to body text if no article or main tag exists.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Try article tag first
    article = soup.find("article")
    if article is None:
        # Try main tag
        article = soup.find("main")
    if article is None:
        # Fall back to whole body
        article = soup.body or soup

    text = article.get_text("\n", strip=True)
    return text


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    total = len(URLS)
    for index, url in enumerate(URLS, start=1):
        print(f"Fetching {index}/{total}: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as exc:
            print(f"Error fetching {url}: {exc}")
            continue

        html = response.text
        base_name = f"{index:03d}_{slugify(url)}"

        # Save raw HTML
        html_path = OUTPUT_DIR / f"{base_name}.html"
        html_path.write_text(html, encoding="utf-8")

        # Save cleaned text
        text = extract_main_text(html)
        text_path = OUTPUT_DIR / f"{base_name}.txt"
        text_path.write_text(text, encoding="utf-8")

        # Small pause to be polite
        time.sleep(1)

    print("Done downloading all pages.")


if __name__ == "__main__":
    main()
