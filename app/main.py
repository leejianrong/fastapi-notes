from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.health import router as health_router
from app.api.notes import router as notes_router
from app.db.session import engine

from app.core.logging import setup_logging
setup_logging(level="INFO")

from app.middlewares.request_logging import RequestContextLogMiddleware

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Register middleware early
app.add_middleware(RequestContextLogMiddleware)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # check the logs work on startup
    import logging
    logging.getLogger("app").info("startup_complete")
    # startup code to create tables if they don't exist
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(
    title=settings.app_name, 
    debug=settings.debug, 
    lifespan=lifespan
)

# routers
app.include_router(health_router)
app.include_router(notes_router)

@app.get("/")
def root():
    return {"message": "Hello, FastAPI Notes!"}