from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from ...db.session import get_db
from ...models.loans import Loan as LoanModel
from ...models.books import Book as BookModel
from ...models.users import User as UserModel
from ..schemas.loans import Loan, LoanCreate, LoanUpdate
from ...repositories.loans import LoanRepository
from ...repositories.books import BookRepository
from ...repositories.users import UserRepository
from ...services.loans import LoanService
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


def _make_service(db: Session) -> LoanService:
    return LoanService(
        LoanRepository(LoanModel, db),
        BookRepository(BookModel, db),
        UserRepository(UserModel, db)
    )


@router.get("/", response_model=List[Loan])
def read_loans(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_admin_user)
) -> Any:
    return _make_service(db).get_multi(skip=skip, limit=limit)


@router.get("/active/", response_model=List[Loan])
def read_active_loans(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
) -> Any:
    return _make_service(db).get_active_loans()


@router.get("/overdue/", response_model=List[Loan])
def read_overdue_loans(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user)
) -> Any:
    return _make_service(db).get_overdue_loans()


@router.get("/user/{user_id}", response_model=List[Loan])
def read_user_loans(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user=Depends(get_current_active_user)
) -> Any:
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return _make_service(db).get_loans_by_user(user_id=user_id)


@router.get("/book/{book_id}", response_model=List[Loan])
def read_book_loans(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    current_user=Depends(get_current_admin_user)
) -> Any:
    return _make_service(db).get_loans_by_book(book_id=book_id)


@router.post("/", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    book_id: int,
    loan_period_days: int = 14,
    current_user=Depends(get_current_admin_user)
) -> Any:
    try:
        return _make_service(db).create_loan(
            user_id=user_id,
            book_id=book_id,
            loan_period_days=loan_period_days
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{id}", response_model=Loan)
def read_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user=Depends(get_current_active_user)
) -> Any:
    loan = _make_service(db).get(id=id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emprunt non trouvé")
    if not current_user.is_admin and current_user.id != loan.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return loan


@router.post("/{id}/return", response_model=Loan)
def return_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user=Depends(get_current_admin_user)
) -> Any:
    try:
        return _make_service(db).return_loan(loan_id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/extend", response_model=Loan)
def extend_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    extension_days: int = 7,
    current_user=Depends(get_current_admin_user)
) -> Any:
    try:
        return _make_service(db).extend_loan(loan_id=id, extension_days=extension_days)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
