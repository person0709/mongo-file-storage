from pathlib import Path
from typing import Generator

import pytest
from starlette.testclient import TestClient

from api.models.role import Role
from db.database import get_db
from db.models.base import Base
from main import app
from tests.db.test_database import override_get_db, TestSession, engine
from tests.mock_factories import UserFactory
from utils.token import generate_jwt


@pytest.fixture(scope="function")
def test_db(cleanup_db) -> Generator:
    Base.metadata.create_all(engine)
    yield TestSession()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="module")
def cleanup_db() -> None:
    yield
    for f in Path("./").glob("*.db"):
        f.unlink()


@pytest.fixture(scope="module")
def test_client() -> Generator:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def admin_token_header() -> Generator:
    admin = UserFactory(role=Role.ADMIN)
    yield {"Authorization": f"Bearer {generate_jwt(admin).access_token}"}


@pytest.fixture(scope="session")
def non_admin_token_header() -> Generator:
    user = UserFactory(role=Role.VIEWER)
    yield {"Authorization": f"Bearer {generate_jwt(user).access_token}"}
