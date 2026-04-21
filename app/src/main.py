import time

from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
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

app.mount(METRICS_PATH, make_asgi_app(registry=registry))


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


for router, prefix in ROUTERS:
    app.include_router(router, prefix=prefix)
