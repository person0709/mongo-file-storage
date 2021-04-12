"""
Models to represent CRUD operation requests for users.
Each model will contain only the necessary fields for the specific operation.
e.g. username, email and password are required to created a user, but only user_id is enough to delete a user
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, conint

from api.models.role import Role


class BaseUserRequest(BaseModel):
    pass


class ListUsersRequest(BaseUserRequest):
    user_id: Optional[str]
    username: Optional[str]
    email: Optional[str]
    role: Optional[str]
    sort_by: Optional[str] = "joined_at"
    desc: Optional[bool] = True
    offset: Optional[int] = 0
    limit: conint(le=100) = 50


class CreateUserRequest(BaseUserRequest):
    username: str
    email: EmailStr
    password: str


class DeleteUserRequest(BaseUserRequest):
    user_id: str


class UpdateUserRequest(BaseUserRequest):
    user_id: str
    role: Optional[Role]
    storage_allowance: Optional[int]
    is_active: Optional[bool]
