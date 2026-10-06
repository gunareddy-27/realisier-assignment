import pytest
from models.record import DataRecord
from processing.deduplication import Deduplicator
from config import SOURCE_BOOKS, SOURCE_QUOTES


def test_deduplication_books():
    deduper = Deduplicator()
    rec1 = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/catalogue/book_1.html",
        name_or_title="Example Book Title"
    )
    rec2 = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/catalogue/book_1.html",
        name_or_title=" EXAMPLE BOOK TITLE "
    )
    rec3 = DataRecord(
        source=SOURCE_BOOKS,
        source_url="https://books.toscrape.com/catalogue/book_2.html",
        name_or_title="Different Book Title"
    )

    retained, duplicates, counts = deduper.process([rec1, rec2, rec3])
    assert len(retained) == 2
    assert len(duplicates) == 1
    assert counts[SOURCE_BOOKS] == 1
    assert retained[0].name_or_title == "Example Book Title"


def test_deduplication_quotes():
    deduper = Deduplicator()
    rec1 = DataRecord(
        source=SOURCE_QUOTES,
        source_url="https://quotes.toscrape.com/",
        name_or_title="The world as we have created it...",
        author="Albert Einstein"
    )
    rec2 = DataRecord(
        source=SOURCE_QUOTES,
        source_url="https://quotes.toscrape.com/page/2/",
        name_or_title=" THE WORLD AS WE HAVE CREATED IT... ",
        author="albert einstein"
    )

    retained, duplicates, counts = deduper.process([rec1, rec2])
    assert len(retained) == 1
    assert len(duplicates) == 1
    assert counts[SOURCE_QUOTES] == 1
