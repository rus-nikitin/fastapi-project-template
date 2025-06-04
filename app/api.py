from fastapi import APIRouter

from domains.user import user_router
from domains.distance import distance_router

api_router = APIRouter()


api_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"]
)


api_router.include_router(
    distance_router,
    prefix="/distance",
    tags=["distance"]
)

@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    """Simple healthcheck endpoint."""
    return {"status": "ok"}
