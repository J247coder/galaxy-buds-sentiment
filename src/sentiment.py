"""Step 3: sentiment (VADER) for each comment + aspect-level sentiment."""
import re
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import PROCESSED_DIR, ASPECTS

sia = SentimentIntensityAnalyzer()


def label(score):
    if score >= 0.05:
        return "Positive"
    if score <= -0.05:
        return "Negative"
    return "Neutral"


def aspect_rows(review_id, text):
    """Split into sentences; score every sentence that mentions an aspect keyword."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        low = sent.lower()
        for aspect, words in ASPECTS.items():
            if any(re.search(rf"\b{re.escape(w)}", low) for w in words):
                s = sia.polarity_scores(sent)["compound"]
                out.append({"review_id": review_id, "aspect": aspect,
                            "compound": s, "label": label(s)})
    return out


def main():
    df = pd.read_csv(PROCESSED_DIR / "reviews_clean.csv")
    df["review_id"] = df.index + 1
    df["compound"] = df["text_clean"].map(lambda t: sia.polarity_scores(t)["compound"])
    df["sentiment"] = df["compound"].map(label)
    df.to_csv(PROCESSED_DIR / "reviews_scored.csv", index=False)

    rows = []
    for rid, text in zip(df["review_id"], df["text_clean"]):
        rows += aspect_rows(rid, text)
    pd.DataFrame(rows, columns=["review_id", "aspect", "compound", "label"]).to_csv(
        PROCESSED_DIR / "aspects_scored.csv", index=False)
    print(df["sentiment"].value_counts().to_string())
    print(f"{len(rows)} aspect mentions found")


if __name__ == "__main__":
    main()
