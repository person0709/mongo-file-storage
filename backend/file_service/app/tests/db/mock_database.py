from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


class MockDatabase:
    def __init__(self, loop):
        self.client: AsyncIOMotorClient = AsyncIOMotorClient("mongodb://localhost:27017", io_loop=loop)
        self.grid_client: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(self.client["file_service"])
