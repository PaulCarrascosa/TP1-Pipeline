from typing import List, Optional, Any, Dict, Union
from datetime import datetime, timedelta

from ..repositories.loans import LoanRepository
from ..repositories.books import BookRepository
from ..repositories.users import UserRepository
from ..models.loans import Loan
from ..models.books import Book
from ..models.users import User
from ..api.schemas.loans import LoanCreate, LoanUpdate
from .base import BaseService


class LoanService(BaseService[Loan, LoanCreate, LoanUpdate]):
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        user_repository: UserRepository
    ):
        super().__init__(loan_repository)
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.user_repository = user_repository

    def get_active_loans(self) -> List[Loan]:
        return self.loan_repository.get_active_loans()

    def get_overdue_loans(self) -> List[Loan]:
        return self.loan_repository.get_overdue_loans()

    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        return self.loan_repository.get_loans_by_user(user_id=user_id)

    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        return self.loan_repository.get_loans_by_book(book_id=book_id)

    def create_loan(
        self,
        *,
        user_id: int,
        book_id: int,
        loan_period_days: int = 14
    ) -> Loan:
        user = self.user_repository.get(id=user_id)
        if not user:
            raise ValueError(f"Utilisateur avec l'ID {user_id} non trouvé")

        if not user.is_active:
            raise ValueError("L'utilisateur est inactif et ne peut pas emprunter de livres")

        book = self.book_repository.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")

        if book.quantity <= 0:
            raise ValueError("Le livre n'est pas disponible pour l'emprunt")

        active_loans = self.loan_repository.get_active_loans()
        for loan in active_loans:
            if loan.user_id == user_id and loan.book_id == book_id:
                raise ValueError("L'utilisateur a déjà emprunté ce livre et ne l'a pas encore rendu")

        user_active_loans = [loan for loan in active_loans if loan.user_id == user_id]
        if len(user_active_loans) >= 5:
            raise ValueError("L'utilisateur a atteint la limite d'emprunts simultanés (5)")

        loan_data = {
            "user_id": user_id,
            "book_id": book_id,
            "loan_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=loan_period_days),
            "return_date": None
        }

        loan = self.loan_repository.create(obj_in=loan_data)

        book.quantity -= 1
        self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})

        return loan

    def return_loan(self, *, loan_id: int) -> Loan:
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            raise ValueError(f"Emprunt avec l'ID {loan_id} non trouvé")

        if loan.return_date:
            raise ValueError("L'emprunt a déjà été retourné")

        loan = self.loan_repository.update(db_obj=loan, obj_in={"return_date": datetime.utcnow()})

        book = self.book_repository.get(id=loan.book_id)
        if book:
            book.quantity += 1
            self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})

        return loan

    def extend_loan(self, *, loan_id: int, extension_days: int = 7) -> Loan:
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            raise ValueError(f"Emprunt avec l'ID {loan_id} non trouvé")

        if loan.return_date:
            raise ValueError("L'emprunt a déjà été retourné")

        if loan.due_date < datetime.utcnow():
            raise ValueError("L'emprunt est en retard et ne peut pas être prolongé")

        if loan.due_date > loan.loan_date + timedelta(days=14):
            raise ValueError("L'emprunt a déjà été prolongé")

        new_due_date = loan.due_date + timedelta(days=extension_days)
        return self.loan_repository.update(db_obj=loan, obj_in={"due_date": new_due_date})
