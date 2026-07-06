import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "signals.db"
CONFIG_DIR = BASE_DIR / "config"

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

try:
    import streamlit as st
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    if "APOLLO_API_KEY" in st.secrets:
        os.environ["APOLLO_API_KEY"] = st.secrets["APOLLO_API_KEY"]
except Exception:
    pass

# Groq Config (Reads from .env, GitHub Secrets, or Streamlit Secrets)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ""
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
