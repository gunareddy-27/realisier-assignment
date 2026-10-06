import logging
from typing import List, Set, Tuple, Dict
from models.record import DataRecord
from utils.helpers import compute_composite_hash
from config import SOURCE_BOOKS, SOURCE_QUOTES

logger = logging.getLogger("scraper_pipeline")


class Deduplicator:
    """Handles identification and removal of duplicate records based on source-specific normalized composite keys."""

    def __init__(self):
        self.seen_keys: Set[str] = set()

    def generate_dedup_key(self, record: DataRecord) -> str:
        """Generates a deterministic composite key for a record using normalized fields."""
        norm_source = record.source.strip().lower()
        norm_title = record.name_or_title.strip().lower()

        if record.source == SOURCE_BOOKS:
            # For Books: source + normalized title + normalized product url
            norm_url = (record.source_url or "").strip().lower()
            key_parts = [norm_source, norm_title, norm_url]
        elif record.source == SOURCE_QUOTES:
            # For Quotes: source + normalized quote text + normalized author
            norm_author = (record.author or "").strip().lower()
            key_parts = [norm_source, norm_title, norm_author]
        else:
            # Fallback for generic sources
            norm_url = (record.source_url or "").strip().lower()
            key_parts = [norm_source, norm_title, norm_url]

        return compute_composite_hash(key_parts)

    def process(self, records: List[DataRecord]) -> Tuple[List[DataRecord], List[DataRecord], Dict[str, int]]:
        """Processes a list of DataRecord objects, returning (retained_records, duplicate_records, per_source_counts)."""
        retained: List[DataRecord] = []
        duplicates: List[DataRecord] = []
        dup_counts_by_source: Dict[str, int] = {}

        for record in records:
            key = self.generate_dedup_key(record)
            if key in self.seen_keys:
                duplicates.append(record)
                dup_counts_by_source[record.source] = dup_counts_by_source.get(record.source, 0) + 1
                logger.debug(f"Duplicate detected for [{record.source}]: '{record.name_or_title}'")
            else:
                self.seen_keys.add(key)
                retained.append(record)

        logger.info(
            f"Deduplication completed. "
            f"Retained: {len(retained)}, Duplicates removed: {len(duplicates)}"
        )
        return retained, duplicates, dup_counts_by_source
