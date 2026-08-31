# Multi-stage production Dockerfile for AI Log Analyzer Pro
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final runtime stage
FROM python:3.11-slim

LABEL maintainer="DevSecOps Team"
LABEL version="1.0.0"
LABEL description="AI Log Analyzer Pro Service"

WORKDIR /app

# Install bash and curl for healthchecks and remediation scripts
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application source code
COPY app /app/app
COPY scripts /app/scripts

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 8000

# Healthcheck definition
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
