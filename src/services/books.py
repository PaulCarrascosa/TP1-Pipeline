from typing import List, Optional, Any, Dict, Union

from ..repositories.books import BookRepository
from ..models.books import Book
from ..api.schemas.books import BookCreate, BookUpdate
from .base import BaseService


class BookService(BaseService[Book, BookCreate, BookUpdate]):
    def __init__(self, repository: BookRepository):
        super().__init__(repository)
        self.repository = repository

    def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
        return self.repository.get_by_isbn(isbn=isbn)

    def get_by_title(self, *, title: str) -> List[Book]:
        return self.repository.get_by_title(title=title)

    def get_by_author(self, *, author: str) -> List[Book]:
        return self.repository.get_by_author(author=author)

    def create(self, *, obj_in: Union[BookCreate, Dict[str, Any]]) -> Book:
        isbn = obj_in.get("isbn") if isinstance(obj_in, dict) else obj_in.isbn
        existing_book = self.get_by_isbn(isbn=isbn)
        if existing_book:
            raise ValueError("L'ISBN est déjà utilisé")

        if isinstance(obj_in, dict):
            book_data = {k: v for k, v in obj_in.items() if k != "category_ids"}
        else:
            book_data = obj_in.model_dump(exclude={"category_ids"})

        return self.repository.create(obj_in=book_data)

    def update_quantity(self, *, book_id: int, quantity_change: int) -> Book:
        book = self.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")

        new_quantity = book.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("La quantité ne peut pas être négative")

        return self.repository.update(db_obj=book, obj_in={"quantity": new_quantity})
