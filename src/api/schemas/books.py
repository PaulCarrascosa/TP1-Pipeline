from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Category(CategoryInDBBase):
    pass


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., ge=1000, le=datetime.now().year)
    description: Optional[str] = Field(None, max_length=1000)
    quantity: int = Field(..., ge=0)
    publisher: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=50)
    pages: Optional[int] = Field(None, gt=0)


class BookCreate(BookBase):
    category_ids: Optional[List[int]] = Field(None)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    description: Optional[str] = Field(None, max_length=1000)
    quantity: Optional[int] = Field(None, ge=0)
    publisher: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=50)
    pages: Optional[int] = Field(None, gt=0)
    category_ids: Optional[List[int]] = Field(None)


class BookInDBBase(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Book(BookInDBBase):
    categories: List[Category] = []
