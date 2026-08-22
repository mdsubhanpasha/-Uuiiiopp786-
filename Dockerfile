# ==============================================================================
# Multi-Stage Dockerfile for CloudNative-Ops-Day3 FastAPI Microservice
# Stage 1: Build & Dependency Wheel Builder
# Stage 2: Hardened Non-Root Production Runtime
# ==============================================================================

# --- STAGE 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies manifest
COPY requirements.txt .

# Build wheels for distribution
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


# --- STAGE 2: Production Runtime ---
FROM python:3.11-slim AS runtime

LABEL maintainer="DevOps Cloud Platform Architect" \
      project="devops-day3-cloudnative-pipeline" \
      version="1.0.0" \
      description="Production Multi-Stage FastAPI Microservice"

# Create non-root system group and user for container hardening
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -m appuser

WORKDIR /app

# Copy wheels from builder stage and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application source code
COPY --chown=appuser:appgroup src/ /app/src/
COPY --chown=appuser:appgroup main.py /app/main.py

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    APP_ENV=production

# Expose microservice port
EXPOSE 8000

# Switch to non-root user
USER appuser

# Healthcheck configuration
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start Uvicorn ASGI server
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
