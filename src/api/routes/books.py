from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Any, Optional

from ...db.session import get_db
from ...models.books import Book as BookModel
from ...models.categories import book_category
from ..schemas.books import Book, BookCreate, BookUpdate, Category, CategoryCreate
from ...repositories.books import BookRepository
from ...repositories.categories import CategoryRepository
from ...models.categories import Category as CategoryModel
from ...services.books import BookService
from ...utils.pagination import PaginationParams, paginate, Page
from ..dependencies import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=Page[Book])
def read_books(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_desc: bool = Query(False),
    current_user=Depends(get_current_active_user)
) -> Any:
    params = PaginationParams(skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc)
    return paginate(db.query(BookModel), params, BookModel)


@router.get("/search/", response_model=Page[Book])
def search_books(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, min_length=1),
    category_id: Optional[int] = Query(None),
    author: Optional[str] = Query(None),
    publication_year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_desc: bool = Query(False),
    current_user=Depends(get_current_active_user)
) -> Any:
    search_query = db.query(BookModel)

    if query:
        search_query = search_query.filter(
            or_(
                BookModel.title.ilike(f"%{query}%"),
                BookModel.author.ilike(f"%{query}%"),
                BookModel.isbn.ilike(f"%{query}%"),
                BookModel.description.ilike(f"%{query}%")
            )
        )
    if category_id:
        search_query = search_query.join(book_category).filter(
            book_category.c.category_id == category_id
        )
    if author:
        search_query = search_query.filter(BookModel.author.ilike(f"%{author}%"))
    if publication_year:
        search_query = search_query.filter(BookModel.publication_year == publication_year)

    params = PaginationParams(skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc)
    return paginate(search_query, params, BookModel)


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(get_db),
    book_in: BookCreate,
    current_user=Depends(get_current_admin_user)
) -> Any:
    service = BookService(BookRepository(BookModel, db))
    try:
        category_ids = book_in.category_ids
        book_data = book_in.model_dump(exclude={"category_ids"})
        book = service.create(obj_in=book_data)
        if category_ids:
            repo = BookRepository(BookModel, db)
            for cid in category_ids:
                repo.add_category(book_id=book.id, category_id=cid)
            db.refresh(book)
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/search/title/{title}", response_model=List[Book])
def search_books_by_title(
    *,
    db: Session = Depends(get_db),
    title: str,
    current_user=Depends(get_current_active_user)
) -> Any:
    return BookService(BookRepository(BookModel, db)).get_by_title(title=title)


@router.get("/search/author/{author}", response_model=List[Book])
def search_books_by_author(
    *,
    db: Session = Depends(get_db),
    author: str,
    current_user=Depends(get_current_active_user)
) -> Any:
    return BookService(BookRepository(BookModel, db)).get_by_author(author=author)


@router.get("/search/isbn/{isbn}", response_model=Book)
def search_book_by_isbn(
    *,
    db: Session = Depends(get_db),
    isbn: str,
    current_user=Depends(get_current_active_user)
) -> Any:
    book = BookService(BookRepository(BookModel, db)).get_by_isbn(isbn=isbn)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé")
    return book


@router.get("/{id}", response_model=Book)
def read_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user=Depends(get_current_active_user)
) -> Any:
    book = BookRepository(BookModel, db).get_with_categories(id=id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé")
    return book


@router.put("/{id}", response_model=Book)
def update_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    book_in: BookUpdate,
    current_user=Depends(get_current_admin_user)
) -> Any:
    service = BookService(BookRepository(BookModel, db))
    book = service.get(id=id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé")
    try:
        category_ids = book_in.category_ids
        update_data = book_in.model_dump(exclude_unset=True, exclude={"category_ids"})
        book = service.update(db_obj=book, obj_in=update_data)
        if category_ids is not None:
            repo = BookRepository(BookModel, db)
            book.categories.clear()
            db.commit()
            for cid in category_ids:
                repo.add_category(book_id=book.id, category_id=cid)
            db.refresh(book)
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", response_model=Book)
def delete_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user=Depends(get_current_admin_user)
) -> Any:
    service = BookService(BookRepository(BookModel, db))
    book = service.get(id=id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre non trouvé")
    return service.remove(id=id)


@router.post("/{id}/categories/{category_id}", response_model=Book)
def add_book_category(
    *,
    db: Session = Depends(get_db),
    id: int,
    category_id: int,
    current_user=Depends(get_current_admin_user)
) -> Any:
    repo = BookRepository(BookModel, db)
    try:
        repo.add_category(book_id=id, category_id=category_id)
        return repo.get_with_categories(id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}/categories/{category_id}", response_model=Book)
def remove_book_category(
    *,
    db: Session = Depends(get_db),
    id: int,
    category_id: int,
    current_user=Depends(get_current_admin_user)
) -> Any:
    repo = BookRepository(BookModel, db)
    try:
        repo.remove_category(book_id=id, category_id=category_id)
        return repo.get_with_categories(id=id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
