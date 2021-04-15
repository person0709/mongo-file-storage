from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from jose import jwt

from api.models.jwt_payload import JWTPayload
from config import settings
from db.models.base import Base
from starlette.testclient import TestClient
from tests.db.test_database import override_get_db, TestSession, engine

from api.models.role import Role
from db.database import get_db
from main import app


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
def admin_token_header() -> str:
    payload = JWTPayload(
        sub="admin_id",
        role=Role.ADMIN,
        exp=datetime(2077, 1, 1),
        username="marko",
        email="hello@world.com",
    )
    yield {
        "Authorization": f"Bearer {jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)}"
    }


@pytest.fixture(scope="session")
def non_admin_token_header() -> Generator:
    payload = JWTPayload(
        sub="uploader_id",
        role=Role.UPLOADER,
        exp=datetime(2077, 1, 1),
        username="pollo",
        email="hola@world.com",
    )
    yield {
        "Authorization": f"Bearer {jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)}"
    }
