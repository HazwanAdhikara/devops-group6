from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client.gc_collector import GCCollector
from prometheus_client.platform_collector import PlatformCollector
from prometheus_client.process_collector import ProcessCollector


registry = CollectorRegistry()

ProcessCollector(registry=registry)
PlatformCollector(registry=registry)
GCCollector(registry=registry)

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    labelnames=["method", "route", "status_code"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["method", "route", "status_code"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1, 2, 5],
    registry=registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of requests currently being processed",
    labelnames=["method", "route"],
    registry=registry,
)

__all__ = [
    "registry",
    "http_requests_total",
    "http_request_duration_seconds",
    "http_requests_in_progress",
]
