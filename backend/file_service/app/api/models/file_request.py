from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel, conint


class BaseFileRequest(BaseModel):
    pass


class ReadFileInfoRequest(BaseFileRequest):
    user_id: Optional[str]
    filename: str


class UploadFileRequest(BaseFileRequest):
    user_id: Optional[str]
    file: UploadFile = File(...)


class DownloadFileRequest(BaseFileRequest):
    user_id: Optional[str]
    filename: str


class DeleteFileRequest(BaseFileRequest):
    user_id: Optional[str]
    filename: str


class ListFileInfoRequest(BaseFileRequest):
    user_id: Optional[str]
    offset: conint(ge=0, le=100) = 0
    limit: conint(ge=0, le=100) = 100
    sort_by: Optional[str] = "uploadDate"
    desc: Optional[bool] = True

    def convert_sort_by(self):
        """
        Convert sort_by values to the field names that are used in DB
        """
        if self.sort_by == "uploaded_at":
            self.sort_by = "uploadDate"
        elif self.sort_by == "size":
            self.sort_by = "length"


class SearchFileInfoRequest(BaseFileRequest):
    user_id: Optional[str]
    pattern: str
    limit: conint(le=30) = 10


class ReadFileCountRequest(BaseFileRequest):
    user_id: Optional[str]


class ReadUsageRequest(BaseFileRequest):
    user_id: Optional[str]
