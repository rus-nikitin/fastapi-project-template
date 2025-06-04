import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        logger.info(f"[{request_id}] Processing request: {request.method} {request.url}")

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        logger.info(f"[{request_id}] Request completed with status: {response.status_code}")
        return response
