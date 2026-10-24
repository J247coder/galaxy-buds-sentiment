"""Central settings. Change the earbud list here and everything else follows."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "earbuds.db"

# product name -> (series, release_year)  -- edit freely
PRODUCTS = {
    "Galaxy Buds FE":   ("FE", 2023),
    "Galaxy Buds2":     ("Buds2", 2021),
    "Galaxy Buds2 Pro": ("Buds2", 2022),
    "Galaxy Buds3":     ("Buds3", 2024),
    "Galaxy Buds3 Pro": ("Buds3", 2024),
}

# How many YouTube videos per product and comments per video
VIDEOS_PER_PRODUCT = 5
COMMENTS_PER_VIDEO = 150

# Words that tell us which aspect a sentence talks about
ASPECTS = {
    "Sound quality":      ["sound", "bass", "treble", "audio", "music", "clarity", "volume"],
    "Battery":            ["battery", "charge", "charging", "last", "hours"],
    "Noise cancellation": ["anc", "noise", "ambient"],
    "Comfort & fit":      ["comfort", "fit", "ear", "tip", "pain", "hurt", "wear"],
    "Mic & calls":        ["mic", "microphone", "call", "calls", "voice"],
    "Connectivity":       ["bluetooth", "connect", "connection", "pair", "lag", "latency", "disconnect"],
    "Price & value":      ["price", "cheap", "expensive", "worth", "value", "money", "deal"],
    "Design & build":     ["design", "look", "case", "build", "color", "colour", "quality"],
}
