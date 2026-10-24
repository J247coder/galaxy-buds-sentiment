"""Step 4: load everything into SQLite using the ERD in docs/erd.md."""
import sqlite3
import pandas as pd

from config import DB_PATH, PROCESSED_DIR, PRODUCTS, ASPECTS

SCHEMA = """
DROP TABLE IF EXISTS review_aspects;
DROP TABLE IF EXISTS sentiment_results;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS aspects;
DROP TABLE IF EXISTS sources;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    series       TEXT,
    release_year INTEGER
);
CREATE TABLE sources (
    source_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE
);
CREATE TABLE aspects (
    aspect_id INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE
);
CREATE TABLE reviews (
    review_id    INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL REFERENCES products(product_id),
    source_id    INTEGER NOT NULL REFERENCES sources(source_id),
    author       TEXT,
    text_raw     TEXT,
    text_clean   TEXT,
    rating       REAL,
    likes        INTEGER,
    published_at TEXT
);
CREATE TABLE sentiment_results (
    review_id INTEGER PRIMARY KEY REFERENCES reviews(review_id),
    compound  REAL NOT NULL,
    label     TEXT NOT NULL
);
CREATE TABLE review_aspects (
    review_id INTEGER NOT NULL REFERENCES reviews(review_id),
    aspect_id INTEGER NOT NULL REFERENCES aspects(aspect_id),
    compound  REAL NOT NULL,
    label     TEXT NOT NULL
);
CREATE INDEX idx_reviews_product ON reviews(product_id);
"""


def main():
    rev = pd.read_csv(PROCESSED_DIR / "reviews_scored.csv")
    asp = pd.read_csv(PROCESSED_DIR / "aspects_scored.csv")

    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)

    products = pd.DataFrame(
        [(i + 1, n, s, y) for i, (n, (s, y)) in enumerate(PRODUCTS.items())],
        columns=["product_id", "name", "series", "release_year"])
    sources = pd.DataFrame({"name": sorted(rev["source"].dropna().unique())})
    sources.insert(0, "source_id", range(1, len(sources) + 1))
    aspects = pd.DataFrame({"name": list(ASPECTS)})
    aspects.insert(0, "aspect_id", range(1, len(aspects) + 1))
    for name, tbl in [("products", products), ("sources", sources), ("aspects", aspects)]:
        tbl.to_sql(name, con, if_exists="append", index=False)

    pid = dict(zip(products["name"], products["product_id"]))
    sid = dict(zip(sources["name"], sources["source_id"]))
    aid = dict(zip(aspects["name"], aspects["aspect_id"]))

    rev["product_id"] = rev["product"].map(pid)
    rev["source_id"] = rev["source"].map(sid)
    rev = rev.dropna(subset=["product_id", "source_id"]).astype({"product_id": int, "source_id": int})
    cols = ["review_id", "product_id", "source_id", "author", "text_raw",
            "text_clean", "rating", "likes", "published_at"]
    rev[cols].to_sql("reviews", con, if_exists="append", index=False)
    rev[["review_id", "compound", "sentiment"]].rename(columns={"sentiment": "label"}).to_sql(
        "sentiment_results", con, if_exists="append", index=False)

    asp = asp[asp["review_id"].isin(rev["review_id"])].copy()
    asp["aspect_id"] = asp["aspect"].map(aid)
    asp[["review_id", "aspect_id", "compound", "label"]].to_sql(
        "review_aspects", con, if_exists="append", index=False)

    con.commit()
    con.close()
    print(f"Database ready -> {DB_PATH}")


if __name__ == "__main__":
    main()
