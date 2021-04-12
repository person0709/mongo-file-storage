from datetime import datetime
from typing import List

from pydantic import BaseModel


class BaseFileResponse(BaseModel):
    pass


class ReadFileInfoResponse(BaseFileResponse):
    filename: str
    uploaded_at: datetime
    size: int  # file size in byte
    md5: str  # md5 hashing of the file


class UploadFileResponse(BaseFileResponse):
    filename: str
    uploaded_at: datetime
    size: int
    md5: str


class DownloadFileResponse(BaseFileResponse):
    file: bytes


class DeleteFileResponse(BaseFileResponse):
    filename: str


class ListFileInfoResponse(BaseFileResponse):
    files: List[ReadFileInfoResponse] = []


class SearchFileInfoResponse(BaseFileResponse):
    files: List[ReadFileInfoResponse] = []


class ReadFileCountResponse(BaseFileResponse):
    count: int


class ReadUsageResponse(BaseFileResponse):
    storage_used: int
