"""
Models to represent CRUD operation requests for users.
Each model will contain only the necessary fields for the specific operation.
e.g. username, email and password are required to created a user, but only user_id is enough to delete a user
"""
from typing import Optional

from pydantic import BaseModel, EmailStr

from api.models.role import Role


class BaseUserRequest(BaseModel):
    pass


class CreateUserRequest(BaseUserRequest):
    username: str
    email: EmailStr
    password: str


class DeleteUserRequest(BaseUserRequest):
    user_id: str


class UpdateUserRoleRequest(BaseUserRequest):
    user_id: str
    target_role: Role
