import sys
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

from config import (
    BOOKS_BASE_URL,
    QUOTES_BASE_URL,
    SOURCE_BOOKS,
    SOURCE_QUOTES,
    CSV_OUTPUT_PATH,
    SUMMARY_OUTPUT_PATH,
    LOG_FILE_PATH,
    REQUEST_DELAY
)
from utils.logger import setup_logger
from utils.http_client import HTTPClient
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from models.record import DataRecord
from processing.cleaning import clean_record
from processing.validation import validate_record
from processing.deduplication import Deduplicator
from processing.consolidation import consolidate_records, generate_summary_report


def parse_args() -> argparse.Namespace:
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-Source Web Scraping & Data Consolidation Pipeline"
    )
    parser.add_argument(
        "--source",
        choices=["all", "books", "quotes"],
        default="all",
        help="Specify which source to scrape (default: 'all')"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY,
        help=f"Politeness request delay in seconds (default: {REQUEST_DELAY})"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to scrape per source (default: all pages)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom directory for output CSV and summary JSON"
    )
    parser.add_argument(
        "--no-details",
        action="store_true",
        help="Disable detail page fetching for books scraper to speed up execution"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Determine paths
    output_dir = Path(args.output_dir) if args.output_dir else CSV_OUTPUT_PATH.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "final_dataset.csv"
    summary_path = output_dir / "summary_report.json"

    # Setup logger
    logger = setup_logger("scraper_pipeline", log_file=LOG_FILE_PATH)
    logger.info("Initializing Web Scraping Pipeline")

    start_time = time.time()
    execution_started_at = datetime.now(timezone.utc).isoformat()

    # Initialize HTTP client
    http_client = HTTPClient(delay=args.delay)

    # Tracking counters
    sources_metrics: Dict[str, Dict[str, int]] = {
        SOURCE_BOOKS: {
            "records_collected": 0,
            "records_after_cleaning": 0,
            "records_rejected": 0,
            "duplicates_detected": 0,
            "final_records": 0
        },
        SOURCE_QUOTES: {
            "records_collected": 0,
            "records_after_cleaning": 0,
            "records_rejected": 0,
            "duplicates_detected": 0,
            "final_records": 0
        }
    }
    all_raw_records: List[DataRecord] = []
    collected_errors: List[str] = []

    try:
        # Step 1: Execute Scrapers
        if args.source in ("all", "books"):
            books_scraper = BooksScraper(http_client, fetch_details=not args.no_details)
            books_records = books_scraper.run(BOOKS_BASE_URL, max_pages=args.max_pages)
            all_raw_records.extend(books_records)
            sources_metrics[SOURCE_BOOKS]["records_collected"] = len(books_records)
            collected_errors.extend(books_scraper.errors)

        if args.source in ("all", "quotes"):
            quotes_scraper = QuotesScraper(http_client)
            quotes_records = quotes_scraper.run(QUOTES_BASE_URL, max_pages=args.max_pages)
            all_raw_records.extend(quotes_records)
            sources_metrics[SOURCE_QUOTES]["records_collected"] = len(quotes_records)
            collected_errors.extend(quotes_scraper.errors)

        logger.info(f"Scraping phase complete. Total raw records collected: {len(all_raw_records)}")

        # Step 2: Cleaning Phase
        logger.info("Starting Data Cleaning Phase...")
        cleaned_records: List[DataRecord] = []
        for raw_rec in all_raw_records:
            cleaned = clean_record(raw_rec)
            cleaned_records.append(cleaned)
            if cleaned.source in sources_metrics:
                sources_metrics[cleaned.source]["records_after_cleaning"] += 1

        # Step 3: Validation Phase
        logger.info("Starting Data Validation Phase...")
        validated_records: List[DataRecord] = []
        for cleaned_rec in cleaned_records:
            val_res = validate_record(cleaned_rec)
            if val_res.is_valid:
                validated_records.append(cleaned_rec)
            else:
                if cleaned_rec.source in sources_metrics:
                    sources_metrics[cleaned_rec.source]["records_rejected"] += 1
                err_msg = f"Validation failed for [{cleaned_rec.source}] '{cleaned_rec.name_or_title}': {val_res.errors}"
                logger.warning(err_msg)
                collected_errors.append(err_msg)

        # Step 4: Deduplication Phase
        logger.info("Starting Deduplication Phase...")
        deduper = Deduplicator()
        final_records, duplicate_records, dup_counts = deduper.process(validated_records)

        for src, dup_count in dup_counts.items():
            if src in sources_metrics:
                sources_metrics[src]["duplicates_detected"] = dup_count

        # Compute per-source final record counts
        for rec in final_records:
            if rec.source in sources_metrics:
                sources_metrics[rec.source]["final_records"] += 1

        # Step 5: Export to CSV
        logger.info("Consolidating data and exporting to CSV...")
        consolidate_records(final_records, csv_path=csv_path)

        # Step 6: Generate JSON Summary Report
        execution_finished_at = datetime.now(timezone.utc).isoformat()
        elapsed_seconds = round(time.time() - start_time, 2)

        total_collected = sum(m["records_collected"] for m in sources_metrics.values())
        total_cleaned = sum(m["records_after_cleaning"] for m in sources_metrics.values())
        total_rejected = sum(m["records_rejected"] for m in sources_metrics.values())
        total_duplicates = sum(m["duplicates_detected"] for m in sources_metrics.values())
        final_count = len(final_records)

        summary_data: Dict[str, Any] = {
            "execution_started_at": execution_started_at,
            "execution_finished_at": execution_finished_at,
            "execution_time_seconds": elapsed_seconds,
            "sources": sources_metrics,
            "total_records_collected": total_collected,
            "total_records_cleaned": total_cleaned,
            "total_records_rejected": total_rejected,
            "total_duplicates": total_duplicates,
            "final_record_count": final_count,
            "errors": collected_errors
        }
        generate_summary_report(summary_data, summary_path)

        # Final Summary Console Output
        print("\n" + "=" * 40)
        print("SCRAPING COMPLETED")
        print("=" * 40)
        print(f"Books collected: {sources_metrics[SOURCE_BOOKS]['records_collected']}")
        print(f"Quotes collected: {sources_metrics[SOURCE_QUOTES]['records_collected']}")
        print(f"\nRecords after cleaning: {total_cleaned}")
        print(f"Invalid records: {total_rejected}")
        print(f"Duplicates detected: {total_duplicates}")
        print(f"Final records: {final_count}")
        print(f"\nCSV: {csv_path}")
        print(f"Summary: {summary_path}")
        print(f"Log: {LOG_FILE_PATH}")
        print("=" * 40 + "\n")

    finally:
        http_client.close()


if __name__ == "__main__":
    main()
