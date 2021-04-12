from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class FileMeta(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime
    size: int  # file size in byte
    md5: str  # md5 hashing of the file
    user_id: str  # user id of the owner

    @classmethod
    def from_odm(cls, obj):
        """
        Convert from DB document model to FileMeta model
        Args:
            obj: ODM taken directly from DB

        Returns:
            FileMeta object
        """
        return FileMeta(
            id=str(obj["_id"]),
            filename=obj["filename"],
            uploaded_at=obj["uploadDate"],
            size=obj["length"],
            md5=obj["md5"],
            user_id=obj["metadata"]["user_id"],
        )

    @classmethod
    def to_odm(cls, obj):
        """
        Convert from FileMeta object to a dictionary that maps to an entry to metadata collection in DB
        Args:
            obj: FileMeta object to convert
        Returns:
            dict with the exact same mapping to BSON of metadata collection in DB
        """
        return {
            "_id": ObjectId(obj.id),
            "filename": obj.filename,
            "uploadDate": obj.uploaded_at,
            "length": obj.size,
            "md5": obj.md5,
            "metadata": {"user_id": obj.user_id},
        }
