# Multi-Source Web Scraping & Data Consolidation Pipeline

A production-ready Python web scraping and data consolidation pipeline built to extract, sanitize, validate, deduplicate, and consolidate records from two public scraping practice websites: **Books to Scrape** and **Quotes to Scrape**.

---

## 1. Assignment Overview & Objective

The primary objective of this project is to create a robust, modular, and failure-resilient scraping pipeline that collects data from heterogeneous web sources with different HTML structures, maps them into a unified schema, performs data cleaning and validation, detects duplicates deterministically, and exports a clean CSV dataset alongside a JSON execution summary report.

### Key Highlights
- **Dynamic Pagination**: Scrapes multi-page websites automatically by inspecting and resolving `<li class="next">` pagination elements until no further pages remain.
- **Unified Standard Schema**: Normalizes source-specific fields into one common 10-field DataRecord model.
- **Sanitization & Validation**: Standardizes currency prices to numeric floats, converts textual star ratings (`One`..`Five`) to integers (`1`..`5`), strips surrounding decorative quotes, and validates mandatory fields.
- **Deterministic Deduplication**: Employs MD5 hash composite keys (`source` + `normalized title` + `normalized URL/author`) to identify duplicate records regardless of casing or leading/trailing whitespace.
- **Error Resilience**: Includes exponential backoff retries for HTTP failures and gracefully continues execution if individual page requests fail.

---

## 2. Architecture & Pipeline Workflow

```
┌────────────────────────┐      ┌────────────────────────┐
│   Books to Scrape      │      │    Quotes to Scrape    │
│ https://books.toscrape │      │ https://quotes.toscrape│
└───────────┬────────────┘      └───────────┬────────────┘
            │                               │
            ▼                               ▼
    [ BooksScraper ]                [ QuotesScraper ]
            │                               │
            └───────────────┬───────────────┘
                            │ (Raw DataRecords)
                            ▼
                  [ 1. Data Cleaning ]
                            │ (Sanitized DataRecords)
                            ▼
                 [ 2. Data Validation ]
                            │ (Valid DataRecords + Errors logged)
                            ▼
                [ 3. Deduplication ]
                            │ (Retained unique DataRecords)
                            ▼
              [ 4. Consolidation & Export ]
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
      output/final_dataset.csv   output/summary_report.json
```

---

## 3. Technologies Used & Dependencies

- **Python**: 3.11+
- **requests**: Synchronous HTTP requests with persistent `requests.Session`.
- **BeautifulSoup4 & lxml**: High-performance HTML parsing.
- **pandas**: Data manipulation, schema alignment, and CSV exporting.
- **pytest**: Automated unit testing with zero live website dependencies.

---

## 4. Project Structure

```
.
├── models/
│   ├── __init__.py
│   └── record.py             # Standardized DataRecord dataclass
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Dual console and file logger configuration
│   ├── http_client.py        # Requests session wrapper with retries & rate limiting
│   └── helpers.py            # URL resolution & composite hashing helpers
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py       # Abstract base scraper with pagination workflow
│   ├── books_scraper.py      # Books to Scrape scraper & detail fetcher
│   └── quotes_scraper.py     # Quotes to Scrape scraper
├── processing/
│   ├── __init__.py
│   ├── cleaning.py           # Text, price, rating, URL, and tag sanitization
│   ├── validation.py         # Schema validation & boundary enforcement
│   ├── deduplication.py      # Composite key hash deduplication engine
│   └── consolidation.py      # pandas export and summary report generator
├── output/
│   ├── final_dataset.csv     # Consolidated output CSV dataset
│   └── summary_report.json   # Execution metrics and summary JSON
├── logs/
│   └── scraper.log           # Execution log file
├── tests/
│   ├── __init__.py
│   ├── test_cleaning.py      # Unit tests for cleaning utilities
│   ├── test_validation.py    # Unit tests for schema validation rules
│   ├── test_deduplication.py # Unit tests for composite deduplication
│   ├── test_books_scraper.py # Offline unit test with mock HTML
│   └── test_quotes_scraper.py# Offline unit test with mock HTML
├── main.py                   # Main pipeline entry point & CLI runner
├── config.py                 # Centralized configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── AI_USAGE.md               # AI assistance disclosure & verification record
└── .gitignore                # Git ignore configuration
```

---

## 5. Installation & Setup Instructions

### Prerequisites
- Python 3.11 or higher installed on your system.

### Virtual Environment Setup

#### Windows (Command Prompt / PowerShell)
```cmd
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. How to Run the Scraper

### Full Pipeline Run (All Sources, All Pages)
```bash
python main.py
```

### CLI Command Options

#### Scrape a Specific Source
```bash
# Scrape only Books to Scrape
python main.py --source books

# Scrape only Quotes to Scrape
python main.py --source quotes
```

#### Limit Pages for Quick Testing
```bash
python main.py --max-pages 2
```

#### Speed Up Books Scraping (Skip Detail Pages)
```bash
python main.py --no-details --max-pages 3
```

#### Custom Request Delay
```bash
python main.py --delay 0.5
```

---

## 7. How Pagination Works

Pagination is dynamically resolved without hard-coding total page counts:
1. The scraper fetches the current page HTML.
2. It looks for the next page link (`li.next > a`).
3. If present, the relative `href` (e.g. `page-2.html`) is converted into an absolute URL using `urllib.parse.urljoin`.
4. The URL is checked against `self.visited_urls` set to prevent infinite loops.
5. The loop continues until no next page link is found.

---

## 8. Data Model & Field Mapping

| Field Name | Standard Type | Books to Scrape Source | Quotes to Scrape Source |
|---|---|---|---|
| `source` | `str` | `"Books to Scrape"` | `"Quotes to Scrape"` |
| `source_url` | `str` | Product detail URL | Quote listing URL |
| `name_or_title` | `str` | Book Title | Quote Text |
| `category` | `Optional[str]` | Breadcrumb Category | `None` |
| `price` | `Optional[float]` | Float (e.g., `51.77`) | `None` |
| `rating` | `Optional[int]` | Integer `1`..`5` | `None` |
| `author` | `Optional[str]` | `None` | Quote Author |
| `tags` | `Optional[str]` | `None` | Comma-separated tags |
| `description` | `Optional[str]` | Product Description | `None` |
| `scraped_at` | `str` | UTC ISO 8601 Timestamp | UTC ISO 8601 Timestamp |

---

## 9. Cleaning, Validation & Deduplication Approach

### Data Cleaning (`processing/cleaning.py`)
- **Whitespace**: Collapses multiple whitespace characters and strips leading/trailing spaces.
- **Quotes**: Removes decorative surrounding quotes (`“`, `”`, `"`) from quote text.
- **Price**: Strips currency symbols (`£`, `$`) using regular expressions and parses floats.
- **Rating**: Maps word ratings (`One`, `Two`, `Three`, `Four`, `Five`) to integers `1..5`.
- **Missing Values**: Converts sentinel strings (`"N/A"`, `"none"`, `""`) to `None`.

### Validation (`processing/validation.py`)
- Enforces mandatory existence of `source`, `source_url`, `name_or_title`, and `scraped_at`.
- Validates that `source_url` starts with `http://` or `https://`.
- Ensures `price >= 0` and `1 <= rating <= 5`.
- Invalid records are flagged, logged, and excluded from the final dataset.

### Deduplication (`processing/deduplication.py`)
- Generates a composite hash for each record:
  - **Books**: `MD5(source + normalized_title + normalized_product_url)`
  - **Quotes**: `MD5(source + normalized_quote_text + normalized_author)`
- Strips whitespace and lowercases string fields prior to hashing so that `"EXAMPLE TITLE"` and `" example title "` yield identical duplicate keys.

---

## 10. Output Description

### Consolidated Dataset (`output/final_dataset.csv`)
Contains all cleaned, validated, and deduplicated records in standard column order.

### Summary Report (`output/summary_report.json`)
```json
{
    "execution_started_at": "2026-10-06T13:50:00.000000+00:00",
    "execution_finished_at": "2026-10-06T13:50:45.000000+00:00",
    "execution_time_seconds": 45.2,
    "sources": {
        "Books to Scrape": {
            "records_collected": 1000,
            "records_after_cleaning": 1000,
            "records_rejected": 0,
            "duplicates_detected": 0,
            "final_records": 1000
        },
        "Quotes to Scrape": {
            "records_collected": 100,
            "records_after_cleaning": 100,
            "records_rejected": 0,
            "duplicates_detected": 0,
            "final_records": 100
        }
    },
    "total_records_collected": 1100,
    "total_records_cleaned": 1100,
    "total_records_rejected": 0,
    "total_duplicates": 0,
    "final_record_count": 1100,
    "errors": []
}
```

---

## 11. Automated Testing

The unit test suite uses `pytest` and offline HTML mock fixtures, ensuring zero external network dependency during testing.

Run tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

---

## 12. Interview Discussion Points

1. **Why Requests + BeautifulSoup?**
   - Both target websites deliver static HTML content. Using a headless browser (Selenium/Playwright) would introduce unnecessary CPU overhead and dependency bloat.
2. **How does pagination work?**
   - The scrapers extract relative pagination links dynamically, convert them to absolute URLs via `urljoin`, and track visited URLs to avoid infinite loops.
3. **How are failed requests handled?**
   - HTTPClient uses `urllib3.util.Retry` for exponential backoff on retryable status codes (429, 500, 502, 503, 504). If a request ultimately fails, the error is logged and execution continues with remaining pages.
4. **How does deduplication work?**
   - Uses an MD5 hash of lowercased and stripped composite keys (`source` + `title` + `url/author`) to reliably identify duplicate entries.
5. **What would change for a production environment?**
   - Implement asynchronous crawling with `aiohttp` or `Scrapy` for higher throughput.
   - Use distributed task queues (Celery / Redis) for queue management.
   - Store records in PostgreSQL or MongoDB.
