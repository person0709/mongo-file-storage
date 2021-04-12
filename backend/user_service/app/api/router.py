from api.endpoints.auth import auth_router
from api.endpoints.users import user_router
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
