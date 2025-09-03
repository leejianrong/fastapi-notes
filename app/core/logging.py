import json
import logging
from logging.config import dictConfig
from datetime import datetime, timezone
from contextvars import ContextVar
import os

# Context var we can read inside the formatter
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

LOG_FILE = os.getenv("APP_LOG_FILE", "/var/log/app/app.jsonl")

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Base payload
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Attach common extras if present
        # (we use .__dict__ to avoid consuming record.args)
        for key in ("method", "path", "status", "duration_ms", "client_ip", "user_agent", 
                    "service", "env", "note_id", "changed_fields", "route", "count", 
                    "offset", "limit", "title"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        # Request ID from context
        rid = request_id_var.get()
        if rid:
            payload["request_id"] = rid
        return json.dumps(payload, ensure_ascii=False)

def setup_logging(level: str = "INFO"):
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"()": JSONFormatter},
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            },
            # write to a file Alloy can tail
            "file": {
                "class": "logging.handlers.WatchedFileHandler",
                "filename": LOG_FILE,
                "formatter": "json",
            },
        },
        "root": {
            "level": level,
            "handlers": ["stdout", "file"], # write to both; remove "stdout" if you want file-only
        },
        # Optional: tune noisy third-party loggers
        "loggers": {
            "uvicorn.error": {"level": "INFO", "handlers": ["stdout", "file"], "propagate": False},
            "uvicorn.access": {"level": "WARNING", "handlers": ["stdout", "file"], "propagate": False},  # we'll log access ourselves
            "sqlalchemy.engine.Engine": {"level": "WARNING"},
        },
    })
