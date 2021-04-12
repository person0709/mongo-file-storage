"""
API endpoint for authorization/authentication
"""
from api.models.token import Token
from db.repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status
from utils.password import verify_hash

from db.database import get_db
from utils import token

auth_router = APIRouter()


@auth_router.post("/token", response_model=Token)
def get_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Check given credentials against DB and issue a JWT if they match.<br>
    - **username**: email of the user
    - **password**: password of the user
    """
    repo = UserRepository(db)
    user = repo.get_user_by_email(email=form_data.username)
    if (
        user
        and user.is_active == 1
        and verify_hash(form_data.password, user.hashed_password)
    ):
        return token.generate_jwt(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
