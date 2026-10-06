import os
from pathlib import Path

# Base URLs
BOOKS_BASE_URL = "https://books.toscrape.com/"
QUOTES_BASE_URL = "https://quotes.toscrape.com/"

# HTTP Client Configuration
REQUEST_TIMEOUT = 15  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0
REQUEST_DELAY = 0.2  # delay between requests in seconds to respect server rates
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Base Paths (relative to project root)
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# Output Files
CSV_OUTPUT_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "summary_report.json"
LOG_FILE_PATH = LOG_DIR / "scraper.log"

# Source Names
SOURCE_BOOKS = "Books to Scrape"
SOURCE_QUOTES = "Quotes to Scrape"

# Ensure required directories exist when config is imported
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
