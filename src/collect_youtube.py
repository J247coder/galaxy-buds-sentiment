"""Step 1a: collect YouTube comments for every earbud model (official YouTube Data API).

Usage:
    export YOUTUBE_API_KEY="your key"
    python src/collect_youtube.py
"""
import os
import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import PRODUCTS, RAW_DIR, VIDEOS_PER_PRODUCT, COMMENTS_PER_VIDEO


def find_videos(yt, product, n):
    resp = yt.search().list(
        q=f"Samsung {product} review", part="snippet", type="video",
        maxResults=n, relevanceLanguage="en", order="relevance",
    ).execute()
    return [(i["id"]["videoId"], i["snippet"]["title"]) for i in resp["items"]]


def get_comments(yt, video_id, limit):
    rows, token = [], None
    while len(rows) < limit:
        try:
            resp = yt.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100,
                pageToken=token, textFormat="plainText",
            ).execute()
        except HttpError as e:          # comments disabled, quota, etc.
            print(f"   skipped {video_id}: HTTP {e.resp.status}")
            break
        for item in resp["items"]:
            s = item["snippet"]["topLevelComment"]["snippet"]
            rows.append({
                "video_id": video_id,
                "author": s.get("authorDisplayName"),
                "text_raw": s.get("textDisplay"),
                "likes": s.get("likeCount", 0),
                "published_at": s.get("publishedAt"),
            })
        token = resp.get("nextPageToken")
        if not token:
            break
        time.sleep(0.2)
    return rows[:limit]


def main():
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise SystemExit("Set YOUTUBE_API_KEY first (see README).")
    yt = build("youtube", "v3", developerKey=key)

    all_rows = []
    for product in PRODUCTS:
        print(f"== {product}")
        for vid, title in find_videos(yt, product, VIDEOS_PER_PRODUCT):
            comments = get_comments(yt, vid, COMMENTS_PER_VIDEO)
            print(f"   {len(comments):4d} comments  <- {title[:60]}")
            for c in comments:
                c.update(product=product, source="YouTube", video_title=title)
            all_rows += comments

    df = pd.DataFrame(all_rows)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = RAW_DIR / "youtube_comments.csv"
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} comments -> {out}")


if __name__ == "__main__":
    main()
