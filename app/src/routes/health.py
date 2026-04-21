import time

from fastapi import APIRouter


router = APIRouter()
APP_START_TIME = time.time()


@router.get("/health", status_code=200)
async def health_check() -> dict[str, float | str]:
    return {
        "status": "ok",
        "uptime": round(time.time() - APP_START_TIME, 2),
    }
