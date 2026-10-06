import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from scrapers.books_scraper import BooksScraper
from config import SOURCE_BOOKS

MOCK_BOOKS_HTML = """
<!DOCTYPE html>
<html>
<body>
    <ol class="row">
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
            <article class="product_pod">
                <h3><a href="a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
                <div class="product_price">
                    <p class="price_color">£51.77</p>
                    <p class="instock availability"><i class="icon-ok"></i> In stock</p>
                </div>
                <p class="star-rating Three"></p>
            </article>
        </li>
    </ol>
    <ul class="pager">
        <li class="next"><a href="page-2.html">next</a></li>
    </ul>
</body>
</html>
"""


def test_books_scraper_parse_page():
    mock_http_client = MagicMock()
    scraper = BooksScraper(http_client=mock_http_client, fetch_details=False)

    soup = BeautifulSoup(MOCK_BOOKS_HTML, "html.parser")
    current_url = "https://books.toscrape.com/catalogue/page-1.html"

    records, next_url = scraper.parse_page(current_url, soup)

    assert len(records) == 1
    record = records[0]
    assert record.source == SOURCE_BOOKS
    assert record.name_or_title == "A Light in the Attic"
    assert record.price == "£51.77"
    assert record.rating == "Three"
    assert record.source_url == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    assert next_url == "page-2.html"
