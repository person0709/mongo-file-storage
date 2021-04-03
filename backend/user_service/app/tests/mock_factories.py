import factory

from api.models.role import Role
from db.models.user import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    user_id = factory.Faker("uuid4")
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    hashed_password = factory.Faker("password")
    role = Role.VIEWER
    del_flag = 0
