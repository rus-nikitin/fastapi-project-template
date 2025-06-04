from typing import Annotated, TYPE_CHECKING
import logging

from fastapi import Depends
from starlette.requests import Request

from infrastructure.database.managers import BaseDbManager

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


def get_db_manager_from_app(app) -> BaseDbManager:
    """Get database manager from FastAPI app state"""
    if not hasattr(app.state, 'db_manager'):
        raise RuntimeError("Database manager not found in app state")
    return app.state.db_manager


def get_db_provider(request: Request)-> 'AsyncSession | AsyncIOMotorDatabase | None':
    """
    Dependency injection function that provides database provider.
    Cleanup is managed by middleware.
    """
    db_provider = getattr(request.state, 'db_provider', None)

    if db_provider is None:
        db_manager = get_db_manager_from_app(request.app)
        db_provider = db_manager.get_db_provider()
        request.state.db_provider = db_provider

        request_id = getattr(request.state, 'request_id', 'unknown')
        logger.info(f"[{request_id}] {db_manager.get_provider_type()} id:{id(db_provider)} provider set in request.state.db_provider")

    return db_provider


DbProvider = Annotated['AsyncSession | AsyncIOMotorDatabase', Depends(get_db_provider)]
