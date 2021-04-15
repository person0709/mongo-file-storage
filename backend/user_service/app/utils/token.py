"""
A util module for all the token related operations
"""
from datetime import datetime, timedelta
from typing import Optional

from api.models.token import Token
from db.models.user import User
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from starlette import status

from api.models.jwt_payload import JWTPayload
from config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def generate_jwt(user: User) -> Token:
    """
    Generate a JWT using the user info provided.
    A JWT will contain all the necessary info for authorization and authentication in future transactions.
    Args:
        user: user model to create JWT with

    Returns:
        JWT typed bearer token
    """
    payload = JWTPayload(
        sub=user.user_id,
        exp=datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES),
        role=user.role,
        username=user.username,
        email=user.email,
    )
    return Token(
        token_type="bearer",
        access_token=jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM),
    )


def auth_with_jwt(token: str = Depends(reusable_oauth2)) -> Optional[JWTPayload]:
    try:
        decoded_jwt = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credential validation failed.",
        )
    return JWTPayload(**decoded_jwt)
