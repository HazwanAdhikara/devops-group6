import os
import time

from fastapi import FastAPI, Request, Response
from prometheus_client import make_asgi_app

from src.metrics import (
    http_request_duration_seconds,
    http_requests_in_progress,
    http_requests_total,
    registry,
)
from src.routes.health import router as health_router
from src.routes.products import router as products_router
from src.routes.users import router as users_router


APP_START_TIME = time.time()
PORT = int(os.getenv("PORT", "3000"))

app = FastAPI(title="Observability Demo API")
app.state.start_time = APP_START_TIME

metrics_app = make_asgi_app(registry=registry)
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next) -> Response:
    method = request.method
    route = request.url.path

    http_requests_in_progress.labels(method=method, route=route).inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        duration = time.time() - start_time

        http_requests_total.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).inc()
        http_request_duration_seconds.labels(
            method=method,
            route=route,
            status_code=status_code,
        ).observe(duration)

        return response
    finally:
        http_requests_in_progress.labels(method=method, route=route).dec()


app.include_router(users_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(health_router)
