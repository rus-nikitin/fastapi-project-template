from fastapi import APIRouter

from src.core.dependencies import RequestId
from src.domains.distance.schemas import Point, DistanceResponse
from src.core.dependencies import JwtClientDep


router = APIRouter()


@router.post("", response_model=DistanceResponse, status_code=200)
async def calculate_distance(
    point_a: Point,
    point_b: Point,
    jwt_client: JwtClientDep,
    request_id: RequestId
):
    # some complex business logic for jwt authenticated users only
    distance=((point_a.x-point_b.x)**2+(point_a.y-point_b.y)**2)**0.5
    return DistanceResponse(distance=distance)
