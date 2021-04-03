"""
API endpoint for authorization/authentication
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from api.models.token import Token
from db.database import get_db
from db.repositories.user_repository import UserRepository
from utils import token
from utils.password import verify_hash

auth_router = APIRouter()


@auth_router.post("/token", response_model=Token)
def get_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Check given credentials against DB and issue a JWT if they match.<br>
    - **username**: email of the user
    - **password**: password of the user
    """
    repo = UserRepository(db)
    user = repo.get_user_by_email(email=form_data.username)
    if user and user.del_flag == 0 and verify_hash(form_data.password, user.hashed_password):
        return token.generate_jwt(user)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
