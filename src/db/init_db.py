import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..models.users import User
from ..models.books import Book
from ..models.loans import Loan
from ..models.categories import Category
from ..utils.security import get_password_hash

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Administrateur créé")

    categories_data = [
        {"name": "Roman", "description": "Romans littéraires"},
        {"name": "Science-Fiction", "description": "Livres de science-fiction"},
        {"name": "Policier", "description": "Romans policiers et thrillers"},
        {"name": "Biographie", "description": "Biographies et autobiographies"},
        {"name": "Histoire", "description": "Livres d'histoire"},
    ]

    for cat_data in categories_data:
        if not db.query(Category).filter(Category.name == cat_data["name"]).first():
            db.add(Category(**cat_data))

    db.commit()
    logger.info("Catégories créées")

    roman = db.query(Category).filter(Category.name == "Roman").first()
    sf = db.query(Category).filter(Category.name == "Science-Fiction").first()
    policier = db.query(Category).filter(Category.name == "Policier").first()
    biographie = db.query(Category).filter(Category.name == "Biographie").first()
    histoire = db.query(Category).filter(Category.name == "Histoire").first()

    books_data = [
        {
            "title": "1984",
            "author": "George Orwell",
            "isbn": "9780451524935",
            "publication_year": 1949,
            "description": "Un roman dystopique sur un régime totalitaire",
            "quantity": 5,
            "publisher": "Secker & Warburg",
            "language": "Anglais",
            "pages": 328,
            "categories": [roman, sf]
        },
        {
            "title": "Le Seigneur des Anneaux",
            "author": "J.R.R. Tolkien",
            "isbn": "9780618640157",
            "publication_year": 1954,
            "description": "Une épopée de fantasy",
            "quantity": 3,
            "publisher": "Allen & Unwin",
            "language": "Anglais",
            "pages": 1178,
            "categories": [roman, sf]
        },
        {
            "title": "Le Nom de la Rose",
            "author": "Umberto Eco",
            "isbn": "9782253033134",
            "publication_year": 1980,
            "description": "Un roman policier médiéval",
            "quantity": 2,
            "publisher": "Grasset",
            "language": "Italien",
            "pages": 512,
            "categories": [roman, policier, histoire]
        },
        {
            "title": "Steve Jobs",
            "author": "Walter Isaacson",
            "isbn": "9781451648539",
            "publication_year": 2011,
            "description": "La biographie de Steve Jobs",
            "quantity": 4,
            "publisher": "Simon & Schuster",
            "language": "Anglais",
            "pages": 656,
            "categories": [biographie]
        },
    ]

    for book_data in books_data:
        book_cats = book_data.pop("categories")
        if not db.query(Book).filter(Book.isbn == book_data["isbn"]).first():
            book = Book(**book_data)
            db.add(book)
            db.flush()
            for cat in book_cats:
                book.categories.append(cat)

    db.commit()
    logger.info("Livres créés")

    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = User(
            email="user@example.com",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            is_active=True,
            is_admin=False,
            phone="123-456-7890",
            address="123 Main St, Anytown, USA"
        )
        db.add(user)
        db.commit()
        logger.info("Utilisateur créé")

    book1 = db.query(Book).filter(Book.isbn == "9780451524935").first()
    book2 = db.query(Book).filter(Book.isbn == "9780618640157").first()

    if book1 and book2 and user:
        if not db.query(Loan).filter(
            Loan.user_id == user.id, Loan.book_id == book1.id, Loan.return_date.is_(None)
        ).first():
            db.add(Loan(
                user_id=user.id,
                book_id=book1.id,
                loan_date=datetime.utcnow() - timedelta(days=7),
                due_date=datetime.utcnow() + timedelta(days=7),
                extended=False
            ))
            book1.quantity -= 1

        if not db.query(Loan).filter(
            Loan.user_id == user.id, Loan.book_id == book2.id, Loan.return_date.isnot(None)
        ).first():
            db.add(Loan(
                user_id=user.id,
                book_id=book2.id,
                loan_date=datetime.utcnow() - timedelta(days=30),
                due_date=datetime.utcnow() - timedelta(days=16),
                return_date=datetime.utcnow() - timedelta(days=20),
                extended=True
            ))

        db.commit()
        logger.info("Emprunts créés")
