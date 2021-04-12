from api.models.token import Token
from db.models.user import User
from db.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient
from tests.mock_factories import UserFactory


def test_get_token(test_client: TestClient, test_db: Session):
    """
    Test the case where a user gets a token successfully with the correct credentials
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    data = {"username": mock_user.email, "password": "some_password"}
    response = test_client.post("/api/auth/token", data=data)
    token: Token = Token(**response.json())
    assert response.status_code == status.HTTP_200_OK
    assert token.token_type == "bearer"
    # JWT has 3 parts
    assert len(token.access_token.split(".")) == 3


def test_get_token_fail_wrong_password(test_client: TestClient, test_db: Session):
    """
    Test the case where a user fails to get a token due to incorrect password
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    data = {"username": mock_user.email, "password": "some_wrong_password"}
    response = test_client.post("/api/auth/token", data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_token_fail_wrong_email(test_client: TestClient, test_db: Session):
    """
    Test the case where a user fails to get a token due to non-existent email
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    data = {"username": "wrong@example.com", "password": "some_password"}
    response = test_client.post("/api/auth/token", data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_token_fail_deleted_user(test_client: TestClient, test_db: Session):
    """
    est the case where a user fails to get a token due to the user being deleted
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory(is_active=False)
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    repo.delete_user(user_id=added_user.user_id)
    data = {"username": mock_user.email, "password": "some_password"}
    response = test_client.post("/api/auth/token", data=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
