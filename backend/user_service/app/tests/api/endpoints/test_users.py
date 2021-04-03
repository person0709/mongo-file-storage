from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient

from api.models.role import Role
from api.models.token import Token
from api.models.user_request import CreateUserRequest, UpdateUserRoleRequest, DeleteUserRequest
from db.models.user import User
from db.repositories.user_repository import UserRepository
from tests.mock_factories import UserFactory


def test_create_user(test_client: TestClient, test_db: Session):
    """
    Test the case where a user is added successfully
    """
    mock_user: User = UserFactory()
    request = CreateUserRequest(
        username=mock_user.username,
        email=mock_user.email,
        password="some_password",
    )
    response = test_client.post("/api/users/", json=request.dict())
    assert response.status_code == status.HTTP_200_OK


def test_create_user_duplicate_username(test_client: TestClient, test_db: Session):
    """
    Test the case where there is already a user with the same username in the DB when creating a user
    """
    mock_user: User = UserFactory()
    # add a user directly to DB
    UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    request = CreateUserRequest(
        # use the same username
        username=mock_user.username,
        email="mock@example.com",
        password="some_password",
    )
    response = test_client.post("/api/users/", json=request.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_duplicate_email(test_client: TestClient, test_db: Session):
    """
    Test the case where there is already a user with the same email in the DB when creating a user
    """
    mock_user: User = UserFactory()
    # add a user directly to DB
    UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    request = CreateUserRequest(
        # use the same username
        username="username",
        email=mock_user.email,
        password="some_password",
    )
    response = test_client.post("/api/users/", json=request.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_user_info_by_user_id_as_admin(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin gets info of a user by user id.
    An admin should be able to fetch all data including del_flag.
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    response = test_client.get("/api/users", params={"user_id": added_user.user_id}, headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    # only admin can see del_flag and user_id field
    assert response.json()["username"] == mock_user.username
    assert response.json()["user_id"] == added_user.user_id
    assert response.json()["del_flag"] == added_user.del_flag


def test_get_user_info_by_user_id_as_non_admin(test_client: TestClient, test_db: Session, non_admin_token_header: Token):
    """
    Test the case where a non-admin user requests info of another user by user id.
    The response should be a 403
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    response = test_client.get("/api/users", params={"user_id": added_user.user_id}, headers=non_admin_token_header)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_info_by_username_as_admin(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin gets info of a user by username. An admin should be able to fetch all data including del_flag.
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    response = test_client.get("/api/users/search", params={"username": mock_user.username}, headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    # only admin can see del_flag and user_id field
    assert response.json()["username"] == mock_user.username
    assert response.json()["user_id"] == added_user.user_id
    assert response.json()["del_flag"] == added_user.del_flag


def test_get_user_info_by_username_as_non_admin(
    test_client: TestClient, test_db: Session, non_admin_token_header: Token
):
    """
    Test the case where a non-admin user searches for a user by username of a different user. This is not allowed.
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    response = test_client.get(
        "/api/users/search", params={"username": mock_user.username}, headers=non_admin_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_info_by_username_as_non_admin_self(test_client: TestClient, test_db: Session):
    """
    Test the case where a non-admin user gets info of themselves. This is allowed.
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(mock_user.username, mock_user.email, password="some_password")
    token_response = test_client.post(
        "api/auth/token",
        data={"username": mock_user.email, "password": "some_password"},
    )
    response = test_client.get(
        "/api/users/search",
        params={"username": mock_user.username},
        headers={"Authorization": f"bearer {token_response.json()['access_token']}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == mock_user.username
    # privileged info is not sent
    assert "del_flag" not in response.json()
    assert "user_id" not in response.json()


def test_delete_user_as_admin(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin deletes an existing user
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = DeleteUserRequest(user_id=added_user.user_id)
    response = test_client.delete("/api/users/", json=request.dict(), headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    test_db.refresh(added_user)
    assert added_user.del_flag == 1


def test_delete_user_as_admin_not_found(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin deletes a non-existing user
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = DeleteUserRequest(user_id="non-existing-user")
    response = test_client.delete("/api/users/", json=request.dict(), headers=admin_token_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_as_non_admin(test_client: TestClient, test_db: Session, non_admin_token_header: Token):
    """
    Test the case where an non-admin tries to delete an existing user
    Should return 403
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = DeleteUserRequest(user_id=added_user.user_id)
    response = test_client.delete("/api/users/", json=request.dict(), headers=non_admin_token_header)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_as_admin(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin update an existing user's role
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = UpdateUserRoleRequest(user_id=added_user.user_id, target_role=Role.UPLOADER)
    response = test_client.put("/api/users/role", json=request.dict(), headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    test_db.refresh(added_user)
    assert added_user.role == Role.UPLOADER


def test_update_user_as_admin_not_found(test_client: TestClient, test_db: Session, admin_token_header: Token):
    """
    Test the case where an admin update a non-existing user's role
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = UpdateUserRoleRequest(user_id="non-existing-user", target_role=Role.UPLOADER)
    response = test_client.put("/api/users/role", json=request.dict(), headers=admin_token_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_as_non_admin(test_client: TestClient, test_db: Session, non_admin_token_header: Token):
    """
    Test the case where a non-admin user tries to update an existing user's role
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = UpdateUserRoleRequest(user_id=added_user.user_id, target_role=Role.UPLOADER)
    response = test_client.put("/api/users/role", json=request.dict(), headers=non_admin_token_header)
    assert response.status_code == status.HTTP_403_FORBIDDEN
