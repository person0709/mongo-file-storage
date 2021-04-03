"""
API endpoint for file storage
"""
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, Response, HTTPException, Form
from filetype import filetype
from starlette import status

from api.models.file_request import (
    DownloadFileRequest,
    ReadFileInfoRequest,
    ListFileInfoRequest,
    DeleteFileRequest,
)
from api.models.file_response import UploadFileResponse, ReadFileInfoResponse, ListFileInfoResponse, DeleteFileResponse
from api.models.jwt_payload import JWTPayload
from api.models.role import Role
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
from utils.token import auth_with_jwt

files_router = APIRouter()


@files_router.post("/upload", response_model=UploadFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_upload_permission),
):
    """
    Uploads file.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    - **file**: file to upload
    - **user_id**: target storage owner's id
    """
    if user_id and user_id != current_user_jwt.sub:
        if current_user_jwt.role == Role.ADMIN:
            # if user_id is provided and the role stored in JWT is admin, use the given user's storage as target
            storage_user_id = user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload files to other user's storage"
            )
    else:
        storage_user_id = current_user_jwt.sub

    # validate files
    try:
        check_file(file)
    except FileValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        await FileRepository(db).add_file(storage_user_id, file)
        return UploadFileResponse(filename=file.filename)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@files_router.get("/download")
async def download_file(
    request=Depends(DownloadFileRequest),
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
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to download other user's file"
            )
    else:
        request.user_id = current_user_jwt.sub

    try:
        file_in_bin: bytes = await FileRepository(db).download_file(
            storage_user_id=request.user_id, filename=request.filename
        )
        return Response(content=file_in_bin, media_type=filetype.guess_mime(file_in_bin))
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@files_router.get("/", response_model=ReadFileInfoResponse)
async def get_file_meta(
    request: ReadFileInfoRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(check_view_permission),
):
    """
    Get info of a file.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.
    - **filename**: filename to download
    - **user_id**: source storage owner's id
    """
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get other user's files info"
            )
    else:
        request.user_id = current_user_jwt.sub
    meta_data: FileMeta = await FileRepository(db).read_file_info(
        storage_user_id=request.user_id, filename=request.filename
    )
    return ReadFileInfoResponse(**meta_data.dict())


@files_router.get("/list", response_model=ListFileInfoResponse)
async def get_file_meta_list(
    request: ListFileInfoRequest = Depends(),
    db: Database = Depends(get_db),
    current_user_jwt: JWTPayload = Depends(auth_with_jwt),
):
    """
    Get info of a list files.<br>
    The data will be fetched using the parameters passed.<br>
    If user_id is not provided, the caller's storage will be accessed by default.<br>
    A user cannot check files from another user's storage unless they are admins.<br>
    - **sort_by**: the method to sort the list.
        - filename_desc: sort by filename, descending
        - filename_asc: sort by filename, ascending
        - uploaded_date_desc: sort by uploaded date, descending
        - uploaded_date_asc: sort by uploaded date, ascending
        - size_desc: sort by file size, descending
        - size_asc: sort by file size, ascending
    - **offset**: the number of items to skip from the head when returning the sorted list
    - **limit**: the maximum number of items to return
    - **user_id**: source storage owner's id
    """
    if request.user_id and request.user_id != current_user_jwt.sub:
        if current_user_jwt.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to get other user's files info"
            )
    else:
        request.user_id = current_user_jwt.sub
    metadata_iterator = FileRepository(db).list_files_info(
        storage_user_id=request.user_id, offset=request.offset, limit=request.limit, sort_by=request.sort_by
    )
    response = ListFileInfoResponse()
    async for info in metadata_iterator:
        response.data.append(ReadFileInfoResponse(**info.dict()))

    return response


@files_router.delete("/", response_model=DeleteFileResponse)
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
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete other user's files"
            )
    else:
        request.user_id = current_user_jwt.sub

    if not await FileRepository(db).delete_file(storage_user_id=request.user_id, filename=request.filename):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return DeleteFileResponse(filename=request.filename)

