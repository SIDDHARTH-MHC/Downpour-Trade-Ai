from __future__ import annotations

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("downpour.api")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        try:
            response = await call_next(request)
            logger.info(
                '{"request_id":"%s","method":"%s","path":"%s","status":%s}',
                request_id,
                request.method,
                request.url.path,
                response.status_code,
            )
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:  # noqa: BLE001
            logger.exception("unhandled error request_id=%s", request_id)
            return JSONResponse(
                status_code=500,
                content={"error": str(exc), "request_id": request_id},
            )
