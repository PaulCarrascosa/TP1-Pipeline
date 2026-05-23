import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import SessionLocal
from src.db.init_db import init_db


def main():
    db = SessionLocal()
    try:
        init_db(db)
        print("Base de données initialisée avec succès")
    finally:
        db.close()


if __name__ == "__main__":
    main()
