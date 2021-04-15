import pytest
from db.models.user import User
from fastapi import HTTPException
from jose import jwt, ExpiredSignatureError
from tests.mock_factories import UserFactory

from config import settings
from utils.token import generate_jwt, auth_with_jwt


def test_generate_jwt_claims():
    settings.JWT_SECRET_KEY = "secret"
    settings.JWT_ALGORITHM = "HS256"
    mock_user: User = UserFactory()
    token = generate_jwt(mock_user)
    assert token.token_type == "bearer"
    decoded_token = jwt.decode(token.access_token, key="secret", algorithms="HS256")
    assert decoded_token["sub"] == mock_user.user_id
    assert decoded_token["role"] == mock_user.role
    assert isinstance(decoded_token["exp"], int)


def test_generate_jwt_expire():
    settings.JWT_SECRET_KEY = "secret"
    settings.JWT_ALGORITHM = "HS256"
    # set negative expire minute to set expire date to past
    settings.TOKEN_EXPIRE_MINUTES = -1
    mock_user: User = UserFactory()
    token = generate_jwt(mock_user)
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token.access_token, key="secret", algorithms="HS256")


def test_auth_with_jwt():
    settings.JWT_SECRET_KEY = "secret"
    settings.JWT_ALGORITHM = "HS256"
    # set negative expire minute to set expire date to past
    settings.TOKEN_EXPIRE_MINUTES = -1
    mock_user: User = UserFactory()
    token = generate_jwt(mock_user)
    with pytest.raises(HTTPException):
        auth_with_jwt(token.access_token)
