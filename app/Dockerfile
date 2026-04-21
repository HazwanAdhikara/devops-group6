FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 appuser

COPY src/ ./src/
COPY data/ ./data/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000/health')"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3000"]
