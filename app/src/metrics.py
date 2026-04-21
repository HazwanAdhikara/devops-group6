from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client.gc_collector import GCCollector
from prometheus_client.platform_collector import PlatformCollector
from prometheus_client.process_collector import ProcessCollector


HISTOGRAM_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1, 2, 5)


def create_registry() -> CollectorRegistry:
    registry = CollectorRegistry()
    ProcessCollector(registry=registry)
    PlatformCollector(registry=registry)
    GCCollector(registry=registry)
    return registry


registry = create_registry()

http_requests_total = Counter(
    name="http_requests_total",
    documentation="Total number of HTTP requests",
    labelnames=("method", "route", "status_code"),
    registry=registry,
)

http_request_duration_seconds = Histogram(
    name="http_request_duration_seconds",
    documentation="HTTP request duration in seconds",
    labelnames=("method", "route", "status_code"),
    buckets=HISTOGRAM_BUCKETS,
    registry=registry,
)

http_requests_in_progress = Gauge(
    name="http_requests_in_progress",
    documentation="Number of requests currently being processed",
    labelnames=("method", "route"),
    registry=registry,
)

__all__ = [
    "registry",
    "HISTOGRAM_BUCKETS",
    "http_requests_total",
    "http_request_duration_seconds",
    "http_requests_in_progress",
]
