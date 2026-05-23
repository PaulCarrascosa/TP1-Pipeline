"""Database session configuration"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings
from ..utils import sql_logging  # noqa: F401 — registers SQLAlchemy event listeners

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=settings.SQL_ECHO,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session as dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
