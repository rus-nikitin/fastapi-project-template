from pydantic import BaseModel


class Point(BaseModel):
    x: float
    y: float


class DistanceResponse(BaseModel):
    distance: float
