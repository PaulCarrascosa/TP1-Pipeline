from typing import Optional

from .base import BaseRepository
from ..models.categories import Category


class CategoryRepository(BaseRepository):
    def get_by_name(self, *, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_or_create(self, *, name: str, description: Optional[str] = None) -> Category:
        category = self.get_by_name(name=name)
        if not category:
            category_data = {"name": name}
            if description:
                category_data["description"] = description
            category = self.create(obj_in=category_data)
        return category
