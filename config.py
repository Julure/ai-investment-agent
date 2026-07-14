"""Main configuration and connections
- rate limit
- model names
- paths """

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

#--- API keys ---

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SEC_EDGAR_CONTACT = os.getenv("SEC_EDGAR_CONTACT")

if not GROQ_API_KEY:
    raise RuntimeError (
    "GROQ_API_KEY is not set. please make sure .env is created and GROQ_API_KEY is set"
    )


# --- Models ---

MODEL_FAST = "llama-3.1-8b-instant" #query generation and condensing raw source data 

MODEL_SMART = "llama-3.3-70b-versatile" # smarter model for the final synthesis step with reasoning

# --- Rate Limit ---

MIN_SECONDS_BETWEEN_CALLS = 2.5
MAX_RETRIES = 5
RETRY_BACKOFF_SECONDS = 8

# --- Paths ---
ROOT_DIR = Path(__file__).parent
CACHE_DB_PATH = ROOT_DIR / "cache" / "cache.sqlite3"
REPORTS_DIR = ROOT_DIR / "reports"
PROMPTS_DIR = ROOT_DIR / "prompts"

REPORTS_DIR.mkdir(exist_ok=True)
