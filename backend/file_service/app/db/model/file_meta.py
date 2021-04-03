from datetime import datetime

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
        return FileMeta(
            id=str(obj["_id"]),
            filename=obj["filename"],
            uploaded_at=obj["uploadDate"],
            size=obj["length"],
            md5=obj["md5"],
            user_id=obj["metadata"]["user_id"],
        )
