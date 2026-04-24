import time

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
# [LAMA - dinonaktifkan] make_asgi_app sebelumnya digunakan untuk mount /metrics, tetapi endpoint /metrics menjadi tidak stabil.
# from prometheus_client import make_asgi_app

# [BARU] generate_latest digunakan untuk membuat endpoint /metrics secara eksplisit.
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

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
APP_TITLE = "Observability Demo API"
METRICS_PATH = "/metrics"
API_PREFIX = "/api"
ROUTERS = (
    (users_router, API_PREFIX),
    (products_router, API_PREFIX),
    (health_router, ""),
)

app = FastAPI(title=APP_TITLE)
app.state.start_time = APP_START_TIME

# [LAMA - dinonaktifkan] Mounted ASGI metrics endpoint tidak stabil pada deployment saat ini.
# app.mount(METRICS_PATH, make_asgi_app(registry=registry))


# [BARU] Endpoint /metrics eksplisit untuk Prometheus.
@app.get(METRICS_PATH, include_in_schema=False)
async def prometheus_metrics() -> Response:
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    missing_fields: list[str] = []
    details: list[dict[str, object]] = []

    for error in exc.errors():
        location = [str(part) for part in error.get("loc", ())]
        details.append(
            {
                "field": ".".join(location),
                "message": str(error.get("msg", "Invalid value")),
            }
        )
        if error.get("type") == "missing" and len(location) >= 2 and location[0] == "body":
            missing_fields.append(location[1])

    response_body: dict[str, object] = {
        "message": "Invalid request body",
        "errors": details,
    }
    if missing_fields:
        response_body["required_fields"] = sorted(set(missing_fields))

    return JSONResponse(status_code=422, content=response_body)


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

# [BARU] Endpoint khusus testing error rate untuk observability/k6.
@app.get("/api/error")
async def test_error() -> Response:
    return Response(
        content='{"message":"intentional error for testing"}',
        status_code=500,
        media_type="application/json",
    )

for router, prefix in ROUTERS:
    app.include_router(router, prefix=prefix)
