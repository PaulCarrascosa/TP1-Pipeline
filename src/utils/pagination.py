from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginationParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_desc = sort_desc


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"arbitrary_types_allowed": True}


def paginate(query: Query, params: PaginationParams, model_class) -> Page:
    total = query.count()

    if params.sort_by and hasattr(model_class, params.sort_by):
        column = getattr(model_class, params.sort_by)
        query = query.order_by(column.desc() if params.sort_desc else column)

    items = query.offset(params.skip).limit(params.limit).all()

    pages = (total + params.limit - 1) // params.limit if params.limit > 0 else 1
    page = (params.skip // params.limit) + 1 if params.limit > 0 else 1

    return Page(items=items, total=total, page=page, size=params.limit, pages=pages)
