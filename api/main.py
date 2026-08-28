import logging
import sys
import time
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

# 1. Custom JSON Logger Setup
logger = logging.getLogger("fastapi_service")
logHandler = logging.StreamHandler(sys.stdout)


class CustomJsonFormatter(jsonlogger.JsonFormatter):

  def add_fields(self, log_record, record, message_dict):
    super().add_fields(log_record, record, message_dict)
    log_record["timestamp"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
    )
    log_record["level"] = record.levelname
    log_record["correlation_id"] = correlation_id.get() or "N/A"


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(correlation_id)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 2. FastAPI App Setup
app = FastAPI(title="FinAgent Ops Service")

# 3. Correlation ID Middleware (X-Request-ID Header)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
)

# 4. Prometheus Metrics Expose
Instrumentator().instrument(app).expose(app)


# 5. Access Log Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
  start_time = time.time()
  response: Response = await call_next(request)
  duration_ms = round((time.time() - start_time) * 1000, 2)

  logger.info(
      "HTTP Request Processed",
      extra={
          "http_method": request.method,
          "path": request.url.path,
          "status_code": response.status_code,
          "latency_ms": duration_ms,
          "client_ip": request.client.host if request.client else "unknown",
      },
  )
  return response


@app.get("/")
def read_root():
  return {"status": "healthy", "service": "finagent-ops"}


@app.get("/error-test")
def trigger_error():
  logger.error(
      "Manual test error triggered for observability testing",
      extra={"error_code": "TEST_500"},
  )
  return {"error": "Simulated exception logged"}