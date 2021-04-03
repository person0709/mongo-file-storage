import pytest
from jose import jwt, ExpiredSignatureError

from config import settings
from db.models.user import User
from tests.mock_factories import UserFactory
from utils.token import generate_jwt


def test_generate_jwt_claims():
    settings.SECRET_KEY = "secret"
    settings.JWT_ALGORITHM = "HS256"
    mock_user: User = UserFactory()
    token = generate_jwt(mock_user)
    assert token.token_type == "bearer"
    decoded_token = jwt.decode(token.access_token, key="secret", algorithms="HS256")
    assert decoded_token["sub"] == mock_user.user_id
    assert decoded_token["role"] == mock_user.role
    assert isinstance(decoded_token["exp"], int)


def test_generate_jwt_expire():
    settings.SECRET_KEY = "secret"
    settings.JWT_ALGORITHM = "HS256"
    # set negative expire minute to set expire date to past
    settings.TOKEN_EXPIRE_MINUTES = -1
    mock_user: User = UserFactory()
    token = generate_jwt(mock_user)
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token.access_token, key="secret", algorithms="HS256")
