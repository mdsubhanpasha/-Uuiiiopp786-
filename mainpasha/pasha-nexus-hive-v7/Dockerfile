FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium || true

COPY . .

EXPOSE 8000 8501

CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"]
