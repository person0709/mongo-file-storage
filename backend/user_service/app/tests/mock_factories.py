import factory
from db.models.user import User

from api.models.role import Role


class UserFactory(factory.Factory):
    class Meta:
        model = User

    user_id = factory.Faker("uuid4")
    username = factory.Faker("user_name")
    email = factory.Faker("email")
    hashed_password = factory.Faker("password")
    joined_at = factory.Faker("date_time_this_decade")
    role = factory.Faker("random_element", elements=(Role.VIEWER, Role.UPLOADER, Role.ADMIN))
