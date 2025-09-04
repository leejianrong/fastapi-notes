# ---- base ----
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# ---- deps ----
FROM base AS deps
COPY requirements.txt .
RUN pip install -r requirements.txt && pip install gunicorn

# ---- runtime ----
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 
WORKDIR /app

# non-root user
RUN useradd -m appuser
COPY --from=deps /usr/local /usr/local
COPY app ./app

# create a log directory and give ownership to appuser
RUN mkdir -p /var/log/app && chown -R appuser:appuser /var/log/app /app
USER appuser

EXPOSE 8000
# Production server: Gunicorn with Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
