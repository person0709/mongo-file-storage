import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from config import settings


class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.grid_client: AsyncIOMotorGridFSBucket = None


db = Database()


def get_db() -> Database:
    return db


async def open_db_connection() -> None:
    """
    Opens connection to DB. This will be initiated as the API service starts up
    """
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.grid_client = AsyncIOMotorGridFSBucket(db.client["file_service"])

    # create index
    await db.client["file_service"]["fs.files"].create_index([("metadata.user_id", pymongo.TEXT)])
    await db.client["file_service"]["fs.files"].create_index([("uploadDate", pymongo.DESCENDING)])
    await db.client["file_service"]["fs.files"].create_index([("length", pymongo.DESCENDING)])
    await db.client["file_service"]["fs.files"].create_index([("filename", pymongo.DESCENDING)])


async def close_db_connection() -> None:
    """
    Closes connection to DB. This will be initiated as the API service shuts down
    """
    db.client.close()
