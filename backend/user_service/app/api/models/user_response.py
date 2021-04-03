"""
Models to represent CRUD operation responses for users.
Each model will contain only the appropriate info as the specific operation response.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr

from api.models.role import Role


class BaseUserResponse(BaseModel):
    pass


class CreateUserResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role


class ReadUserResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role
    user_id: Optional[str]
    del_flag: Optional[int]


class DeleteUserResponse(BaseUserResponse):
    username: str
    email: EmailStr


class UpdateUserRoleResponse(BaseUserResponse):
    username: str
    email: EmailStr
    role: Role
