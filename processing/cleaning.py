import re
from typing import Optional, Any
from models.record import DataRecord
from utils.helpers import is_valid_url

# Rating text mapping
RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def normalize_missing_value(val: Any) -> Any:
    """Converts missing-value sentinel strings (e.g. 'N/A', 'none', '') to None."""
    if val is None:
        return None
    if isinstance(val, str):
        cleaned = val.strip()
        if cleaned.lower() in ("", "n/a", "none", "null", "nan", "undefined"):
            return None
        return cleaned
    return val


def clean_text(val: Optional[str], strip_quotes: bool = False) -> Optional[str]:
    """Cleans text by collapsing whitespace, stripping whitespace, and optionally removing quotes."""
    val = normalize_missing_value(val)
    if not val or not isinstance(val, str):
        return None

    # Collapse repeated whitespace
    cleaned = re.sub(r"\s+", " ", val).strip()

    if strip_quotes:
        # Strip decorative surrounding quotes
        cleaned = re.sub(r"^[“\"']|[”\"']$", "", cleaned).strip()

    return cleaned if cleaned else None


def clean_price(val: Any) -> Optional[float]:
    """Extracts numeric float price from string or number, removing currency symbols."""
    val = normalize_missing_value(val)
    if val is None:
        return None

    if isinstance(val, (int, float)):
        return float(val) if val >= 0 else None

    # String parsing
    str_val = str(val).strip()
    # Match optional leading negative sign and decimal pattern
    match = re.search(r"(-?\d+(?:\.\d+)?)", str_val)
    if match:
        try:
            parsed = float(match.group(1))
            return parsed if parsed >= 0 else None
        except ValueError:
            return None
    return None


def clean_rating(val: Any) -> Optional[int]:
    """Standardizes rating values (textual or numeric) into an integer between 1 and 5."""
    val = normalize_missing_value(val)
    if val is None:
        return None

    # Check textual ratings
    if isinstance(val, str):
        str_val = val.strip().lower()
        if str_val in RATING_MAP:
            return RATING_MAP[str_val]

    # Check numeric conversion
    try:
        num = int(float(str(val).strip()))
        if 1 <= num <= 5:
            return num
    except (ValueError, TypeError):
        pass

    return None


def clean_url(val: Optional[str]) -> Optional[str]:
    """Normalizes and validates URL strings."""
    cleaned = clean_text(val)
    if cleaned and is_valid_url(cleaned):
        return cleaned
    return None


def clean_tags(val: Optional[str]) -> Optional[str]:
    """Normalizes tags into a clean comma-separated string."""
    val = normalize_missing_value(val)
    if not val or not isinstance(val, str):
        return None

    # Split by comma
    raw_tags = val.split(",")
    cleaned_tags = []
    for tag in raw_tags:
        ct = clean_text(tag)
        if ct:
            cleaned_tags.append(ct)

    return ", ".join(cleaned_tags) if cleaned_tags else None


def clean_record(record: DataRecord) -> DataRecord:
    """Returns a new DataRecord with all fields sanitized and normalized."""
    is_quote = "quote" in record.source.lower()

    cleaned_title = clean_text(record.name_or_title, strip_quotes=is_quote)
    cleaned_source = clean_text(record.source)
    cleaned_url = clean_url(record.source_url) or record.source_url
    cleaned_category = clean_text(record.category)
    cleaned_price_val = clean_price(record.price)
    cleaned_rating_val = clean_rating(record.rating)
    cleaned_author = clean_text(record.author)
    cleaned_tags_val = clean_tags(record.tags)
    cleaned_desc = clean_text(record.description)

    return DataRecord(
        source=cleaned_source or record.source,
        source_url=cleaned_url,
        name_or_title=cleaned_title or "",
        category=cleaned_category,
        price=cleaned_price_val,
        rating=cleaned_rating_val,
        author=cleaned_author,
        tags=cleaned_tags_val,
        description=cleaned_desc,
        scraped_at=record.scraped_at
    )
