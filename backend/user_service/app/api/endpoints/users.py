"""
API endpoint for user CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from api.models.user_request import CreateUserRequest, DeleteUserRequest, UpdateUserRoleRequest
from api.models.user_response import ReadUserResponse, CreateUserResponse, DeleteUserResponse, UpdateUserRoleResponse
from db.database import get_db
from db.repositories.user_repository import UserRepository
from utils.token import auth_with_jwt

user_router = APIRouter()


@user_router.get("/", response_model=ReadUserResponse, response_model_exclude_unset=True)
def get_user_info_by_user_id(
    user_id: str,
    current_user_jwt: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
) -> ReadUserResponse:
    """
    Fetch user info using user id.<br>
    User id should not be shared with users, so only admin can use this endpoint.<br>
    - **user_id**: unique key for a user
    """
    if current_user_jwt.role == Role.ADMIN:
        user = UserRepository(db).get_user_by_user_id(user_id)
        return ReadUserResponse(**user.__dict__)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the action")


@user_router.get("/search", response_model=ReadUserResponse, response_model_exclude_unset=True)
def get_user_info_by_username(
    username: str,
    current_user_jwt: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
) -> ReadUserResponse:
    """
    Fetch user info using the username.<br>
    Only admin can get full detail such as del_flag, otherwise we simply decode JWT and return info in it.<br>
    - **username**: username to find info of
    """
    # return all user info from DB if requested by admin
    if current_user_jwt.role == Role.ADMIN:
        user = UserRepository(db).get_user_by_username(username)
        return ReadUserResponse(**user.__dict__)
    else:
        # only return basic info if the user is requesting their own
        if username == current_user_jwt.username:
            return ReadUserResponse(username=current_user_jwt.username, email=current_user_jwt.email, role=current_user_jwt.role)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the action")


@user_router.post("/", response_model=CreateUserResponse)
def create_user(request: CreateUserRequest, db: Session = Depends(get_db)) -> CreateUserResponse:
    """
    Create a user with the provided credentials.<br>
    Email and username must be unique.<br>
    - **username**: username of the creating user
    - **email**: email of the creating user
    - **password**: password for the account
    """
    repo = UserRepository(db)
    if repo.get_user_by_email(request.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use.")

    if repo.get_user_by_username(request.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use.")

    added_user = repo.add_user(**request.dict())
    return CreateUserResponse(**added_user.__dict__)


@user_router.delete("/", response_model=DeleteUserResponse)
def delete_user(
    request: DeleteUserRequest, jwt_data: JWTPayload = Depends(auth_with_jwt), db: Session = Depends(get_db)
) -> DeleteUserResponse:
    """
    Soft delete a user with the provided user id<br>
    Only an admin can delete a user.<br>
    - **user_id**: user_id of the deleting user
    """
    # user must be an admin
    if jwt_data.role == Role.ADMIN:
        deleted_user = UserRepository(db).delete_user(request.user_id)
        if not deleted_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return DeleteUserResponse(**deleted_user.__dict__)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the action")


@user_router.put("/role", response_model=UpdateUserRoleResponse)
def update_user_role(
    request: UpdateUserRoleRequest, jwt_data: JWTPayload = Depends(auth_with_jwt), db: Session = Depends(get_db)
):
    """
    Update a user's role.<br>
    Only an admin can change a user's role.<br>
    An admin cannot change another admin's role.<br>
    - **user_id**: user id to change role of
    - **target_role**: target role for the update
    """
    # user must be an admin
    if jwt_data.role == Role.ADMIN:
        repo = UserRepository(db)
        target_user = repo.get_user_by_user_id(request.user_id)
        # return 404 if target user is not found
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # error if target user is also an admin
        if target_user.role == Role.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the action")

        updated_user = UserRepository(db).update_user_role(request.user_id, request.target_role)
        return UpdateUserRoleResponse(**updated_user.__dict__)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the action")
