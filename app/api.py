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


from core.dependencies import JwtClient, JwtClientDep, AdminJwtClientDep
@api_router.get("/jwt-client", response_model=JwtClient)
def jwt_client(jwt_client: JwtClientDep):
    """Simple jwt endpoint."""
    return jwt_client


@api_router.get("/admin-client", response_model=JwtClient)
def admin_client(jwt_client: AdminJwtClientDep):
    """Simple jwt endpoint."""
    return jwt_client
