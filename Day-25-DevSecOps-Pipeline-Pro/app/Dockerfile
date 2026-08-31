# Multi-stage Dockerfile adhering to DevSecOps Security Best Practices
# Stage 1: Build Dependencies Stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build tools & dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Minimal Production Runner Stage
FROM python:3.9-slim AS runner

# Security: Create dedicated non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

WORKDIR /app

# Copy python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code with non-root ownership
COPY --chown=appuser:appgroup . /app

# Install curl for container HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Security: Switch to non-root user
USER appuser

# Environment variables
ENV PORT=5000 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 5000

# Docker Healthcheck to satisfy security & orchestration readiness standards
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production WSGI server launch command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]
