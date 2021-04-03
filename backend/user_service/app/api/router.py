from fastapi import APIRouter

from api.endpoints.auth import auth_router
from api.endpoints.users import user_router

api_router = APIRouter()
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
