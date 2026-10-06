import logging
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup

from config import SOURCE_QUOTES, QUOTES_BASE_URL
from models.record import DataRecord
from scrapers.base_scraper import BaseScraper
from utils.http_client import HTTPClient

logger = logging.getLogger("scraper_pipeline")


class QuotesScraper(BaseScraper):
    """Scraper implementation for Quotes to Scrape (https://quotes.toscrape.com/)."""

    def __init__(self, http_client: HTTPClient):
        super().__init__(http_client, source_name=SOURCE_QUOTES)

    def parse_page(self, current_url: str, soup: BeautifulSoup) -> Tuple[List[DataRecord], Optional[str]]:
        records: List[DataRecord] = []
        quote_elements = soup.select("div.quote")

        for elem in quote_elements:
            try:
                # 1. Extract Quote Text
                text_tag = elem.select_one("span.text")
                if not text_tag:
                    logger.warning(f"Missing quote text tag on {current_url}")
                    continue
                quote_text = text_tag.get_text(strip=True)

                # 2. Extract Author
                author_tag = elem.select_one("small.author")
                author = author_tag.get_text(strip=True) if author_tag else None

                # 3. Extract Tags
                tag_elements = elem.select("div.tags > a.tag")
                tags_list = [t.get_text(strip=True) for t in tag_elements if t.get_text(strip=True)]
                tags_str = ", ".join(tags_list) if tags_list else None

                record = DataRecord(
                    source=self.source_name,
                    source_url=current_url,
                    name_or_title=quote_text,
                    category=None,
                    price=None,
                    rating=None,
                    author=author,
                    tags=tags_str,
                    description=None
                )
                records.append(record)

            except Exception as e:
                logger.error(f"Error parsing individual quote element on {current_url}: {e}")
                continue

        # Extract next page link
        next_tag = soup.select_one("li.next > a")
        next_page_url = next_tag.get("href") if next_tag else None

        return records, next_page_url
