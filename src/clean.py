"""Step 2: combine raw files and clean the text."""
import html
import re
import pandas as pd

from config import RAW_DIR, PROCESSED_DIR

URL_RE = re.compile(r"https?://\S+|www\.\S+")
TAG_RE = re.compile(r"<[^>]+>")


def clean_text(t):
    t = html.unescape(str(t))
    t = TAG_RE.sub(" ", t)
    t = URL_RE.sub(" ", t)
    t = re.sub(r"@\w+", " ", t)          # @mentions
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    files = list(RAW_DIR.glob("*.csv"))
    if not files:
        raise SystemExit("No raw CSV files in data/raw/. Run a collector (or make_sample_data.py) first.")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    before = len(df)

    for col, default in [("likes", 0), ("rating", None), ("author", None), ("published_at", None)]:
        if col not in df.columns:
            df[col] = default

    df = df.dropna(subset=["text_raw", "product"])
    df["text_clean"] = df["text_raw"].map(clean_text)
    df = df[df["text_clean"].str.split().str.len() >= 3]            # drop very short comments
    df = df.drop_duplicates(subset=["product", "text_clean"])        # drop spam / repeats
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df.reset_index(drop=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "reviews_clean.csv", index=False)
    print(f"Cleaned: {before} -> {len(df)} rows")


if __name__ == "__main__":
    main()
