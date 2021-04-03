from sqlalchemy.orm import Session

from api.models.role import Role
from db.models.user import User
from db.repositories.user_repository import UserRepository
from tests.mock_factories import UserFactory


def test_add_user(test_db: Session):
    """
    Test add user method in a successful case
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    user_added = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    assert user_added.email == mock_user.email
    assert user_added.role == Role.VIEWER
    user_in_db = test_db.query(User).filter(User.email == mock_user.email).first()
    assert user_in_db


def test_add_user_conflict(test_db: Session):
    """
    Test add user method where there is a key conflict.
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    user_added = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    assert user_added.email == mock_user.email
    assert user_added.role == Role.VIEWER
    # try adding the same user
    user_added = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    assert not user_added
    user_in_db = test_db.query(User).filter(User.email == mock_user.email).first()
    assert user_in_db


def test_get_user_by_user_id(test_db: Session):
    """
    Test getting user by its user id
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    assert repo.get_user_by_user_id(user_id=created_model.user_id)


def test_get_user_by_username(test_db: Session):
    """
    Test getting user by its username
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    assert repo.get_user_by_username(username=created_model.username)


def test_delete_user(test_db: Session):
    """
    Test soft deleting a user when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    added_user = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    repo.delete_user(user_id=added_user.user_id)
    assert repo.get_user_by_user_id(user_id=added_user.user_id).del_flag == 1


def test_delete_user_not_found(test_db: Session):
    """
    Test soft deleting a user when there is no matching row
    """
    repo = UserRepository(test_db)
    deleted_user = repo.delete_user(user_id="aaa")
    assert deleted_user is None


def test_update_user_role(test_db: Session):
    """
    Test updating a user's role when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(username=mock_user.username, email=mock_user.email, password="password")
    updated_model = repo.update_user_role(user_id=created_model.user_id, target_role=Role.UPLOADER)
    assert updated_model.role == Role.UPLOADER


def test_update_user_role_not_found(test_db: Session):
    """
    Test updating a user's role when there is no matching row
    """
    repo = UserRepository(test_db)
    updated_model = repo.update_user_role(user_id="aaa", target_role=Role.UPLOADER)
    assert updated_model is None
