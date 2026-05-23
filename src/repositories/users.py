from typing import Optional

from ..models.users import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    def get_by_email(self, *, email: str) -> Optional[User]:
        return self.db.query(self.model).filter(self.model.email == email).first()
