from typing import Optional

from sqlalchemy.exc import IntegrityError
from db.models.user import User
from db.repositories.base_repository import BaseRepository
from utils.password import get_hash


class UserRepository(BaseRepository):
    """
    Repository that contains all DB operations on user table.
    Each operation are intentionally very specific for a use case.
    """
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user row using an email address.
        Args:
            email: email address of target user

        Returns:
            A user row, or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        """
        Get a user row using a user id
        Args:
            user_id: user id of target user

        Returns:
            A user row, or None if not found
        """
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user row using a username
        Args:
            username: username of target user

        Returns:
            A user row, or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()

    def add_user(self, username: str, email: str, password: str) -> Optional[User]:
        """
        Add a user row into the table. Given password will be hashed before inserting.
        Args:
            username: username of the user to be created
            email: email of the user to be created
            password: password to be used for creation

        Returns:
            Added user model, or None if failed
        """
        user_to_add = User(username=username, email=email)
        user_to_add.hashed_password = get_hash(password)
        try:
            self.db.add(user_to_add)
            self.db.commit()
            self.db.refresh(user_to_add)
            return user_to_add
        except IntegrityError:
            self.db.rollback()
            return None

    def delete_user(self, user_id) -> Optional[User]:
        """
        Soft delete a user row with the given user id
        Args:
            user_id: user id of target user

        Returns:
            Deleted user model, or None if not found
        """
        user_to_delete = self.db.query(User).filter(User.user_id == user_id).first()
        if not user_to_delete:
            return None
        user_to_delete.del_flag = 1
        self.db.commit()
        self.db.refresh(user_to_delete)
        return user_to_delete

    def update_user_role(self, user_id: str, target_role) -> Optional[User]:
        """
        Update a user's role to the given target role.
        Args:
            user_id: user id of target user
            target_role: new role for the target user

        Returns:
            Updated user model, or None if not found
        """
        user_to_update = self.db.query(User).filter(User.user_id == user_id).first()
        if not user_to_update:
            return None
        user_to_update.role = target_role
        self.db.commit()
        self.db.refresh(user_to_update)
        return user_to_update
