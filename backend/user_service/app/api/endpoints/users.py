"""
API endpoint for user CRUD operations
"""

from api.models.user_request import (
    CreateUserRequest,
    DeleteUserRequest,
    UpdateUserRequest,
    ListUsersRequest,
)
from api.models.user_response import (
    ReadUserResponse,
    CreateUserResponse,
    DeleteUserResponse,
    UpdateUserResponse,
    ListUsersResponse,
)
from db.repositories.user_repository import UserRepository
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from db.database import get_db
from utils.token import auth_with_jwt

from fastapi.logger import logger

user_router = APIRouter()


@user_router.get(
    "/my", response_model=ReadUserResponse, response_model_exclude_unset=True
)
def get_users(
    current_user_jwt: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
) -> ReadUserResponse:
    """
    Get current user's info.<br>
    - **user_id**: user id of the user to get info of
    """
    user = UserRepository(db).get_user_by_user_id(current_user_jwt.sub)
    return ReadUserResponse(**user.__dict__)


@user_router.get("/", response_model=ListUsersResponse)
def get_users(
    request: ListUsersRequest = Depends(),
    current_user_jwt: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
) -> ListUsersResponse:
    """
    Fetch a list of users using the given filters.<br>
    User id should not be public, so only admin can query using other users' id<br>
    - **user_id**: user id of the user, must be exact
    - **username**: username of the user, can be partial
    - **email**: email of the user, can be partial
    - **role**: role of the user
    - **sort_by**: field to order by the list
    - **desc**: sorting direction. True for descending
    - **offset**: number of rows to skip from the head of list
    - **limit**: max number of rows to return
    """
    if current_user_jwt.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the action",
        )

    user_list, count = UserRepository(db).get_users_by_filter(**request.dict())
    response = ListUsersResponse(count=count)
    for user in user_list:
        response.users.append(ReadUserResponse(**user.__dict__))
    return response


@user_router.post("", response_model=CreateUserResponse)
def create_user(
    request: CreateUserRequest, db: Session = Depends(get_db)
) -> CreateUserResponse:
    """
    Create a user with the provided credentials.<br>
    Email and username must be unique.<br>
    - **username**: username of the creating user
    - **email**: email of the creating user
    - **password**: password for the account
    """
    repo = UserRepository(db)
    if repo.get_user_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use."
        )

    if repo.get_user_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use."
        )

    added_user = repo.add_user(**request.dict())
    logger.info(f"Created user {added_user.user_id}, {added_user.email}, {added_user.username}")
    return CreateUserResponse(**added_user.__dict__)


@user_router.put("", response_model=UpdateUserResponse)
def update_user(
    request: UpdateUserRequest,
    jwt_data: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
):
    """
    Update a user's role and/or allowance.<br>
    Only an admin can change a user.<br>
    - **user_id**: user id to change role of
    - **role**: target role for the update
    - **storage_allowance**: target value for storage allowance update
    - **is_active**: target value for active state update
    """
    # user must be an admin
    if jwt_data.role == Role.ADMIN:
        repo = UserRepository(db)
        target_user = repo.get_user_by_user_id(request.user_id)
        # return 404 if target user is not found
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        # prevent admin demoting themselves
        elif request.user_id == jwt_data.sub and request.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin cannot demote themselves",
            )

        logger.info(
            f"Updating user {target_user.user_id}, {target_user.email}, {target_user.username}: "
            f"{target_user.role} {target_user.storage_allowance} {target_user.is_active} => "
            f"{request.role} {request.storage_allowance} {request.is_active}")
        updated_user = repo.update_user(**request.dict())
        return UpdateUserResponse(**updated_user.__dict__)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the action",
        )


@user_router.delete("", response_model=DeleteUserResponse)
def delete_user(
    request: DeleteUserRequest = Depends(),
    jwt_data: JWTPayload = Depends(auth_with_jwt),
    db: Session = Depends(get_db),
) -> DeleteUserResponse:
    """
    Hard delete a user with the provided user id<br>
    Only an admin can delete a user.<br>
    - **user_id**: user_id of the deleting user
    """
    # user must be an admin
    if jwt_data.role == Role.ADMIN:
        if jwt_data.sub == request.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete self"
            )
        is_deleted = UserRepository(db).delete_user(request.user_id)
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return DeleteUserResponse(user_id=request.user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the action",
        )
