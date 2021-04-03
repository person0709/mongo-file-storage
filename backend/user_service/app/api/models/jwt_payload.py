from datetime import datetime

from pydantic import BaseModel, EmailStr

from api.models.role import Role


class JWTPayload(BaseModel):
    """
    A model to represent the JWT claims used in the API
    """
    sub: str  # subject's user_id
    exp: datetime  # JWT expiration date
    role: Role  # subject's permission level
    username: str  # subject's username
    email: EmailStr  # subject's email
