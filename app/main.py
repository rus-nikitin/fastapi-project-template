import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

from api import api_router
from core.config.settings import settings
from core.middleware import MetricsMiddleware, RequestIdMiddleware, DbMiddlewareFactory
from infrastructure.database.managers import DbManagerFactory


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(message)s]",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs.log")
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with database state"""
    logger.info("Application starting up...")

    db_manager = DbManagerFactory.create_manager(**settings.model_dump())
    app.state.db_manager = db_manager

    await db_manager.connect()

    try:
        # Optional: Create tables if they don't exist
        pass
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        # Don't fail startup - tables might already exist

    yield

    # Shutdown
    logger.info("Application shutting down...")
    await db_manager.disconnect()


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Minimal HTTP exception handler - MetricsMiddleware already logged the details."""
    request_id = getattr(request.state, 'request_id', 'unknown')

    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Minimal general exception handler - MetricsMiddleware already logged the details."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )
    response.headers["X-Request-ID"] = request_id
    return response


# # Add the middleware
DbMiddleware = DbMiddlewareFactory.get_middleware(**settings.model_dump())
app.add_middleware(DbMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)
