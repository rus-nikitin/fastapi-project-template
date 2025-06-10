import logging
from abc import ABC, abstractmethod
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


def _is_success_response(response: Response) -> bool:
    """Check if response indicates success (2xx status codes)."""
    return response.status_code // 200 == 1


class BaseDbMiddleware(BaseHTTPMiddleware, ABC):
    """
    Base middleware for database session management.
    Handles common logic while allowing database-specific implementations.
    """

    async def dispatch(self, request: Request, call_next):
        request.state.db_provider = None
        request_id = getattr(request.state, 'request_id', 'unknown')

        try:
            # Process the request
            response = await call_next(request)

            # Handle successful response
            db_provider = request.state.db_provider
            if db_provider is not None:
                await self._handle_success(db_provider, response, request_id)

            return response

        except Exception as e:
            # Handle exceptions
            db_provider = request.state.db_provider
            if db_provider is not None:
                await self._handle_error(db_provider, e, request_id)
            raise

        finally:
            # Always cleanup
            db_provider = request.state.db_provider
            if db_provider is not None:
                await self._cleanup(db_provider, request_id)
            request.state.db_provider = None

    @abstractmethod
    async def _handle_success(self, db_provider, response: Response, request_id: str):
        """Handle successful response - commit or log success"""
        pass

    @abstractmethod
    async def _handle_error(self, db_provider, error: Exception, request_id: str):
        """Handle error response - rollback or log error"""
        pass

    @abstractmethod
    async def _cleanup(self, db_provider, request_id: str):
        """Cleanup resources - close sessions or connections"""
        pass


class SQLAlchemyDbMiddleware(BaseDbMiddleware):
    """SQLAlchemy-specific database middleware with transaction management"""

    async def _handle_success(self, db_provider, response: Response, request_id: str):
        try:
            if _is_success_response(response):
                await db_provider.commit()
                logger.info(f"[{request_id}] SQL transaction committed")
            else:
                await db_provider.rollback()
                logger.warning(f"[{request_id}] SQL transaction rolled back (status: {response.status_code})")
        except Exception as e:
            logger.error(f"[{request_id}] Error during SQL transaction handling: {e}")
            await db_provider.rollback()

    async def _handle_error(self, db_provider, error: Exception, request_id: str):
        try:
            await db_provider.rollback()
            logger.error(f"[{request_id}] SQL transaction rolled back due to exception: {error}")
        except Exception as rollback_error:
            logger.error(f"[{request_id}] Error during SQL rollback: {rollback_error}")

    async def _cleanup(self, db_provider, request_id: str):
        try:
            await db_provider.close()
            logger.debug(f"[{request_id}] SQL session closed")
        except Exception as e:
            logger.error(f"[{request_id}] Error closing SQL session: {e}")


class MotorDbMiddleware(BaseDbMiddleware):
    """MongoDB-specific database middleware"""

    async def _handle_success(self, db_provider, response: Response, request_id: str):
        if _is_success_response(response):
            logger.debug(f"[{request_id}] MongoDB operation completed successfully")
        else:
            logger.warning(f"[{request_id}] MongoDB operation completed with error status: {response.status_code}")

    async def _handle_error(self, db_provider, error: Exception, request_id: str):
        logger.error(f"[{request_id}] MongoDB operation failed: {error}")

    async def _cleanup(self, db_provider, request_id: str):
        # MongoDB connections are managed by the motor client, no explicit cleanup needed
        logger.debug(f"[{request_id}] MongoDB operation cleanup completed")


class NoOpDbMiddleware(BaseHTTPMiddleware):
    """No-operation middleware when no database is needed"""

    async def dispatch(self, request: Request, call_next):
        # Simply pass through without any database handling
        return await call_next(request)


class DbMiddlewareFactory:
    _managers = {
        "sqlalchemy": SQLAlchemyDbMiddleware,
        "motor": MotorDbMiddleware,
        "none": NoOpDbMiddleware
    }

    @classmethod
    def get_middleware(cls, **config):
        db_type = config.get("db_type")

        # If no database manager specified, use no-op middleware
        if db_type is None:
            logger.info("No database manager specified, using no-op middleware")
            return cls._managers["none"]

        if db_type not in cls._managers:
            available = ", ".join(cls._managers.keys())
            raise ValueError(f"Unknown database manager: {db_type}. Available: {available}")

        logger.info(f"Using database middleware: {db_type}")
        return cls._managers[db_type]
