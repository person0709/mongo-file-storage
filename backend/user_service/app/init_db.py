"""
Create initial admin user to database when it starts up
"""
from api.models.role import Role
from config import settings
from db.database import DBSession
from db.models.user import User
from utils.password import get_hash

super_user = User(
    username=settings.ADMIN_USER_USERNAME,
    email=settings.ADMIN_USER_EMAIL,
    hashed_password=get_hash(settings.ADMIN_USER_PASSWORD),
    role=Role.ADMIN,
)

db = DBSession()
db.add(super_user)
db.commit()
db.close()
