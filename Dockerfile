# Multi-stage production Dockerfile for FinAgent-Ops

FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY data/ data/
COPY src/ src/
COPY scripts/ scripts/
COPY main.py .

# Create directory for report artifacts
RUN mkdir -p artifacts

# Expose FastAPI server port
EXPOSE 8000

# Default entrypoint starts FastAPI service
CMD ["python", "main.py", "--mode", "api", "--port", "8000"]
