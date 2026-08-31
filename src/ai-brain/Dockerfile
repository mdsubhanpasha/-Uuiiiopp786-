FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim AS runner

WORKDIR /app
COPY --from=builder /install /usr/local
COPY main.py .

RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /bin/false appuser && \
    chown -R appuser:appuser /app

USER 10001:10001

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')" || exit 1

ENTRYPOINT ["python", "main.py"]
