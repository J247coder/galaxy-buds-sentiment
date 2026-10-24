"""Streamlit dashboard: compare Samsung earbuds by what people say about them.

Run:  streamlit run dashboard/app.py
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
from config import DB_PATH  # noqa: E402

st.set_page_config(page_title="Galaxy Buds Comparison", page_icon="🎧", layout="wide")
COLORS = {"Positive": "#2e9e6b", "Neutral": "#9aa3ad", "Negative": "#d9534f"}


@st.cache_data
def load():
    con = sqlite3.connect(DB_PATH)
    reviews = pd.read_sql("""
        SELECT r.review_id, p.name AS product, s.name AS source, r.text_clean,
               r.likes, r.published_at, sr.compound, sr.label
        FROM reviews r
        JOIN products p ON p.product_id = r.product_id
        JOIN sources  s ON s.source_id  = r.source_id
        JOIN sentiment_results sr ON sr.review_id = r.review_id""", con)
    aspects = pd.read_sql("""
        SELECT p.name AS product, a.name AS aspect, ra.compound, ra.label
        FROM review_aspects ra
        JOIN reviews r  ON r.review_id  = ra.review_id
        JOIN products p ON p.product_id = r.product_id
        JOIN aspects a  ON a.aspect_id  = ra.aspect_id""", con)
    con.close()
    reviews["published_at"] = pd.to_datetime(reviews["published_at"], errors="coerce", utc=True)
    return reviews, aspects


if not DB_PATH.exists():
    st.error("Database not found. Run `python src/run_pipeline.py` first.")
    st.stop()

reviews, aspects = load()
st.title("🎧 Samsung Galaxy Buds: which one is better?")
st.caption("Based on sentiment analysis of public comments and reviews.")

# ---------- sidebar ----------
all_products = sorted(reviews["product"].unique())
chosen = st.sidebar.multiselect("Choose earbuds to compare", all_products, default=all_products)
sources = st.sidebar.multiselect("Sources", sorted(reviews["source"].unique()),
                                 default=sorted(reviews["source"].unique()))
rv = reviews[reviews["product"].isin(chosen) & reviews["source"].isin(sources)]
asp = aspects[aspects["product"].isin(chosen)]
if rv.empty:
    st.warning("Select at least one earbud.")
    st.stop()

# ---------- KPIs ----------
summary = (rv.groupby("product")
             .agg(comments=("review_id", "count"),
                  avg_score=("compound", "mean"),
                  pct_positive=("label", lambda s: (s == "Positive").mean() * 100),
                  pct_negative=("label", lambda s: (s == "Negative").mean() * 100))
             .sort_values("avg_score", ascending=False).reset_index())
best = summary.iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Comments analysed", f"{len(rv):,}")
c2.metric("Earbuds compared", len(summary))
c3.metric("Highest sentiment", best["product"], f"{best['pct_positive']:.0f}% positive")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Aspects", "Find my best pair", "Read comments"])

# ---------- Overview ----------
with tab1:
    left, right = st.columns(2)
    dist = rv.groupby(["product", "label"]).size().reset_index(name="n")
    dist["pct"] = dist["n"] / dist.groupby("product")["n"].transform("sum") * 100
    fig = px.bar(dist, x="product", y="pct", color="label", color_discrete_map=COLORS,
                 title="Sentiment split (%)", labels={"pct": "% of comments", "product": ""},
                 category_orders={"label": ["Positive", "Neutral", "Negative"]})
    left.plotly_chart(fig, use_container_width=True)
    fig = px.bar(summary, x="product", y="avg_score", color="avg_score",
                 color_continuous_scale="RdYlGn", range_color=[-1, 1],
                 title="Average sentiment score (-1 to +1)", labels={"avg_score": "score", "product": ""})
    right.plotly_chart(fig, use_container_width=True)

    trend = rv.dropna(subset=["published_at"]).copy()
    if not trend.empty:
        trend["month"] = trend["published_at"].dt.tz_localize(None).dt.to_period("M").dt.to_timestamp()
        t = trend.groupby(["month", "product"])["compound"].mean().reset_index()
        st.plotly_chart(px.line(t, x="month", y="compound", color="product", markers=True,
                                title="Sentiment over time", labels={"compound": "avg score"}),
                        use_container_width=True)
    st.dataframe(summary.round(2), use_container_width=True, hide_index=True)

# ---------- Aspects ----------
with tab2:
    if asp.empty:
        st.info("No aspect mentions found.")
    else:
        piv = asp.pivot_table(index="aspect", columns="product", values="compound", aggfunc="mean")
        st.plotly_chart(px.imshow(piv, color_continuous_scale="RdYlGn", zmin=-1, zmax=1, aspect="auto",
                                  text_auto=".2f", title="Sentiment by aspect (green = liked)"),
                        use_container_width=True)
        counts = asp.groupby(["aspect", "product"]).size().reset_index(name="mentions")
        st.plotly_chart(px.bar(counts, x="aspect", y="mentions", color="product", barmode="group",
                               title="How often each aspect is discussed"), use_container_width=True)

# ---------- Recommender ----------
with tab3:
    st.write("Move the sliders to show what matters to **you**. The ranking updates automatically.")
    piv = asp.pivot_table(index="product", columns="aspect", values="compound", aggfunc="mean")
    if piv.empty:
        st.info("Not enough aspect data.")
    else:
        cols = st.columns(4)
        weights = {a: cols[i % 4].slider(a, 0, 5, 3) for i, a in enumerate(piv.columns)}
        total = sum(weights.values())
        if total == 0:
            st.warning("Set at least one slider above 0.")
        else:
            score = sum(piv[a].fillna(0) * w for a, w in weights.items()) / total
            rank = score.sort_values(ascending=False).reset_index()
            rank.columns = ["product", "your_score"]
            rank["your_score"] = rank["your_score"].round(3)
            st.success(f"🏆 Best match for you: **{rank.iloc[0]['product']}**")
            st.plotly_chart(px.bar(rank, x="your_score", y="product", orientation="h",
                                   color="your_score", color_continuous_scale="RdYlGn",
                                   range_color=[-1, 1]), use_container_width=True)

# ---------- Comments ----------
with tab4:
    prod = st.selectbox("Earbud", chosen)
    lab = st.radio("Sentiment", ["Positive", "Neutral", "Negative"], horizontal=True)
    sub = rv[(rv["product"] == prod) & (rv["label"] == lab)].sort_values("likes", ascending=False)
    st.dataframe(sub[["text_clean", "likes", "compound"]].head(50), use_container_width=True, hide_index=True)
