from typing import Annotated
import logging

from fastapi import Depends
from starlette.requests import Request

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    return getattr(request.state, 'request_id', 'unknown')


RequestId = Annotated[str, Depends(get_request_id)]
