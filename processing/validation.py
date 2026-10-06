from dataclasses import dataclass, field
from typing import List
from models.record import DataRecord
from utils.helpers import is_valid_url
from config import SOURCE_BOOKS, SOURCE_QUOTES


@dataclass
class ValidationResult:
    """Holds the result of validating a DataRecord."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    record: DataRecord = None


VALID_SOURCES = {SOURCE_BOOKS, SOURCE_QUOTES}


def validate_record(record: DataRecord) -> ValidationResult:
    """Validates a DataRecord against defined schema and range constraints."""
    errors: List[str] = []

    # 1. Source Validation
    if not record.source or not record.source.strip():
        errors.append("Missing required field: 'source'")
    elif record.source not in VALID_SOURCES:
        errors.append(f"Unrecognized source: '{record.source}'")

    # 2. Source URL Validation
    if not record.source_url or not record.source_url.strip():
        errors.append("Missing required field: 'source_url'")
    elif not is_valid_url(record.source_url):
        errors.append(f"Invalid source_url format: '{record.source_url}'")

    # 3. Name / Title Validation
    if not record.name_or_title or not record.name_or_title.strip():
        errors.append("Missing required field: 'name_or_title'")

    # 4. Price Validation (if present)
    if record.price is not None:
        if not isinstance(record.price, (int, float)):
            errors.append(f"Price must be numeric, got: {type(record.price).__name__}")
        elif record.price < 0:
            errors.append(f"Price cannot be negative: {record.price}")

    # 5. Rating Validation (if present)
    if record.rating is not None:
        if not isinstance(record.rating, int):
            errors.append(f"Rating must be an integer, got: {type(record.rating).__name__}")
        elif not (1 <= record.rating <= 5):
            errors.append(f"Rating must be between 1 and 5, got: {record.rating}")

    # 6. Timestamp Validation
    if not record.scraped_at or not isinstance(record.scraped_at, str):
        errors.append("Missing or invalid 'scraped_at' timestamp")

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        record=record
    )
