from fastapi import APIRouter

from api.endpoints.files import files_router

api_router = APIRouter()
api_router.include_router(files_router, prefix="/files", tags=["files"])
