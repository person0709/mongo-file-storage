from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_hash(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_hash(password: str) -> str:
    return pwd_context.hash(password)
