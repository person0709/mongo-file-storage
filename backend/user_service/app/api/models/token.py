from pydantic import BaseModel


class Token(BaseModel):
    """
    A model to represent a token used for authorization/authentication
    """
    token_type: str
    access_token: str
