import secrets
from typing import Set

from pydantic import BaseSettings

from api.models.role import Role


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str = "HS256"
    MONGODB_URL: str = "mongodb://localhost:27017"

    ROLE_FOR_VIEW: Set[Role] = {Role.VIEWER, Role.UPLOADER, Role.ADMIN}
    ROLE_FOR_DOWNLOAD: Set[Role] = {Role.UPLOADER, Role.ADMIN}
    ROLE_FOR_UPLOAD: Set[Role] = {Role.UPLOADER, Role.ADMIN}
    ROLE_FOR_DELETE: Set[Role] = {Role.UPLOADER, Role.ADMIN}

    FILE_SIZE_LIMIT: int = 500_000_000  # 500MB by default
    FILE_EXTENSION_WHITELIST: Set[str] = {
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".xls",
        ".xlsx",
        ".txt",
        ".csv",
    }

    NO_AUTH_MODE: bool = False


settings = Settings()
