import logging
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup

from config import SOURCE_BOOKS, BOOKS_BASE_URL
from models.record import DataRecord
from scrapers.base_scraper import BaseScraper
from utils.helpers import make_absolute_url
from utils.http_client import HTTPClient

logger = logging.getLogger("scraper_pipeline")


class BooksScraper(BaseScraper):
    """Scraper implementation for Books to Scrape (https://books.toscrape.com/)."""

    def __init__(self, http_client: HTTPClient, fetch_details: bool = True):
        super().__init__(http_client, source_name=SOURCE_BOOKS)
        self.fetch_details = fetch_details

    def parse_page(self, current_url: str, soup: BeautifulSoup) -> Tuple[List[DataRecord], Optional[str]]:
        records: List[DataRecord] = []
        book_pods = soup.select("article.product_pod")

        for pod in book_pods:
            try:
                # 1. Extract Title & Detail URL
                a_tag = pod.select_one("h3 > a")
                if not a_tag:
                    logger.warning(f"Missing title <a> tag in book pod on {current_url}")
                    continue

                title = a_tag.get("title") or a_tag.get_text(strip=True)
                relative_url = a_tag.get("href", "")
                product_url = make_absolute_url(current_url, relative_url)

                # 2. Extract Price String
                price_tag = pod.select_one("p.price_color")
                price_str = price_tag.get_text(strip=True) if price_tag else None

                # 3. Extract Rating String
                rating_str = None
                rating_tag = pod.select_one("p.star-rating")
                if rating_tag:
                    classes = rating_tag.get("class", [])
                    rating_classes = [c for c in classes if c != "star-rating"]
                    if rating_classes:
                        rating_str = rating_classes[0]

                # 4. Optional Detail Page Fetching (Category & Description)
                category = None
                description = None
                if self.fetch_details and product_url:
                    category, description = self._fetch_book_details(product_url)

                record = DataRecord(
                    source=self.source_name,
                    source_url=product_url,
                    name_or_title=title,
                    category=category,
                    price=price_str,  # Will be converted to float in cleaning step
                    rating=rating_str,  # Will be converted to integer rating in cleaning step
                    author=None,
                    tags=None,
                    description=description
                )
                records.append(record)

            except Exception as e:
                logger.error(f"Error parsing individual book pod on {current_url}: {e}")
                continue

        # Extract next page link
        next_tag = soup.select_one("li.next > a")
        next_page_url = next_tag.get("href") if next_tag else None

        return records, next_page_url

    def _fetch_book_details(self, product_url: str) -> Tuple[Optional[str], Optional[str]]:
        """Safely fetches and extracts category and description from the detail page."""
        response = self.http_client.get(product_url)
        if not response:
            return None, None

        try:
            detail_soup = BeautifulSoup(response.text, "lxml")
        except Exception:
            detail_soup = BeautifulSoup(response.text, "html.parser")

        category = None
        description = None

        # Category from breadcrumbs (e.g. Home > Books > Sequential Art > Title)
        breadcrumb_links = detail_soup.select("ul.breadcrumb > li > a")
        if len(breadcrumb_links) >= 3:
            category = breadcrumb_links[2].get_text(strip=True)

        # Description from #product_description div sibling <p>
        desc_header = detail_soup.select_one("#product_description")
        if desc_header:
            desc_p = desc_header.find_next_sibling("p")
            if desc_p:
                description = desc_p.get_text(strip=True)

        return category, description
