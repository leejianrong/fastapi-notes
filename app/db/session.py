from sqlalchemy.engine import Engine
from sqlmodel import create_engine

from app.core.config import settings

def _make_engine(database_url: str) -> Engine:
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False}, # needed for SQLite in threads
            echo=False,
        )
    return create_engine(database_url, echo=False)

engine = _make_engine(settings.database_url)