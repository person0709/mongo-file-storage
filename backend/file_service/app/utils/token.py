from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from starlette import status

from api.models.jwt_payload import JWTPayload
from config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def auth_with_jwt(token: str = Depends(reusable_oauth2)) -> Optional[JWTPayload]:
    """
    Check if the JWT token is valid.
    Args:
        token: token to check

    Returns:
        Decoded JWT with all the claims
    """
    try:
        decoded_jwt = jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Credential validation failed.",
        )
    return JWTPayload(**decoded_jwt)
