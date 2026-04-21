# FastAPI Application

This folder contains the application node used in the observability mini project. The service is built with FastAPI and exposes business endpoints plus Prometheus metrics for monitoring and load testing.

## Purpose

The application acts as the traffic target for k6 and the metrics source for Prometheus. It provides simple mock data endpoints so the monitoring stack can observe request patterns, response latency, and request volume.

## Tech Stack

- Python 3.11
- FastAPI 0.111.0
- Uvicorn 0.30.1
- prometheus-client 0.20.0
- Docker

## Available Endpoints

- `GET /health` returns app status and uptime
- `GET /metrics` returns Prometheus metrics in text format
- `GET /api/users` returns 10 mock users
- `POST /api/users` creates a new user in memory
- `GET /api/products` returns 5 mock products
- `GET /api/products/{id}` returns a product by ID or `404`

## What `/metrics` Does

The `/metrics` endpoint exposes internal application metrics in Prometheus text format. Prometheus scrapes this endpoint on a schedule and stores the results for monitoring, alerting, and dashboard visualization.

In this project, `/metrics` publishes:

- `http_requests_total` to count total HTTP requests,
- `http_request_duration_seconds` to measure request latency,
- `http_requests_in_progress` to track active in-flight requests.

These metrics allow the monitoring stack to answer questions such as:

- how many requests the app is receiving,
- how long each route takes to respond,
- whether the application is under heavy load,
- whether performance changes after k6 load testing.

## Local Development

Install dependencies and run the app directly:

```bash
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 3000
```

## Docker Run

The simplest way to run the app is from the repository root using the helper script:

```bash
./run.sh
```

If you want to run it manually instead, use:

```bash
cd app
docker build -t observability-app .
docker run --rm -p 3000:3000 observability-app
```

## Docker Image Details

The Dockerfile uses:

- base image: `python:3.11-slim`
- non-root runtime user: `appuser`
- health check: `GET /health`
- exposed port: `3000`

## Verification Checklist

After the app is running, verify these URLs:

- `http://localhost:3000/health`
- `http://localhost:3000/api/users`
- `http://localhost:3000/api/products`
- `http://localhost:3000/metrics`
