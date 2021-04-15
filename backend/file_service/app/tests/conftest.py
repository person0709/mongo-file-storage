from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from jose import jwt

from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from config import settings
from db.database import get_db
from main import app
from tests.db.mock_database import MockDatabase


@pytest.fixture(scope="function")
async def test_client(event_loop):
    app.dependency_overrides[get_db] = lambda: MockDatabase(event_loop)
    async with AsyncClient(
        app=app, base_url="http://localhost"
    ) as client, LifespanManager(app):
        yield client


@pytest.fixture(scope="function")
async def test_db(event_loop) -> MockDatabase:
    db = MockDatabase(event_loop)
    await db.create_index()
    yield db
    await db.client.drop_database("file_service")


@pytest.fixture(scope="session")
def text_file() -> Path:
    current_dir = Path(__file__).parent
    return current_dir / "resources" / "text.txt"


@pytest.fixture(scope="session")
def audio_file() -> Path:
    current_dir = Path(__file__).parent
    return current_dir / "resources" / "meow.wav"


@pytest.fixture(scope="session")
def image_file() -> Path:
    current_dir = Path(__file__).parent
    return current_dir / "resources" / "doge.jpg"


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
def uploader_token_header() -> Generator:
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


@pytest.fixture(scope="session")
def viewer_token_header() -> Generator:
    payload = JWTPayload(
        sub="viewer_id",
        role=Role.VIEWER,
        exp=datetime(2077, 1, 1),
        username="guy",
        email="halla@world.com",
    )
    yield {
        "Authorization": f"Bearer {jwt.encode(payload.dict(), key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)}"
    }
