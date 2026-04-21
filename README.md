# Mini Project Study Case 4 - DevOps

This mini project builds an observability stack to validate service performance and stability before launch. The main focus is to provide a target application that exposes metrics, then connect it to monitoring and load-testing components that other team members can use.

## Purpose

The goal of this project is to provide an end-to-end workflow for:

- running a FastAPI application as the traffic target and metrics source,
- exposing Prometheus metrics from the application,
- preparing a monitoring stack such as Prometheus and Grafana,
- running k6 load tests to evaluate latency and error rate,
- supporting a clean handoff between project roles in the DevOps team.

## Tech Stack

- Python 3.11
- FastAPI
- prometheus-client
- Uvicorn
- Docker

## Scope in This Repository

This repository currently contains the application node owned by Person 1:

- FastAPI source code in [app/src](app/src),
- Prometheus metrics in [app/src/metrics.py](app/src/metrics.py),
- application routes in [app/src/routes](app/src/routes),
- the Dockerfile used to build the application image in [app/Dockerfile](app/Dockerfile),
- the helper script used to run the container in [run.sh](run.sh).

Other components such as Terraform, Ansible, Prometheus, Grafana, and k6 will be handled by other personas in the project.

## Application Endpoints

- `GET /health` - application status and uptime
- `GET /metrics` - Prometheus metrics in text format
- `GET /api/users` - mock user list
- `POST /api/users` - create a new user
- `GET /api/products` - mock product list
- `POST /api/products` - create a new product
- `GET /api/products/{id}` - product details by ID

## Run With Docker

From the repository root, use the helper script:

```bash
./run.sh
```

The script will:

1. move into the `app/` folder,
2. build the Docker image named `observability-app`,
3. run the container and expose port `3000`.

## Manual Docker Run

If you prefer to run the commands manually:

```bash
cd app
docker build -t observability-app .
docker run --rm -p 3000:3000 -v "$(pwd)/data:/app/data" observability-app
```

The mounted volume keeps CSV data in `app/data` persistent on the host even after the container is stopped.

## Verify the App

After the container is running, test these URLs:

- `http://localhost:3000/health`
- `http://localhost:3000/api/users`
- `http://localhost:3000/api/products`
- `http://localhost:3000/metrics`

## Run Monitoring Stack (Docker Compose)

To run the application alongside Prometheus and Grafana in a unified network:

```
cd docker-compose
docker compose up -d
```

Once running, you can access the services here:

- `Target Application: http://localhost:3000/health`
- `Prometheus UI: http://localhost:9090`
- `Grafana UI: http://localhost:3001 (Default login: - - admin / admin)`

## Run Load Testing (K6)

```
cd k6
k6 run --out json=results.json load-test.js
```

Note: The script tests 1000 VUs for 5 minutes and tracks custom latency to trigger monitoring alerts.

## Repository Layout

```text
.
├── README.md
├── run.sh
├──  app/
	├── Dockerfile
	├── README.md
	├── requirements.txt
	└── src/
		├── main.py
		├── metrics.py
		└── routes/
			├── health.py
			├── products.py
			└── users.py
└── terraform
	├── main.tf
	├── variables.tf
	├── outputs.tf
	└── terraform.tfvars

├── docker-compose/
│   └── docker-compose.yml
├── k6/
│   ├── load-test.js
│   └── results.json

```
