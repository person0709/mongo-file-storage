from api.models.token import Token
from api.models.user_request import (
    CreateUserRequest,
    UpdateUserRequest,
    DeleteUserRequest,
)
from db.models.user import User
from db.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from starlette import status
from starlette.testclient import TestClient
from tests.mock_factories import UserFactory

from api.models.role import Role
from utils.token import generate_jwt


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
    response = test_client.post("/api/users", json=request.dict())
    assert response.status_code == status.HTTP_200_OK


def test_create_user_duplicate_username(test_client: TestClient, test_db: Session):
    """
    Test the case where there is already a user with the same username in the DB when creating a user
    """
    mock_user: User = UserFactory()
    # add a user directly to DB
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = CreateUserRequest(
        # use the same username
        username=mock_user.username,
        email="mock@example.com",
        password="some_password",
    )
    response = test_client.post("/api/users", json=request.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_duplicate_email(test_client: TestClient, test_db: Session):
    """
    Test the case where there is already a user with the same email in the DB when creating a user
    """
    mock_user: User = UserFactory()
    # add a user directly to DB
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = CreateUserRequest(
        # use the same username
        username="username",
        email=mock_user.email,
        password="some_password",
    )
    response = test_client.post("/api/users", json=request.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_my_info(test_client: TestClient, test_db: Session):
    """
    Test the case where a non-admin user requests info of themselves.
    This should return the user's own info
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    token = generate_jwt(added_user)
    response = test_client.get(
        "/api/users/my", headers={"Authorization": f"bearer {token.access_token}"}
    )
    assert response.json()["username"] == added_user.username


def test_get_user_info_by_user_id_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin gets all user info list
    An admin should be able to fetch all data including active state.
    """
    mock_user1: User = UserFactory()
    mock_user2: User = UserFactory()
    mock_user3: User = UserFactory()
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    response = test_client.get("/api/users/", params={}, headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["users"]) == 3
    assert "is_active" in response.json()["users"][0]


def test_get_user_info_by_user_id_as_non_admin(
    test_client: TestClient, test_db: Session, non_admin_token_header: Token
):
    """
    Test the case where a non-admin user requests info of another user by user id.
    The response should be a 403
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    response = test_client.get(
        "/api/users/",
        params={"user_id": added_user.user_id},
        headers=non_admin_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_user_info_by_username_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin gets info of a user by username. An admin should be able to fetch all data including active state.
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    response = test_client.get(
        "/api/users/",
        params={"username": mock_user.username},
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    # only admin can see active state and user_id field
    assert response.json()["users"][0]["username"] == mock_user.username
    assert response.json()["users"][0]["user_id"] == added_user.user_id
    assert response.json()["users"][0]["is_active"] == added_user.is_active


def test_get_user_info_by_partial_username_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin gets info of a user by partial username.
    An admin should be able to fetch all data including active state.
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    response = test_client.get(
        "/api/users/",
        params={"username": mock_user.username[:5]},
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    # only admin can see active state and user_id field
    assert response.json()["users"][0]["username"] == mock_user.username
    assert response.json()["users"][0]["user_id"] == added_user.user_id
    assert response.json()["users"][0]["is_active"] == added_user.is_active


def test_get_user_info_by_partial_email_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin gets info of a user by partial username.
    An admin should be able to fetch all data including active state.
    """
    mock_user: User = UserFactory()
    added_user = UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    response = test_client.get(
        "/api/users/", params={"email": mock_user.email[:5]}, headers=admin_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    # only admin can see active state and user_id field
    assert response.json()["users"][0]["username"] == mock_user.username
    assert response.json()["users"][0]["user_id"] == added_user.user_id
    assert response.json()["users"][0]["is_active"] == added_user.is_active


def test_list_user_sort(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the sort function in list user endpoint
    An admin should be able to fetch all data including active state.
    """
    mock_user: User = UserFactory.build_batch(30)
    test_db.add_all(mock_user)
    response = test_client.get(
        "/api/users/",
        params={"sort_by": "joined_at", "desc": "false"},
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["users"]
    for i in range(len(data)):
        assert data[i].joined_at > data[i + 1].joined_at


def test_get_user_info_by_username_as_non_admin(
    test_client: TestClient, test_db: Session, non_admin_token_header: Token
):
    """
    Test the case where a non-admin user searches for a user by username of a different user. This is not allowed.
    """
    mock_user: User = UserFactory()
    UserRepository(test_db).add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    response = test_client.get(
        "/api/users/",
        params={"username": mock_user.username},
        headers=non_admin_token_header,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_user_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin deletes an existing user
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = DeleteUserRequest(user_id=added_user.user_id)
    response = test_client.delete(
        "/api/users", params=request.dict(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        test_db.query(User).filter(User.user_id == added_user.user_id).first() is None
    )


def test_delete_user_as_admin_not_found(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin deletes a non-existing user
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = DeleteUserRequest(user_id="non-existing-user")
    response = test_client.delete(
        "/api/users", params=request.dict(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user_as_non_admin(
    test_client: TestClient, test_db: Session, non_admin_token_header: Token
):
    """
    Test the case where an non-admin tries to delete an existing user
    Should return 403
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = DeleteUserRequest(user_id=added_user.user_id)
    response = test_client.delete(
        "/api/users", params=request.dict(), headers=non_admin_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user_as_admin(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin update an existing user's role
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = UpdateUserRequest(
        user_id=added_user.user_id,
        role=Role.UPLOADER,
        storage_allowance=500,
        is_active=False,
    )
    response = test_client.put(
        "/api/users", json=request.dict(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    test_db.refresh(added_user)
    assert added_user.role == Role.UPLOADER
    assert added_user.storage_allowance == 500
    assert added_user.is_active == 0


def test_update_user_as_admin_not_found(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin update a non-existing user's role
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    repo.add_user(mock_user.username, mock_user.email, password="some_password")
    request = UpdateUserRequest(user_id="non-existing-user", role=Role.UPLOADER)
    response = test_client.put(
        "/api/users", json=request.dict(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_as_non_admin(
    test_client: TestClient, test_db: Session, non_admin_token_header: Token
):
    """
    Test the case where a non-admin user tries to update an existing user
    """
    mock_user: User = UserFactory()
    repo = UserRepository(test_db)
    added_user = repo.add_user(
        mock_user.username, mock_user.email, password="some_password"
    )
    request = UpdateUserRequest(user_id=added_user.user_id, role=Role.UPLOADER)
    response = test_client.put(
        "/api/users", json=request.dict(), headers=non_admin_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_admin_themselves(
    test_client: TestClient, test_db: Session, admin_token_header: Token
):
    """
    Test the case where an admin tries to demote themselves
    """
    mock_user: User = UserFactory(user_id="admin_id", role=Role.ADMIN)
    test_db.add(mock_user)
    test_db.commit()
    request = UpdateUserRequest(user_id="admin_id", role=Role.UPLOADER)
    response = test_client.put(
        "/api/users", json=request.dict(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
