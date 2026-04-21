# FastAPI Application

This folder contains the application node for the observability stack.

## Endpoints

- GET /health
- GET /metrics
- GET /api/users
- POST /api/users
- GET /api/products
- GET /api/products/{id}

## Run locally

```bash
cd app
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 3000
```
