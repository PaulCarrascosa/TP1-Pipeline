from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .users import User
from .books import Book


class LoanBase(BaseModel):
    user_id: int = Field(...)
    book_id: int = Field(...)
    loan_date: datetime = Field(default_factory=datetime.utcnow)
    return_date: Optional[datetime] = Field(None)
    due_date: datetime = Field(...)
    extended: bool = Field(False)


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    return_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    extended: Optional[bool] = None


class LoanInDBBase(LoanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Loan(LoanInDBBase):
    pass


class LoanWithDetails(Loan):
    user: User
    book: Book
