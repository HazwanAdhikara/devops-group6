import time

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["Health"])
APP_START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str
    uptime: float


@router.get("/health", status_code=200)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", uptime=round(time.time() - APP_START_TIME, 2))
