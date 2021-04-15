import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 60 * 24

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./user_db.db"
    ADMIN_USER_EMAIL: str = "overwhelming@power.com"
    ADMIN_USER_USERNAME: str = "chuck-norris"
    ADMIN_USER_PASSWORD: str = "youshallnotpass"


settings = Settings()
