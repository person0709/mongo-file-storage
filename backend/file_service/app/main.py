import logging
from datetime import datetime

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.models.jwt_payload import JWTPayload
from api.models.role import Role
from api.router import api_router
from config import settings
from db.database import open_db_connection, close_db_connection
from utils.token import auth_with_jwt

app = FastAPI(
    title="File Service API",
    openapi_url="/api/files/openapi.json",
    docs_url="/api/files/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://fs-service.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", open_db_connection)
app.add_event_handler("shutdown", close_db_connection)
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def logger_setup():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s", level=logging.INFO
    )
    uvi_logger = logging.getLogger("uvicorn.access")
    if len(uvi_logger.handlers):
        uvi_logger.handlers[0].setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))


# This will allow all endpoints to be called without Authorization headers. Use this only for testing.
if settings.NO_AUTH_MODE:
    app.dependency_overrides[auth_with_jwt] = lambda: JWTPayload(
        sub="super_user_id",
        exp=datetime.now(),
        role=Role.ADMIN,
        username="superuser",
        email="superuser@email.com",
    )
