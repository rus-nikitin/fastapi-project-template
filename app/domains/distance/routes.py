from fastapi import APIRouter

from core.dependencies import RequestId
from .schemas import Point, DistanceResponse
from domains.user import CurrentUserDep


router = APIRouter()


@router.post("", response_model=DistanceResponse, status_code=200)
async def calculate_distance(
    point_a: Point,
    point_b: Point,
    current_user: CurrentUserDep,
    request_id: RequestId
):
    # some complex business logic for authenticated users only
    distance=((point_a.x-point_b.x)**2+(point_a.y-point_b.y)**2)**0.5
    return DistanceResponse(distance=distance)
