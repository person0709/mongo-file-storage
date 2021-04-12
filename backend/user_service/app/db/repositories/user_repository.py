from typing import Optional, List, Tuple

import sqlalchemy
from db.models.user import User
from db.repositories.base_repository import BaseRepository
from utils.password import get_hash

from api.models.role import Role


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

    def get_users_by_filter(
        self,
        user_id: str = None,
        username: str = None,
        email: str = None,
        role: Role = None,
        sort_by: str = "joined_at",
        desc: bool = True,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[User], int]:
        """
        Get a user row using various filters
        Args:
            user_id: user id to filter by
            username: substring of username to partial match by
            email: substring email to partial by
            role: user role to filter by
            sort_by: the field to order the list by
            desc: direction of the order. True if descending False if Ascending
            offset: number of items to skip. Used for pagination
            limit: max number of items to select

        Returns:
            List of users
        """
        filter_list = []
        if user_id:
            filter_list.append(User.user_id == user_id)
        elif username:
            filter_list.append(User.username.contains(username))
        elif email:
            filter_list.append(User.email.contains(email))
        if role:
            filter_list.append(User.role == role)

        # default to joined_at if given order by field is invalid
        if sort_by not in User.__table__.columns:
            sort_by = "joined_at"

        if desc:
            order_by_query = sqlalchemy.desc(getattr(User, sort_by))
        else:
            order_by_query = sqlalchemy.asc(getattr(User, sort_by))

        filter_query = self.db.query(User).filter(*filter_list)
        count = filter_query.count()
        return (
            self.db.query(User)
            .filter(*filter_list)
            .order_by(order_by_query)
            .offset(offset)
            .limit(limit)
            .all(),
            count,
        )

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
        except sqlalchemy.exc.IntegrityError:
            self.db.rollback()
            return None

    def delete_user(self, user_id) -> bool:
        """
        Soft delete a user row with the given user id
        Args:
            user_id: user id of target user

        Returns:
            True if deleted, false if failed
        """
        deleted_row = self.db.query(User).filter(User.user_id == user_id).delete()
        self.db.commit()
        return bool(deleted_row)

    def update_user(
        self,
        user_id: str,
        role: Role = None,
        storage_allowance: int = None,
        is_active: bool = None,
    ) -> Optional[User]:
        """
        Update a user's role to the given target role.
        Args:
            user_id: user id of target user
            role: new role for the target user
            storage_allowance: new allowance for the target user
            is_active: new active state for the target user

        Returns:
            Updated user model, or None if not found
        """
        user_to_update: User = (
            self.db.query(User).filter(User.user_id == user_id).first()
        )
        if not user_to_update:
            return None
        if role:
            user_to_update.role = role
        if storage_allowance:
            user_to_update.storage_allowance = storage_allowance
        if is_active is not None:
            user_to_update.is_active = is_active
        self.db.commit()
        self.db.refresh(user_to_update)
        return user_to_update
