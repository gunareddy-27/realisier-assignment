# AI Usage Disclosure Document

## 1. Overview & AI Tools Used
- **Primary AI Tool**: Gemini 3.6 Flash / ChatGPT
- **Role of AI**: Architecture planning, generating initial regex patterns, suggesting test fixtures, writing initial boilerplate, and formatting documentation.

---

## 2. Specific AI Assistance Breakdown

| Component | AI Assistance Level | Details |
|---|---|---|
| **Architecture Design** | High | Assisted in designing the 10-field DataRecord schema and module layout. |
| **Scraper Implementation** | Medium | Generated initial HTML selector parsing for BeautifulSoup. |
| **Cleaning & Validation** | Medium | Provided regular expression patterns for currency and rating word mapping. |
| **Deduplication Engine** | Medium | Suggested MD5 composite key hashing approach. |
| **Test Suite** | High | Generated HTML mock strings for pytest fixtures. |
| **Documentation** | High | Drafted structural outline for README.md. |

---

## 3. Representative Prompts

### Prompt 1 (Data Normalization)
> "Write a Python function to clean prices from strings like '£51.77' or '$19.99' into floats, handle missing values like 'N/A' or empty strings, and return None if invalid."

### Prompt 2 (Deduplication)
> "How can I implement deterministic duplicate detection for web scraped records from two different sources using Python dataclasses without relying only on raw title comparison?"

### Prompt 3 (Test Fixtures)
> "Generate pytest mock HTML unit test cases for testing a BeautifulSoup scraper offline without making live network calls."

---

## 4. Manual Review, Modifications & Verification

### Issues Discovered & Corrected from Initial Suggestions
1. **Relative URL Resolution**: Initial AI code used simple string concatenation for pagination URLs, which broke when navigating nested directory paths (e.g. `catalogue/page-2.html`). Modified to use `urllib.parse.urljoin(base_url, relative_url)` via `make_absolute_url`.
2. **Book Detail Page Error Handling**: AI generated detail page fetching that assumed every book pod would have a valid detail URL. Refactored `_fetch_book_details` with fallback `try-except` blocks and optional flag `--no-details`.
3. **Rating Class Parsing**: Initial AI selector looked for `p.star-rating.text`. The actual site stores star ratings as CSS class names (`star-rating Three`). Corrected parsing to extract class lists and inspect secondary class names.

---

## 5. Verification & Testing Procedure

- Executed `pytest` unit test suite covering all cleaning, validation, deduplication, and offline HTML parsing.
- Executed `python main.py --max-pages 2` to test quick pipeline execution and verify creation of `output/final_dataset.csv`, `output/summary_report.json`, and `logs/scraper.log`.
- Executed full pipeline `python main.py` to collect live data from both sources and verify output correctness.
