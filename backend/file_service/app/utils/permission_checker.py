"""
Dependencies that will be used for checking permission of a user for each action.
They will use JWT claims to check permission.
"""
from fastapi import Depends, HTTPException
from starlette import status

from api.models.jwt_payload import JWTPayload
from config import settings
from utils.token import auth_with_jwt


def check_view_permission(jwt_data: JWTPayload = Depends(auth_with_jwt)):
    if jwt_data.role not in settings.ROLE_FOR_VIEW:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission"
        )
    return jwt_data


def check_upload_permission(jwt_data: JWTPayload = Depends(auth_with_jwt)):
    if jwt_data.role not in settings.ROLE_FOR_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission"
        )
    return jwt_data


def check_download_permission(jwt_data: JWTPayload = Depends(auth_with_jwt)):
    if jwt_data.role not in settings.ROLE_FOR_DOWNLOAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission"
        )
    return jwt_data


def check_delete_permission(jwt_data: JWTPayload = Depends(auth_with_jwt)):
    if jwt_data.role not in settings.ROLE_FOR_DELETE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission"
        )
    return jwt_data
