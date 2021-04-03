from typing import Optional

from fastapi import UploadFile, File
from pydantic import BaseModel, conint

from api.models.sort_type import SortType


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
    sort_by: SortType = SortType.UPLOADED_DATE_DESC
