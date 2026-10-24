# 🎧 Samsung Galaxy Buds: Sentiment Analysis & Comparison Dashboard

Big Data Analytics course project. We collect public comments/reviews about several
Samsung earbuds, clean them, run sentiment analysis (overall + per aspect such as
battery or sound), store everything in a relational database (see the ERD) and
show it in an interactive dashboard where a user can compare earbuds and find the best one.

## Pipeline
```
YouTube API ─┐
             ├─> data/raw/*.csv ─> clean.py ─> sentiment.py ─> database.py (SQLite) ─> Streamlit dashboard
Web scraping ┘
```

| Step | File | What it does |
|------|------|--------------|
| 1a | `src/collect_youtube.py` | Comments from YouTube review videos (official API) |
| 1b | `src/scrape_reviews.py` | Web scraping with requests + BeautifulSoup (respects robots.txt) |
| 2 | `src/clean.py` | Remove links, HTML, duplicates, very short comments |
| 3 | `src/sentiment.py` | VADER sentiment + aspect detection (sound, battery, ANC, comfort, ...) |
| 4 | `src/database.py` | Builds the SQLite database from the ERD |
| 5 | `dashboard/app.py` | Interactive comparison dashboard |

## ERD
See [`docs/erd.md`](docs/erd.md): tables `products`, `sources`, `reviews`, `sentiment_results`, `aspects`, `review_aspects`.

## Run in Google Colab
Open `notebooks/run_in_colab.ipynb` and run the cells top to bottom.

## Run on your computer
```bash
git clone https://github.com/<your-username>/galaxy-buds-sentiment.git
cd galaxy-buds-sentiment
pip install -r requirements.txt

# 1. get a YouTube Data API v3 key (Google Cloud Console) and set it
export YOUTUBE_API_KEY="your-key"        # Windows: set YOUTUBE_API_KEY=your-key

python src/collect_youtube.py            # collect comments
python src/scrape_reviews.py             # optional: web scraping (edit SITES first)
python src/run_pipeline.py               # clean + sentiment + database
streamlit run dashboard/app.py           # open the dashboard
```

### Just want to test the dashboard first?
```bash
python src/make_sample_data.py           # FAKE demo data
python src/run_pipeline.py
streamlit run dashboard/app.py
```
Delete `data/raw/sample_demo.csv` before collecting real data.

## Choosing earbuds
Edit the `PRODUCTS` dictionary in `src/config.py`.

## Limitations (mention these in your report)
- VADER is built for English; comments in other languages are scored poorly.
- Sarcasm is hard for lexicon-based sentiment.
- Aspect detection uses keywords, so it is approximate.
- YouTube comments reflect people who chose to comment, not all buyers.

## Ethics
Only public data, collected via an official API or from pages that allow it in robots.txt.
Author names are not used in the analysis.
