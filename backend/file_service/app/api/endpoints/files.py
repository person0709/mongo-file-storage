"""
API endpoint for file storage
"""
from tempfile import NamedTemporaryFile
from typing import Optional, IO

from fastapi import APIRouter, UploadFile, File, Depends, Response, HTTPException, Form
from fastapi.params import Header
from filetype import filetype
from starlette import status

from api.models.file_request import (
    DownloadFileRequest,
    ReadFileInfoRequest,
    ListFileInfoRequest,
    DeleteFileRequest,
    SearchFileInfoRequest,
    ReadFileCountRequest,
    ReadUsageRequest,
)
from api.models.file_response import (
    UploadFileResponse,
    ReadFileInfoResponse,
    ListFileInfoResponse,
    DeleteFileResponse,
    SearchFileInfoResponse,
    ReadFileCountResponse,
    ReadUsageResponse,
)
from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from config import settings
from db.database import Database, get_db
from db.model.file_meta import FileMeta
from db.respositories.file_repository import FileRepository
from utils.exceptions import FileValidationError
from utils.file_validator import check_file
from utils.permission_checker import (
    check_upload_permission,
    check_download_permission,
    check_view_permission,
    check_delete_permission,
)

files_router = APIRouter()


@files_router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_upload_permission),
    content_length: int = Header(...),
):
    """
    Uploads file.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    - **file**: file to upload
    - **user_id**: target storage owner's id
    """
    # Check header to see if file is bigger than the limit
    if content_length > settings.FILE_SIZE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too big"
        )
    # Check if the size of the file is really what the header says, in case the header's been spoofed
    # Solution offered by the FastAPI creator; https://github.com/tiangolo/fastapi/issues/362
    real_file_size = 0
    temp: IO = NamedTemporaryFile()
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > content_length:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too big",
            )
        temp.write(chunk)
    temp.close()
    # reset file read pointer to start
    file.file.seek(0)

    if user_id and user_id != current_user_jwt.sub:
        if current_user_jwt.role == Role.ADMIN:
            # if user_id is provided and the role stored in JWT is admin, use the given user's storage as target
            storage_user_id = user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload files to other user's storage",
            )
    else:
        storage_user_id = current_user_jwt.sub

    # validate files
    try:
        check_file(file)
    except FileValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        upload_file_meta = await FileRepository(db).add_file(storage_user_id, file)
        return UploadFileResponse(**upload_file_meta.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@files_router.get("/download")
async def download_file(
    request: DownloadFileRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_download_permission),
):
    """
    Download a files with the given name from a given user's storage.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot download a file from another user's storage unless they are admins.
    - **filename**: filename to download
    - **user_id**: source storage owner's id
    """
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download other user's file",
            )
    else:
        request.user_id = current_user_jwt.sub

    try:
        file_in_bin: bytes = await FileRepository(db).download_file(
            storage_user_id=request.user_id, filename=request.filename
        )
        return Response(
            content=file_in_bin, media_type=filetype.guess_mime(file_in_bin)
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )


@files_router.get("", response_model=ReadFileInfoResponse)
async def get_file_meta(
    request: ReadFileInfoRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Get info of a file.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.
    - **filename**: filename to get info of
    - **user_id**: source storage owner's id
    """
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to get other user's files info",
            )
    else:
        request.user_id = current_user_jwt.sub
    try:
        meta_data: FileMeta = await FileRepository(db).read_file_info(
            storage_user_id=request.user_id, filename=request.filename
        )
        return ReadFileInfoResponse(**meta_data.dict())
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )


@files_router.get("/list/", response_model=ListFileInfoResponse)
async def get_file_meta_list(
    request: ListFileInfoRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Get info of list of files stored in DB with the given filter<br>
    The data will be fetched using the filter passed.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.<br>
    - **sort_by**: the field to sort the list by. `filename`, `length`, `uploaded_at`
    - **desc**: sorting direction. True for descending, false for ascending
    - **offset**: the number of items to skip from the head when returning the sorted list
    - **limit**: the maximum number of items to return
    - **user_id**: source storage owner's id
    """
    repo = FileRepository(db)
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to get other user's files info",
            )
    else:
        request.user_id = current_user_jwt.sub

    request.convert_sort_by()

    metadata_iterator = repo.list_files_info(
        storage_user_id=request.user_id,
        offset=request.offset,
        limit=request.limit,
        sort_by=request.sort_by,
        desc=request.desc,
    )
    response = ListFileInfoResponse()
    async for info in metadata_iterator:
        response.files.append(ReadFileInfoResponse(**info.dict()))
    return response


@files_router.get("/search/", response_model=SearchFileInfoResponse)
async def search_file(
    request: SearchFileInfoRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Search stored file meta from DB using the given regex pattern
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.<br>
    - **user_id**: source storage owner's id
    - **pattern**: regex pattern to search files with
    - **limit**: maximum number of items to return
    """
    repo = FileRepository(db)
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to get other user's files info",
            )
    else:
        request.user_id = current_user_jwt.sub

    metadata_iterator = repo.search_files_by_regex(
        storage_user_id=request.user_id,
        pattern=request.pattern,
        limit=request.limit,
    )

    response = SearchFileInfoResponse()
    async for info in metadata_iterator:
        response.files.append(ReadFileInfoResponse(**info.dict()))
    return response


@files_router.get("/count", response_model=ReadFileCountResponse)
async def count_file(
    request: ReadFileCountRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Get total number of stored files of a user.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.<br>
    - **user_id**: source storage owner's id
    """
    repo = FileRepository(db)
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to get other user's files info",
            )
    else:
        request.user_id = current_user_jwt.sub
    count = await repo.get_files_count(
        storage_user_id=request.user_id,
    )
    return ReadFileCountResponse(count=count)


@files_router.get("/usage", response_model=ReadUsageResponse)
async def get_usage(
    request: ReadUsageRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Get the total storage usage of a given user.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot get info of another user's storage unless they are admin.<br>
    - **user_id**: source storage owner's id
    """
    repo = FileRepository(db)
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to get other user's files info",
            )
    else:
        request.user_id = current_user_jwt.sub
    used = await repo.get_storage_usage(
        storage_user_id=request.user_id,
    )
    return ReadUsageResponse(storage_used=used)


@files_router.delete("", response_model=DeleteFileResponse)
async def delete_file(
    request: DeleteFileRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_delete_permission),
):
    """
    Delete a file.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot delete files from another user's storage unless they are admins.
    - **filename**: filename to delete
    - **user_id**: target storage owner's id
    """
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete other user's files",
            )
    else:
        request.user_id = current_user_jwt.sub

    if not await FileRepository(db).delete_file(
        storage_user_id=request.user_id, filename=request.filename
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return DeleteFileResponse(filename=request.filename)
