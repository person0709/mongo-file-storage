import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from config import settings


class MockDatabase:
    def __init__(self, loop):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(
            settings.MONGODB_URL, io_loop=loop
        )
        self.grid_client: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(
            self.client["file_service"]
        )

    async def create_index(self):
        # create index
        await self.client["file_service"]["fs.files"].create_index(
            [("metadata.user_id", pymongo.TEXT)]
        )
        await self.client["file_service"]["fs.files"].create_index(
            [("uploadDate", pymongo.DESCENDING)]
        )
        await self.client["file_service"]["fs.files"].create_index(
            [("length", pymongo.DESCENDING)]
        )
        await self.client["file_service"]["fs.files"].create_index(
            [("filename", pymongo.DESCENDING)]
        )
