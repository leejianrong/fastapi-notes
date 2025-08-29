import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import request_id_var

access_logger = logging.getLogger("access")  # uses root handler/formatter

class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Use incoming header or generate a new ID
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex
        token = request_id_var.set(rid)

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        finally:
            # Always reset the context var to avoid leaking across requests
            request_id_var.reset(token)

        # Propagate the ID back to the client
        response.headers["X-Request-ID"] = rid

        # Structured access log
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        client_ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")

        # Use extra= to pass structured fields to the JSON formatter
        access_logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "user_agent": ua,
                "service": "notes-api",
            },
        )
        return response
