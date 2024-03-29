import uuid
from datetime import datetime

from db.models.base import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime

from api.models.role import Role


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(36), primary_key=True, unique=True, index=True, default=generate_uuid)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    # storage allowance for the user in bytes(B)
    storage_allowance = Column(Integer, default=100_000_000, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default=Role.UPLOADER.name, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
