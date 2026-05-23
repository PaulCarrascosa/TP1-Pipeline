import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.models.categories import Category
from src.repositories.books import BookRepository
from src.repositories.categories import CategoryRepository


def test_create_book(db_session: Session):
    repo = BookRepository(Book, db_session)

    book = repo.create(obj_in={
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "1234567890123",
        "publication_year": 2020,
        "quantity": 5
    })

    assert book.id is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "1234567890123"
    assert book.quantity == 5


def test_get_book_by_isbn(db_session: Session):
    repo = BookRepository(Book, db_session)
    repo.create(obj_in={
        "title": "ISBN Test Book",
        "author": "Author",
        "isbn": "9876543210123",
        "publication_year": 2021,
        "quantity": 3
    })

    book = repo.get_by_isbn(isbn="9876543210123")
    assert book is not None
    assert book.title == "ISBN Test Book"


def test_search_books(db_session: Session):
    repo = BookRepository(Book, db_session)
    for data in [
        {"title": "Python Programming", "author": "John Doe", "isbn": "1111111111111", "publication_year": 2019, "quantity": 2},
        {"title": "Advanced Python", "author": "Jane Smith", "isbn": "2222222222222", "publication_year": 2020, "quantity": 1},
        {"title": "Java Programming", "author": "Bob Johnson", "isbn": "3333333333333", "publication_year": 2018, "quantity": 3},
    ]:
        repo.create(obj_in=data)

    python_books = repo.search(query="Python")
    assert len(python_books) == 2

    smith_books = repo.search(query="Smith")
    assert len(smith_books) == 1
    assert smith_books[0].author == "Jane Smith"

    isbn_books = repo.search(query="2222222222222")
    assert len(isbn_books) == 1


def test_book_categories(db_session: Session):
    book_repo = BookRepository(Book, db_session)
    cat_repo = CategoryRepository(Category, db_session)

    programming = cat_repo.create(obj_in={"name": "Programming", "description": "Programming books"})
    python_cat = cat_repo.create(obj_in={"name": "Python", "description": "Python books"})

    book = book_repo.create(obj_in={
        "title": "Python Cookbook",
        "author": "David Beazley",
        "isbn": "4444444444444",
        "publication_year": 2013,
        "quantity": 2
    })

    book_repo.add_category(book_id=book.id, category_id=programming.id)
    book_repo.add_category(book_id=book.id, category_id=python_cat.id)

    book_with_cats = book_repo.get_with_categories(id=book.id)
    assert len(book_with_cats.categories) == 2
    names = [c.name for c in book_with_cats.categories]
    assert "Programming" in names
    assert "Python" in names

    book_repo.remove_category(book_id=book.id, category_id=programming.id)
    book_with_cats = book_repo.get_with_categories(id=book.id)
    assert len(book_with_cats.categories) == 1
    assert book_with_cats.categories[0].name == "Python"


def test_category_get_or_create(db_session: Session):
    repo = CategoryRepository(Category, db_session)

    cat1 = repo.get_or_create(name="Fiction", description="Fiction books")
    cat2 = repo.get_or_create(name="Fiction")

    assert cat1.id == cat2.id
    assert cat1.name == "Fiction"


def test_book_stats(db_session: Session):
    repo = BookRepository(Book, db_session)
    repo.create(obj_in={"title": "A", "author": "Author", "isbn": "5555555555555", "publication_year": 2000, "quantity": 3})
    repo.create(obj_in={"title": "B", "author": "Author", "isbn": "6666666666666", "publication_year": 2010, "quantity": 2})

    stats = repo.get_stats()
    assert stats["unique_books"] >= 2
    assert stats["total_books"] >= 5
