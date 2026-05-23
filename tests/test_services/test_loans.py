import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.models.users import User
from src.models.loans import Loan
from src.repositories.books import BookRepository
from src.repositories.users import UserRepository
from src.repositories.loans import LoanRepository
from src.services.loans import LoanService
from src.services.users import UserService
from src.services.books import BookService
from src.api.schemas.users import UserCreate
from src.api.schemas.books import BookCreate


def _make_loan_service(db_session: Session) -> LoanService:
    return LoanService(
        LoanRepository(Loan, db_session),
        BookRepository(Book, db_session),
        UserRepository(User, db_session)
    )


def _create_user(db_session: Session, email: str = "user@example.com") -> User:
    service = UserService(UserRepository(User, db_session))
    return service.create(obj_in=UserCreate(
        email=email,
        password="password123",
        full_name="Test User",
        is_active=True,
        is_admin=False
    ))


def _create_book(db_session: Session, isbn: str = "9780000000010", quantity: int = 3) -> Book:
    service = BookService(BookRepository(Book, db_session))
    return service.create(obj_in=BookCreate(
        title="Test Book",
        author="Test Author",
        isbn=isbn,
        publication_year=2020,
        quantity=quantity
    ))


def test_create_loan(db_session: Session):
    user = _create_user(db_session, "loan_create@example.com")
    book = _create_book(db_session, "9780000000011")
    service = _make_loan_service(db_session)

    initial_quantity = book.quantity
    loan = service.create_loan(user_id=user.id, book_id=book.id)

    assert loan.user_id == user.id
    assert loan.book_id == book.id
    assert loan.return_date is None

    updated_book = BookRepository(Book, db_session).get(id=book.id)
    assert updated_book.quantity == initial_quantity - 1


def test_create_loan_book_unavailable(db_session: Session):
    user = _create_user(db_session, "loan_unavail@example.com")
    book = _create_book(db_session, "9780000000012", quantity=0)
    service = _make_loan_service(db_session)

    with pytest.raises(ValueError, match="disponible"):
        service.create_loan(user_id=user.id, book_id=book.id)


def test_create_loan_inactive_user(db_session: Session):
    user_service = UserService(UserRepository(User, db_session))
    user = user_service.create(obj_in=UserCreate(
        email="inactive@example.com",
        password="password123",
        full_name="Inactive User",
        is_active=False,
        is_admin=False
    ))
    book = _create_book(db_session, "9780000000013")
    service = _make_loan_service(db_session)

    with pytest.raises(ValueError, match="inactif"):
        service.create_loan(user_id=user.id, book_id=book.id)


def test_return_loan(db_session: Session):
    user = _create_user(db_session, "return@example.com")
    book = _create_book(db_session, "9780000000014")
    service = _make_loan_service(db_session)

    initial_quantity = book.quantity
    loan = service.create_loan(user_id=user.id, book_id=book.id)

    returned = service.return_loan(loan_id=loan.id)
    assert returned.return_date is not None

    updated_book = BookRepository(Book, db_session).get(id=book.id)
    assert updated_book.quantity == initial_quantity

    with pytest.raises(ValueError, match="déjà été retourné"):
        service.return_loan(loan_id=loan.id)


def test_duplicate_loan(db_session: Session):
    user = _create_user(db_session, "dup_loan@example.com")
    book = _create_book(db_session, "9780000000015", quantity=5)
    service = _make_loan_service(db_session)

    service.create_loan(user_id=user.id, book_id=book.id)

    with pytest.raises(ValueError, match="déjà emprunté"):
        service.create_loan(user_id=user.id, book_id=book.id)
