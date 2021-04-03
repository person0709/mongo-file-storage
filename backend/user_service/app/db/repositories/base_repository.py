from sqlalchemy.orm import Session


class BaseRepository:
    """
    Base class for all repositories. Initialized with a sqlalchemy db session.
    """
    def __init__(self, db: Session):
        self.db = db
