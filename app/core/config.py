import os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name : str = "Notes API"
    debug: bool = True
    # local default: SQLite file; can switch to Postgres later
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

settings = Settings()