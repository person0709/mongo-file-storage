from typing import AsyncIterable, Optional

from bson import ObjectId
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorGridOut

from api.models.sort_type import SortType
from db.model.file_meta import FileMeta
from db.respositories.base_repository import BaseRepository


class FileRepository(BaseRepository):
    async def add_file(self, storage_user_id: str, file: UploadFile) -> Optional[ObjectId]:
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
            filename=file.filename, source=await file.read(), metadata={"user_id": storage_user_id}
        )
        return file_id

    async def download_file(self, storage_user_id: str, filename: str) -> Optional[bytes]:
        """
        Download file with the given filename and user id.
        Args:
            storage_user_id: the owner id of target file
            filename: filename of the file to download

        Returns:
            binary data of the file
        """
        doc = await self.db.client["file_service"]["fs.files"].find_one({"filename": filename, "metadata": {"user_id": storage_user_id}})
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

    async def list_files_info(
        self, storage_user_id: str, offset: int, limit: int, sort_by: SortType
    ) -> AsyncIterable[FileMeta]:
        """
        Get the list of stored files' metadata using the given filters
        Args:
            storage_user_id: the owner of the files
            offset: number of docs to skip from the head of list
            limit: maximum number of docs to return
            sort_by: sorting method for the list. filename, size, uploaded date by descending or ascending.
            Check out SortType enum for the list

        Returns:
            async stream of metadata model
        """
        # parse sort_by parameter
        sort_field, sort_dir = SortType.parse_sort_type(sort_by)

        cursor = (
            self.db.client["file_service"]["fs.files"]
            .find({"metadata": {"user_id": storage_user_id}})
            .skip(offset)
            .limit(limit)
            .sort(sort_field, sort_dir)
        )
        async for doc in cursor:
            yield FileMeta.from_odm(doc)

    async def delete_file(self, storage_user_id: str, filename: str) -> bool:
        """
        Delete file with the given owner id and filename
        Args:
            storage_user_id: the owner of the target file
            filename: the filename of a file to delete

        Returns:
            True if successful, False if failed
        """
        meta_data = await self.read_file_info(storage_user_id, filename)
        if not meta_data:
            return False
        await self.db.grid_client.delete(ObjectId(meta_data.id))
        return True
