import os
import time
import logging

from fastapi import HTTPException
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config.settings import settings

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Enhanced metrics middleware with comprehensive request logging and exception catching."""

    async def dispatch(self, request: Request, call_next):
        if not settings.metrics_enabled:
            return await call_next(request)

        start_time = time.perf_counter()
        request_id = getattr(request.state, 'request_id', 'unknown')
        process_id = os.getpid()

        # Collect request info
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request) if settings.metrics_include_client_ip else None
        user_agent = self._get_user_agent(request) if settings.metrics_include_user_agent else None

        try:
            # Process request
            response = await call_next(request)

            # Calculate timing
            duration_ms = (time.perf_counter() - start_time) * 1000
            status_code = response.status_code

            # Log successful response
            self._log_request(
                request_id, process_id, method, path, status_code, duration_ms,
                client_ip, user_agent, exception=None
            )

            return response

        except HTTPException as http_exc:
            # Calculate timing for HTTP exceptions
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log HTTP exception with metrics
            self._log_request(
                request_id, process_id, method, path, http_exc.status_code, duration_ms,
                client_ip, user_agent, exception=http_exc
            )

            # Re-raise to let exception handlers format the response
            raise

        except Exception as exc:
            # Calculate timing for server errors
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log server exception with metrics
            self._log_request(
                request_id, process_id, method, path, 500, duration_ms,
                client_ip, user_agent, exception=exc
            )

            # Re-raise to let exception handlers format the response
            raise

    def _log_request(
        self,
        request_id: str,
        process_id: int,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str | None = None,
        user_agent: str | None = None,
        exception: Exception | None = None
    ) -> None:
        """Unified request logging with appropriate log levels."""

        # Determine log level based on status code and exception
        log_level = self._get_log_level(status_code, exception)

        # Build comprehensive log message
        log_message = self._build_log_message(
            request_id, process_id, method, path, status_code, duration_ms,
            client_ip, user_agent, exception
        )

        # Log with appropriate level
        logger.log(log_level, log_message)

        # Additional logging for slow requests (non-exceptions only)
        if (not exception and
            settings.metrics_log_slow_requests and
            duration_ms > settings.metrics_slow_threshold_ms):
            self._log_slow_request(request_id, process_id, method, path, duration_ms, client_ip)

    def _get_log_level(self, status_code: int, exception: Exception | None = None) -> int:
        """Determine appropriate log level based on status code and exception type."""
        if exception:
            if isinstance(exception, HTTPException):
                # HTTP exceptions: WARNING for 4xx, ERROR for 5xx
                return logging.ERROR if status_code >= 500 else logging.WARNING
            else:
                # Server exceptions: always ERROR
                return logging.ERROR
        else:
            # Normal responses: ERROR for 5xx, WARNING for 4xx, INFO for 2xx/3xx
            if status_code >= 500:
                return logging.ERROR
            elif status_code >= 400:
                return logging.WARNING
            else:
                return logging.INFO

    def _build_log_message(
        self,
        request_id: str,
        process_id: int,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        client_ip: str | None = None,
        user_agent: str | None = None,
        exception: Exception | None = None
    ) -> str:
        """Build comprehensive log message with exception details."""

        # Base message with PID
        if exception:
            exc_type = type(exception).__name__
            exc_msg = str(exception)[:100]  # Truncate long exception messages
            message = f"[{request_id}] [pid:{process_id}] {method} {path} - {status_code} - {duration_ms:.0f}ms - {exc_type}: {exc_msg}"
        else:
            message = f"[{request_id}] [pid:{process_id}] {method} {path} - {status_code} - {duration_ms:.0f}ms"

        # Add optional info
        extras = []
        if client_ip:
            extras.append(f"ip:{client_ip}")
        if user_agent:
            # Truncate long user agents
            truncated_ua = user_agent[:50] + "..." if len(user_agent) > 50 else user_agent
            extras.append(f"ua:'{truncated_ua}'")

        if extras:
            message += f" - {' '.join(extras)}"

        return message

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, handling proxies."""
        # Check for forwarded headers first (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"

    def _get_user_agent(self, request: Request) -> str:
        """Extract User-Agent header."""
        return request.headers.get("User-Agent", "unknown")

    def _log_slow_request(
        self,
        request_id: str,
        process_id: int,
        method: str,
        path: str,
        duration_ms: float,
        client_ip: str | None = None
    ) -> None:
        """Log slow requests with WARNING level for easy filtering."""
        slow_message = f"[{request_id}] [pid:{process_id}] SLOW REQUEST: {method} {path} took {duration_ms:.0f}ms"
        if client_ip:
            slow_message += f" from {client_ip}"

        logger.warning(slow_message)
