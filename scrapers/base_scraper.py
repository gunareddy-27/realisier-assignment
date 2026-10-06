import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Set
from bs4 import BeautifulSoup

from models.record import DataRecord
from utils.http_client import HTTPClient
from utils.helpers import make_absolute_url

logger = logging.getLogger("scraper_pipeline")


class BaseScraper(ABC):
    """Abstract Base Class for web scrapers implementing dynamic pagination and error handling."""

    def __init__(self, http_client: HTTPClient, source_name: str):
        self.http_client = http_client
        self.source_name = source_name
        self.visited_urls: Set[str] = set()
        self.pages_scraped: int = 0
        self.records_collected: int = 0
        self.errors: List[str] = []

    @abstractmethod
    def parse_page(self, current_url: str, soup: BeautifulSoup) -> Tuple[List[DataRecord], Optional[str]]:
        """Parses page HTML soup and returns a list of DataRecord objects and the next page URL (if any)."""
        pass

    def run(self, start_url: str, max_pages: Optional[int] = None) -> List[DataRecord]:
        """Runs the main pagination loop starting from start_url."""
        logger.info(f"Starting scraper for [{self.source_name}] at {start_url}")
        all_records: List[DataRecord] = []
        current_url: Optional[str] = start_url

        while current_url and current_url not in self.visited_urls:
            if max_pages is not None and self.pages_scraped >= max_pages:
                logger.info(f"Reached maximum page limit ({max_pages}) for [{self.source_name}]")
                break

            self.visited_urls.add(current_url)
            self.pages_scraped += 1
            logger.info(f"Scraping [{self.source_name}] page {self.pages_scraped}: {current_url}")

            response = self.http_client.get(current_url)
            if not response:
                error_msg = f"Failed to fetch response for [{self.source_name}] at {current_url}"
                logger.error(error_msg)
                self.errors.append(error_msg)
                break

            try:
                soup = BeautifulSoup(response.text, "lxml")
            except Exception as e:
                # Fallback parser if lxml is missing or fails
                soup = BeautifulSoup(response.text, "html.parser")

            try:
                page_records, next_relative_url = self.parse_page(current_url, soup)
                all_records.extend(page_records)
                self.records_collected += len(page_records)
                logger.info(f"Found {len(page_records)} records on page {self.pages_scraped}")

                if next_relative_url:
                    current_url = make_absolute_url(current_url, next_relative_url)
                else:
                    current_url = None

            except Exception as e:
                error_msg = f"Unexpected parsing error on page {current_url}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.errors.append(error_msg)
                break

        logger.info(
            f"Finished scraping [{self.source_name}]. "
            f"Total pages: {self.pages_scraped}, Total records collected: {self.records_collected}"
        )
        return all_records
