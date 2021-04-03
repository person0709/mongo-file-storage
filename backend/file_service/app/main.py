from fastapi import FastAPI

from api.router import api_router
from db.database import open_db_connection, close_db_connection

app = FastAPI(title="File Service API")
app.add_event_handler("startup", open_db_connection)
app.add_event_handler("shutdown", close_db_connection)
app.include_router(api_router, prefix="/api")
