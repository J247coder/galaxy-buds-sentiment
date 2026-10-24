"""Step 1b: WEB SCRAPING of review pages (requests + BeautifulSoup).

IMPORTANT
- Only scrape pages whose robots.txt / terms allow it. This script checks robots.txt for you.
- Big shops (Amazon, Samsung, Best Buy) load reviews with JavaScript or block bots,
  so plain requests often returns nothing. Pick a review site that serves reviews in plain HTML.
- Every site has different HTML. Open the page -> right click -> Inspect, find the
  CSS selectors, and put them in SITES below. That is the only part you must edit.

Usage:
    python src/scrape_reviews.py
"""
import time
import urllib.robotparser
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import RAW_DIR

HEADERS = {"User-Agent": "Mozilla/5.0 (student-project; contact: your-email@example.com)"}

# --- EDIT THIS --------------------------------------------------------------
SITES = [
    # {
    #     "product": "Galaxy Buds2 Pro",
    #     "source": "SomeReviewSite",
    #     "url": "https://example.com/galaxy-buds2-pro/reviews?page={page}",
    #     "pages": 5,
    #     "review_box": "div.review",          # one element per review
    #     "text": "p.review-text",
    #     "rating": "span.stars",              # optional, set None if absent
    #     "author": "span.author",             # optional
    #     "date": "time",                      # optional
    # },
]
# ----------------------------------------------------------------------------


def allowed(url):
    p = urlparse(url)
    rp = urllib.robotparser.RobotFileParser(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return False


def pick(box, selector):
    if not selector:
        return None
    el = box.select_one(selector)
    return el.get_text(" ", strip=True) if el else None


def scrape_site(cfg):
    rows = []
    for page in range(1, cfg["pages"] + 1):
        url = cfg["url"].format(page=page)
        if not allowed(url):
            print(f"robots.txt does not allow {url} -> skipped")
            break
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"{url} -> HTTP {r.status_code}, stopping")
            break
        soup = BeautifulSoup(r.text, "html.parser")
        boxes = soup.select(cfg["review_box"])
        if not boxes:
            print(f"page {page}: no reviews found (check selectors / JavaScript-loaded?)")
            break
        for b in boxes:
            rows.append({
                "product": cfg["product"], "source": cfg["source"],
                "text_raw": pick(b, cfg["text"]),
                "rating": pick(b, cfg.get("rating")),
                "author": pick(b, cfg.get("author")),
                "published_at": pick(b, cfg.get("date")),
                "likes": 0,
            })
        print(f"page {page}: {len(boxes)} reviews")
        time.sleep(2)           # be polite
    return rows


def main():
    if not SITES:
        print("SITES is empty. Edit src/scrape_reviews.py first (see comments at top).")
        return
    rows = []
    for cfg in SITES:
        rows += scrape_site(cfg)
    df = pd.DataFrame(rows)
    out = RAW_DIR / "web_reviews.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} reviews -> {out}")


if __name__ == "__main__":
    main()
