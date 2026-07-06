import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "signals.db"
CONFIG_DIR = BASE_DIR / "config"

# Groq Config
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or "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"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Apollo Config
APOLLO_API_KEY = os.environ.get("APOLLO_API_KEY") or "TvrDdUxy6_yrwvX8xS8e4Q"
APOLLO_BASE_URL = "https://api.apollo.io/v1"

# Scraping Sources
RSS_FEEDS = {
    "Inc42": "https://inc42.com/feed",
    "YourStory": "https://yourstory.com/feed",
    "ETHealthworld": "https://health.economictimes.indiatimes.com/rss"
}
