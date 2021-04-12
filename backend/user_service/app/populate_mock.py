from db.database import DBSession
from tests.mock_factories import UserFactory

mock_users = UserFactory.build_batch(100)

db = DBSession()
db.add_all(mock_users)
db.commit()
db.close()
