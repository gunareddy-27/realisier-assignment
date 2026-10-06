import pytest
from models.record import DataRecord
from processing.validation import validate_record
from config import SOURCE_BOOKS, SOURCE_QUOTES


def test_validate_record_success():
    record = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/catalogue/book_1.html",
        name_or_title="A Light in the Attic",
        price=51.77,
        rating=3
    )
    res = validate_record(record)
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_validate_record_missing_mandatory():
    record = DataRecord(
        source="",
        source_url="",
        name_or_title=""
    )
    res = validate_record(record)
    assert res.is_valid is False
    assert any("source" in err for err in res.errors)
    assert any("source_url" in err for err in res.errors)
    assert any("name_or_title" in err for err in res.errors)


def test_validate_record_invalid_source():
    record = DataRecord(
        source="Unknown Source",
        source_url="https://example.com",
        name_or_title="Title"
    )
    res = validate_record(record)
    assert res.is_valid is False
    assert any("Unrecognized source" in err for err in res.errors)


def test_validate_record_invalid_rating():
    record = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/book.html",
        name_or_title="Title",
        rating=10
    )
    res = validate_record(record)
    assert res.is_valid is False
    assert any("Rating must be between 1 and 5" in err for err in res.errors)


def test_validate_record_invalid_price():
    record = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/book.html",
        name_or_title="Title",
        price=-10.0
    )
    res = validate_record(record)
    assert res.is_valid is False
    assert any("cannot be negative" in err for err in res.errors)
