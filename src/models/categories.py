from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from .base import Base

book_category = Table(
    "book_category",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("book.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True),
)


class Category(Base):
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)

    books = relationship("Book", secondary=book_category, back_populates="categories")
