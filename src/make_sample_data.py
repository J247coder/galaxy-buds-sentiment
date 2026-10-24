"""DEMO ONLY: makes FAKE comments so you can test the pipeline + dashboard
before real collection. Delete data/raw/sample_demo.csv before using real data!"""
import random
import pandas as pd
from config import PRODUCTS, RAW_DIR

random.seed(7)
POS = ["The sound quality is amazing and the bass is great.",
       "Battery lasts all day, really happy with it.",
       "Noise cancellation works perfectly on my commute.",
       "Super comfortable fit, I forget I am wearing them.",
       "Great value for the price, worth every penny.",
       "Call quality and the mic are very clear."]
NEG = ["The battery drains too fast, very disappointed.",
       "Connection keeps dropping and the lag is annoying.",
       "They hurt my ears after an hour, poor fit.",
       "Too expensive for what you get.",
       "The mic is terrible on calls.",
       "Noise cancelling is weak and the sound is flat."]
NEU = ["I bought these last week for my phone.", "Does it work with an iPhone or not?",
       "Watching this review before I decide."]
BIAS = {"Galaxy Buds FE": .55, "Galaxy Buds2": .6, "Galaxy Buds2 Pro": .72,
        "Galaxy Buds3": .6, "Galaxy Buds3 Pro": .68}

rows = []
for p in PRODUCTS:
    for i in range(300):
        r = random.random()
        pool = POS if r < BIAS[p] else NEG if r < BIAS[p] + .28 else NEU
        txt = " ".join(random.sample(pool, k=random.choice([1, 2])))
        rows.append(dict(product=p, source="YouTube", author=f"user{i}", text_raw=txt + f" ({p} #{i})",
                         likes=random.randint(0, 30),
                         published_at=f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}T10:00:00Z"))
pd.DataFrame(rows).to_csv(RAW_DIR / "sample_demo.csv", index=False)
print("Wrote data/raw/sample_demo.csv (FAKE demo data)")
