"""
Models to represent CRUD operation responses for users.
Each model will contain only the appropriate info as the specific operation response.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr

from api.models.role import Role


class BaseUserResponse(BaseModel):
    pass


class CreateUserResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role
    storage_allowance: int


class ReadUserResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role
    storage_allowance: int
    joined_at: datetime
    user_id: Optional[str]
    is_active: Optional[bool]


class ListUsersResponse(BaseUserResponse):
    users: List[ReadUserResponse] = []
    count: int


class DeleteUserResponse(BaseUserResponse):
    user_id: str


class UpdateUserResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role
    storage_allowance: int
    is_active: bool
