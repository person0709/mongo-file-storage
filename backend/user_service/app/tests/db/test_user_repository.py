from db.models.user import User
from db.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from tests.mock_factories import UserFactory

from api.models.role import Role


def test_add_user(test_db: Session):
    """
    Test add user method in a successful case
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    user_added = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    assert user_added.email == mock_user.email
    assert user_added.role == Role.UPLOADER
    user_in_db = test_db.query(User).filter(User.email == mock_user.email).first()
    assert user_in_db


def test_add_user_conflict(test_db: Session):
    """
    Test add user method where there is a key conflict.
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    user_added = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    assert user_added.email == mock_user.email
    assert user_added.role == Role.UPLOADER
    # try adding the same user
    user_added = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    assert not user_added
    user_in_db = test_db.query(User).filter(User.email == mock_user.email).first()
    assert user_in_db


def test_get_user_by_user_id(test_db: Session):
    """
    Test getting user by its user id
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    assert repo.get_user_by_user_id(user_id=created_model.user_id)


def test_get_user_by_username(test_db: Session):
    """
    Test getting user by its username
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    assert repo.get_user_by_username(username=created_model.username)


def test_get_users_by_filter_username(test_db: Session):
    """
    Test getting user by filter username
    """
    repo = UserRepository(test_db)
    mock_user1: User = UserFactory()
    mock_user2: User = UserFactory()
    mock_user3: User = UserFactory()
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    result, count = repo.get_users_by_filter(username=mock_user1.username)
    assert count == 1
    assert result[0].username == mock_user1.username


def test_get_users_by_filter_user_id(test_db: Session):
    """
    Test getting user by filter user_id
    """
    repo = UserRepository(test_db)
    mock_user1: User = UserFactory()
    mock_user2: User = UserFactory()
    mock_user3: User = UserFactory()
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    result, count = repo.get_users_by_filter(user_id=mock_user2.user_id)
    assert count == 1
    assert result[0].user_id == mock_user2.user_id


def test_get_users_by_filter_email(test_db: Session):
    """
    Test getting user by filter email
    """
    repo = UserRepository(test_db)
    mock_user1: User = UserFactory()
    mock_user2: User = UserFactory()
    mock_user3: User = UserFactory()
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    result, count = repo.get_users_by_filter(email=mock_user3.email)
    assert count == 1
    assert result[0].email == mock_user3.email


def test_get_users_by_filter_role(test_db: Session):
    """
    Test getting user by filter role
    """
    repo = UserRepository(test_db)
    mock_user1: User = UserFactory(role=Role.UPLOADER)
    mock_user2: User = UserFactory(role=Role.UPLOADER)
    mock_user3: User = UserFactory(role=Role.ADMIN)
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    result, count = repo.get_users_by_filter(role=Role.UPLOADER)
    assert count == 2
    assert mock_user2 in result


def test_get_users_by_filter_with_offset_limit(test_db: Session):
    """
    Test getting user by filter with offset and limit
    """
    repo = UserRepository(test_db)
    mock_user_batch: User = UserFactory.build_batch(30)
    test_db.add_all(mock_user_batch)
    test_db.commit()
    result, count = repo.get_users_by_filter(offset=10, limit=20)
    assert count == 30
    # check sort
    for i in range(len(result) - 1):
        assert result[i].joined_at >= result[i + 1].joined_at


def test_get_users_by_filter_with_offset_limit_partial(test_db: Session):
    """
    Test getting user by filter with offset and limit
    """
    repo = UserRepository(test_db)
    mock_user_batch: User = UserFactory.build_batch(30)
    test_db.add_all(mock_user_batch)
    test_db.commit()
    result, count = repo.get_users_by_filter(offset=20, limit=20)
    # total number of rows that are present is 30
    assert count == 30
    # should only be 10 selected. 20 + 20 - 30
    assert len(result) == 10
    # check sort
    for i in range(len(result) - 1):
        assert result[i].joined_at >= result[i + 1].joined_at


def test_get_users_by_filter_with_sort_by_desc(test_db: Session):
    """
    Test getting user by filter with sort_by args in desc order
    """
    repo = UserRepository(test_db)
    mock_user_batch: User = UserFactory.build_batch(30)
    test_db.add_all(mock_user_batch)
    test_db.commit()
    result, count = repo.get_users_by_filter(sort_by="username", desc=True)
    assert count == 30
    # check sort
    for i in range(len(result) - 1):
        assert result[i].username >= result[i + 1].username


def test_get_users_by_filter_with_invalid_sort_by(test_db: Session):
    """
    Test getting user by filter with invalid sort_by arg
    """
    repo = UserRepository(test_db)
    mock_user_batch: User = UserFactory.build_batch(30)
    test_db.add_all(mock_user_batch)
    test_db.commit()
    result, count = repo.get_users_by_filter(sort_by="some_invalid_field")
    assert count == 30
    # should default to joined_at
    for i in range(len(result) - 1):
        assert result[i].joined_at >= result[i + 1].joined_at


def test_get_users_by_filter_with_partial_match(test_db: Session):
    """
    Test getting user by partial match
    """
    repo = UserRepository(test_db)
    mock_user1: User = UserFactory(username="halla")
    mock_user2: User = UserFactory(username="bolla")
    mock_user3: User = UserFactory(username="lambda")
    test_db.add_all([mock_user1, mock_user2, mock_user3])
    test_db.commit()
    result, count = repo.get_users_by_filter(username="lla")
    assert count == 2
    assert len(result) == 2


def test_delete_user(test_db: Session):
    """
    Test hard deleting a user when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    added_user = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    repo.delete_user(user_id=added_user.user_id)
    assert (
        test_db.query(User).filter(User.user_id == added_user.user_id).first() is None
    )


def test_delete_user_not_found(test_db: Session):
    """
    Test hard deleting a user when there is no matching row
    """
    repo = UserRepository(test_db)
    is_deleted = repo.delete_user(user_id="aaa")
    assert is_deleted is False


def test_update_user_role(test_db: Session):
    """
    Test updating a user's role when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    updated_model = repo.update_user(user_id=created_model.user_id, role=Role.UPLOADER)
    assert updated_model.role == Role.UPLOADER


def test_update_user_allowance(test_db: Session):
    """
    Test updating a user's allowance when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    updated_model = repo.update_user(
        user_id=created_model.user_id, storage_allowance=100
    )
    assert updated_model.storage_allowance == 100


def test_update_user_active(test_db: Session):
    """
    Test updating a user's allowance when there is a matching row
    """
    repo = UserRepository(test_db)
    mock_user: User = UserFactory()
    created_model = repo.add_user(
        username=mock_user.username, email=mock_user.email, password="password"
    )
    updated_model = repo.update_user(user_id=created_model.user_id, is_active=False)
    assert updated_model.is_active == 0


def test_update_user_role_not_found(test_db: Session):
    """
    Test updating a user's role when there is no matching row
    """
    repo = UserRepository(test_db)
    updated_model = repo.update_user(user_id="aaa", role=Role.UPLOADER)
    assert updated_model is None
