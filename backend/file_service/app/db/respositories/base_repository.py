from db.database import Database


class BaseRepository:
    """
    Base class for the repository. Database connection will be shared among a process.
    """
    def __init__(self, db: Database):
        self.db = db
