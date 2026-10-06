import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from models.record import DataRecord
from config import CSV_OUTPUT_PATH, SUMMARY_OUTPUT_PATH

logger = logging.getLogger("scraper_pipeline")

STANDARD_COLUMNS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at"
]


def records_to_dataframe(records: List[DataRecord]) -> pd.DataFrame:
    """Converts a list of DataRecord objects into a pandas DataFrame with standard column order."""
    if not records:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    dict_records = [r.to_dict() for r in records]
    df = pd.DataFrame(dict_records)

    # Reorder and ensure all standard columns exist
    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = None

    return df[STANDARD_COLUMNS]


def export_to_csv(records: List[DataRecord], output_path: Path = CSV_OUTPUT_PATH) -> Path:
    """Exports consolidated records to CSV file using UTF-8 encoding."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df = records_to_dataframe(records)
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Successfully exported {len(records)} records to CSV at: {output_path}")
    return output_path


def generate_summary_report(
    summary_data: Dict[str, Any],
    output_path: Path = SUMMARY_OUTPUT_PATH
) -> Path:
    """Generates and writes the JSON summary report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)
    logger.info(f"Summary report written to: {output_path}")
    return output_path


def consolidate_records(
    records: List[DataRecord],
    csv_path: Path = CSV_OUTPUT_PATH
) -> pd.DataFrame:
    """Consolidates and exports records to CSV, returning the resulting DataFrame."""
    export_to_csv(records, csv_path)
    return records_to_dataframe(records)
