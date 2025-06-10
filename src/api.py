from fastapi import APIRouter

from src.domains.user import user_router
from src.domains.distance import distance_router

api_router = APIRouter()


api_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"]
)

from uuid import int_

api_router.include_router(
    distance_router,
    prefix="/distance",
    tags=["distance"]
)

@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    """Simple healthcheck endpoint."""
    return {"status": "ok"}


from src.core.dependencies import JwtClient, JwtClientDep, AdminJwtClientDep
@api_router.get("/jwt-client", response_model=JwtClient)
def jwt_client(jwt_client: JwtClientDep):
    """Simple jwt endpoint."""
    return jwt_client


@api_router.get("/admin-client", response_model=JwtClient)
def admin_client(jwt_client: AdminJwtClientDep):
    """Simple jwt endpoint."""
    return jwt_client


import asyncio
from concurrent.futures import ProcessPoolExecutor
import os
import time
from pydantic import BaseModel


class Sleep(BaseModel):
    value: int


def cpu_task(sleep: Sleep):
    """Функция, которая будет выполняться в отдельном процессе"""
    current_pid = os.getpid()
    print(f"Executing in process PID: {current_pid}")

    # CPU-intensive задача
    time.sleep(sleep.value)
    return sleep

@api_router.get("/cpu-bound")
async def cpu_bound(sleep: int):
    """Simple cpu-bound endpoint."""

    loop = asyncio.get_event_loop()

    # Создаем пул из 4 процессов
    with ProcessPoolExecutor(max_workers=2) as executor:
        # Запускаем задачи в разных процессах
        tasks = [
            loop.run_in_executor(executor, cpu_task, Sleep(value=sleep)),
            loop.run_in_executor(executor, cpu_task, Sleep(value=sleep)),
            loop.run_in_executor(executor, cpu_task, Sleep(value=sleep)),
            loop.run_in_executor(executor, cpu_task, Sleep(value=sleep)),
        ]
        results = await asyncio.gather(*tasks)
        print(f"Results: {results}")

    # time.sleep(sleep)
    return {"sleep": sleep}
