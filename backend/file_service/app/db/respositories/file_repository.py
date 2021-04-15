from typing import AsyncIterable, Optional

import pymongo
from bson import ObjectId
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorGridOut

from db.model.file_meta import FileMeta
from db.respositories.base_repository import BaseRepository


class FileRepository(BaseRepository):
    async def add_file(self, storage_user_id: str, file: UploadFile) -> Optional[FileMeta]:
        """
        Add file to database and tag it with the given user id to mark its ownership
        Args:
            storage_user_id: the owner of the target file
            file: file to save

        Returns:
            document id of the saved file, None if failed saving
        """
        existing_file = await self.db.client["file_service"]["fs.files"].find_one(
            {"filename": file.filename, "metadata": {"user_id": storage_user_id}}
        )
        if existing_file:
            raise FileExistsError("File with the same name exists")
        file_id = await self.db.grid_client.upload_from_stream(
            filename=file.filename,
            source=await file.read(),
            metadata={"user_id": storage_user_id},
        )
        uploaded_file = await self.db.client["file_service"]["fs.files"].find_one({"_id": file_id})
        return FileMeta.from_odm(uploaded_file)

    async def download_file(self, storage_user_id: str, filename: str) -> Optional[bytes]:
        """
        Download file with the given filename and user id.
        Args:
            storage_user_id: the owner id of target file
            filename: filename of the file to download

        Returns:
            binary data of the file
        """
        doc = await self.db.client["file_service"]["fs.files"].find_one(
            {"filename": filename, "metadata": {"user_id": storage_user_id}}
        )
        if doc:
            result: AsyncIOMotorGridOut = await self.db.grid_client.open_download_stream(doc["_id"])
            return await result.read()
        else:
            raise FileNotFoundError("File not found")

    async def read_file_info(self, storage_user_id: str, filename: str) -> Optional[FileMeta]:
        """
        Get metadata of a file with the given filename and the owner's user id
        Args:
            storage_user_id: the owner of the target file
            filename: filename of the file to get metadata of

        Returns:
            metadata of the target file if found. None if not found.
        """
        result = await self.db.client["file_service"]["fs.files"].find_one(
            {"filename": filename, "metadata": {"user_id": storage_user_id}}
        )
        if result:
            return FileMeta.from_odm(result)
        else:
            raise FileNotFoundError("File not found")

    async def list_files_info(
        self,
        storage_user_id: str,
        offset: int,
        limit: int,
        sort_by: str = "uploadDate",
        desc: bool = True,
    ) -> AsyncIterable[FileMeta]:
        """
        Get the list of stored files' metadata using the given filters.
        This will most likely to be used for pagination.
        Args:
            storage_user_id: the owner of the files
            offset: number of docs to skip from the head of list
            limit: maximum number of docs to return
            sort_by: field to sort the list by. eg. filename, length
            desc: sorting direction. True if to sort by descending order

        Returns:
            async stream of metadata models
        """
        # default sorting field to upload date if not valid
        if sort_by not in ["filename", "length", "uploadDate"]:
            sort_by = "uploadDate"

        if desc:
            sort_dir = pymongo.DESCENDING
        else:
            sort_dir = pymongo.ASCENDING

        cursor = (
            self.db.client["file_service"]["fs.files"]
            .find({"metadata": {"user_id": storage_user_id}})
            .skip(offset)
            .limit(limit)
            .sort(sort_by, sort_dir)
        )
        async for doc in cursor:
            yield FileMeta.from_odm(doc)

    async def search_files_by_regex(self, storage_user_id: str, pattern: str, limit: int = 10):
        """
        Search the list of stored files' metadata by regex.
        Args:
            storage_user_id: the owner of the files
            pattern: regex pattern
            limit: maximum number of docs to return. 10 by default

        Returns:
            async stream of metadata models
        """
        cursor = (
            self.db.client["file_service"]["fs.files"]
            .find(
                {
                    "filename": {"$regex": pattern},
                    "metadata": {"user_id": storage_user_id},
                }
            )
            .limit(limit)
        )
        async for doc in cursor:
            yield FileMeta.from_odm(doc)

    async def get_files_count(self, storage_user_id: str) -> int:
        """
        Get the total number of files owned by the user
        Args:
            storage_user_id: the owner of the files

        Returns:
            Awaitable total number of files stored in DB
        """
        return await (
            self.db.client["file_service"]["fs.files"].count_documents({"metadata": {"user_id": storage_user_id}})
        )

    async def get_storage_usage(self, storage_user_id: str) -> int:
        """
        Get the total size of the given user's storage usage.
        Args:
            storage_user_id: user id to get the usage of

        Returns:
            Awaitable sum of all saved files' size in bytes
        """
        cursor = self.db.client["file_service"]["fs.files"].aggregate(
            [
                {"$match": {"metadata": {"user_id": storage_user_id}}},
                {"$group": {"_id": "null", "total_sum": {"$sum": "$length"}}},
            ]
        )
        try:
            result = await cursor.next()
            return result["total_sum"]
        except StopAsyncIteration:
            return 0

    async def delete_file(self, storage_user_id: str, filename: str) -> bool:
        """
        Delete file with the given owner id and filename
        Args:
            storage_user_id: the owner of the target file
            filename: the filename of a file to delete

        Returns:
            True if successful, False if failed
        """
        try:
            meta_data = await self.read_file_info(storage_user_id, filename)
        except FileNotFoundError:
            return False
        await self.db.grid_client.delete(ObjectId(meta_data.id))
        return True
