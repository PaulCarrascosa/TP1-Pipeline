import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.repositories.books import BookRepository
from src.services.books import BookService
from src.api.schemas.books import BookCreate, BookUpdate


def _make_service(db_session: Session) -> BookService:
    return BookService(BookRepository(Book, db_session))


def test_create_book(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="Le Petit Prince",
        author="Antoine de Saint-Exupéry",
        isbn="9782070612758",
        publication_year=1943,
        quantity=5
    )

    book = service.create(obj_in=book_in)

    assert book.title == "Le Petit Prince"
    assert book.author == "Antoine de Saint-Exupéry"
    assert book.isbn == "9782070612758"
    assert book.quantity == 5


def test_create_book_duplicate_isbn(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="Book One",
        author="Author",
        isbn="9780000000001",
        publication_year=2000,
        quantity=1
    )
    service.create(obj_in=book_in)

    with pytest.raises(ValueError, match="ISBN"):
        service.create(obj_in=book_in)


def test_get_by_isbn(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="ISBN Test Book",
        author="Author",
        isbn="9780000000002",
        publication_year=2000,
        quantity=1
    )
    book = service.create(obj_in=book_in)

    found = service.get_by_isbn(isbn="9780000000002")
    assert found is not None
    assert found.id == book.id

    not_found = service.get_by_isbn(isbn="0000000000000")
    assert not_found is None


def test_get_by_title(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="Python for Beginners",
        author="Author",
        isbn="9780000000003",
        publication_year=2020,
        quantity=2
    )
    service.create(obj_in=book_in)

    results = service.get_by_title(title="Python")
    assert len(results) >= 1
    assert any(b.title == "Python for Beginners" for b in results)


def test_get_by_author(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="Another Book",
        author="Jane Doe",
        isbn="9780000000004",
        publication_year=2021,
        quantity=3
    )
    service.create(obj_in=book_in)

    results = service.get_by_author(author="Jane")
    assert len(results) >= 1
    assert any(b.author == "Jane Doe" for b in results)


def test_update_quantity(db_session: Session):
    service = _make_service(db_session)

    book_in = BookCreate(
        title="Quantity Book",
        author="Author",
        isbn="9780000000005",
        publication_year=2000,
        quantity=3
    )
    book = service.create(obj_in=book_in)

    updated = service.update_quantity(book_id=book.id, quantity_change=-1)
    assert updated.quantity == 2

    updated = service.update_quantity(book_id=book.id, quantity_change=2)
    assert updated.quantity == 4

    with pytest.raises(ValueError, match="négative"):
        service.update_quantity(book_id=book.id, quantity_change=-10)
