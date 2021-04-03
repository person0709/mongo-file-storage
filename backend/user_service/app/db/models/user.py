import uuid

from sqlalchemy import Column, String, SmallInteger

from api.models.role import Role
from db.models.base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(36), primary_key=True, index=True, default=str(uuid.uuid4()))
    username = Column(String(32), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(32), default=Role.VIEWER.name)
    del_flag = Column(SmallInteger, default=0)
