from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.router import api_router

app = FastAPI(
    title="User Service API",
    openapi_url="/api/users/openapi.json",
    docs_url="/api/users/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://fs-service.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
