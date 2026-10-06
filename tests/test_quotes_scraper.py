import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from scrapers.quotes_scraper import QuotesScraper
from config import SOURCE_QUOTES

MOCK_QUOTES_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="quote">
        <span class="text">“The world as we have created it is a process of our thinking.”</span>
        <span>by <small class="author">Albert Einstein</small></span>
        <div class="tags">
            <a class="tag" href="/tag/change/page/1/">change</a>
            <a class="tag" href="/tag/deep-thoughts/page/1/">deep-thoughts</a>
        </div>
    </div>
    <ul class="pager">
        <li class="next"><a href="/page/2/">Next</a></li>
    </ul>
</body>
</html>
"""


def test_quotes_scraper_parse_page():
    mock_http_client = MagicMock()
    scraper = QuotesScraper(http_client=mock_http_client)

    soup = BeautifulSoup(MOCK_QUOTES_HTML, "html.parser")
    current_url = "https://quotes.toscrape.com/"

    records, next_url = scraper.parse_page(current_url, soup)

    assert len(records) == 1
    record = records[0]
    assert record.source == SOURCE_QUOTES
    assert record.name_or_title == "“The world as we have created it is a process of our thinking.”"
    assert record.author == "Albert Einstein"
    assert record.tags == "change, deep-thoughts"
    assert record.source_url == current_url
    assert next_url == "/page/2/"
