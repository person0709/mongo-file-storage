"""
sqlalchemy ORM engine initializing module
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db: Session = DBSession()
    try:
        yield db
    finally:
        db.close()
