import pytest
from models.record import DataRecord
from processing.cleaning import (
    clean_text,
    clean_price,
    clean_rating,
    clean_url,
    clean_tags,
    normalize_missing_value,
    clean_record
)


def test_clean_text():
    assert clean_text("  Example   Book  Title  ") == "Example Book Title"
    assert clean_text("“The world is beautiful.”", strip_quotes=True) == "The world is beautiful."
    assert clean_text("   ") is None
    assert clean_text("N/A") is None
    assert clean_text("null") is None


def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("$19.99") == 19.99
    assert clean_price("15.50") == 15.50
    assert clean_price(42) == 42.0
    assert clean_price("free") is None
    assert clean_price("N/A") is None
    assert clean_price("-5.00") is None


def test_clean_rating():
    assert clean_rating("One") == 1
    assert clean_rating("Two") == 2
    assert clean_rating("Three") == 3
    assert clean_rating("Four") == 4
    assert clean_rating("Five") == 5
    assert clean_rating("3") == 3
    assert clean_rating(5) == 5
    assert clean_rating("Ten") is None
    assert clean_rating(0) is None
    assert clean_rating(6) is None


def test_clean_url():
    assert clean_url("https://books.toscrape.com/catalogue/page-1.html") == "https://books.toscrape.com/catalogue/page-1.html"
    assert clean_url("invalid-url") is None
    assert clean_url("  ") is None


def test_clean_tags():
    assert clean_tags("  change , deep-thoughts ,thinking ") == "change, deep-thoughts, thinking"
    assert clean_tags("N/A") is None


def test_clean_record():
    raw_record = DataRecord(
        source="  Books to Scrape  ",
        source_url="  https://books.toscrape.com/book.html  ",
        name_or_title="  A  Light in the  Attic  ",
        category="  Poetry  ",
        price="£51.77",
        rating="Three",
        description="  A nice book.  "
    )
    cleaned = clean_record(raw_record)
    assert cleaned.source == "Books to Scrape"
    assert cleaned.source_url == "https://books.toscrape.com/book.html"
    assert cleaned.name_or_title == "A Light in the Attic"
    assert cleaned.category == "Poetry"
    assert cleaned.price == 51.77
    assert cleaned.rating == 3
    assert cleaned.description == "A nice book."
