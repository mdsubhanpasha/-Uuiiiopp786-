# Day 26 - AI Log Analyzer Pro (Production Grade)

Production-grade AI-powered Log Analyzer featuring multi-format log parsing, machine learning anomaly detection (`IsolationForest`), automated remediation scripts, Prometheus observability metrics, and DevSecOps CI/CD integration.

---

## 🏗 System Architecture

```
                    ┌─────────────────────────┐
                    │    Incoming System      │
                    │   (Nginx / K8s / Docker) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Log Parser Module     │
                    │   (log_parser.py)       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  AI Anomaly Detector    │
                    │ (IsolationForest + Regex)│
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
    ┌─────────────────────────┐     ┌─────────────────────────┐
    │  Auto-Remediation Engine│     │ Prometheus Metrics      │
    │  (remediate.sh)         │     │  (/metrics Counter)     │
    └─────────────────────────┘     └─────────────────────────┘
                 │                               │
                 ▼                               ▼
    ┌─────────────────────────┐     ┌─────────────────────────┐
    │ Auto-Actions:           │     │ Alerting Rules:         │
    │  - Disk Cleanup         │     │  - High5xxRate          │
    │  - Restart Pod          │     │  - OOMKilled            │
    │  - Scale Up Replicas    │     │  - PodCrashLooping      │
    └─────────────────────────┘     └─────────────────────────┘
```

---

## 🚀 Key Features

1. **Multi-Format Log Parser (`log_parser.py`)**:
   - Parses **Nginx Access & Error Logs** (IP, timestamps, request method/path, HTTP status code, body size).
   - Parses **Kubernetes Pod Logs** (pod name, timestamp, stream stderr/stdout, severity log level, message body).
   - Parses **Docker Container Logs** (container ID, stream stderr/stdout, message body).

2. **AI & ML Anomaly Detection (`anomaly_detector.py`)**:
   - Uses `IsolationForest` unsupervised machine learning (scikit-learn) for behavioral pattern detection.
   - Detects **5xx HTTP Error Spikes** (>10 5xx errors or >30% error rate).
   - Detects **Out of Memory (OOMKilled)** conditions.
   - Detects **CrashLoopBackOff** pod restart states.
   - Detects **Disk Full / No space left on device** warnings.

3. **Auto-Remediation Engine (`auto_remediation.py` & `scripts/remediate.sh`)**:
   - **Disk Full** -> Triggers temporary log and disk cleanup (`cleanup`).
   - **CrashLoopBackOff / OOMKilled** -> Triggers container or Kubernetes pod restart (`restart_pod`).
   - **5xx HTTP Spikes** -> Triggers auto-scaling of application instances (`scale_up`).

4. **Production FastAPI Service (`app.py`)**:
   - `POST /analyze`: Process raw log arrays or upload `.log` files, perform ML anomaly detection, and execute auto-remediation.
   - `GET /anomalies`: Fetch history of detected anomalies.
   - `POST /remediate`: Manually execute target remediation actions.
   - `GET /metrics`: Native Prometheus metrics endpoint.
   - `GET /health`: Service health check.

5. **Observability & Infrastructure Stack**:
   - **Prometheus Alerting Rules** (`prometheus/alerts.yml`) monitoring 5xx error rates, OOM events, CrashLooping, and low disk space.
   - **ELK Stack Integration** (`docker-compose.yml`) with Elasticsearch, Logstash, Kibana, and Prometheus.

6. **DevSecOps Pipeline**:
   - **SonarQube SAST Analysis** (`sonar-project.properties`).
   - **Trivy Container Vulnerability Scan** failing build on HIGH or CRITICAL CVEs.
   - **AWS ECR Container Image Push** with non-root Docker security context.

---

## 📁 Repository Structure

```
Day-26-AI-Log-Analyzer-Pro/
├── app/
│   ├── __init__.py
│   ├── analyzer.py            # Main AI log analyzer orchestrator
│   ├── log_parser.py          # Log parser for Nginx, K8s, Docker
│   ├── anomaly_detector.py    # IsolationForest ML anomaly detector
│   ├── auto_remediation.py   # Auto-remediation trigger engine
│   ├── app.py                 # FastAPI web REST API
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Multi-stage non-root container image
│   └── test_analyzer.py       # Unit and integration test suite (>90% coverage)
├── prometheus/
│   └── alerts.yml             # Prometheus alerting rules for log anomalies
├── scripts/
│   └── remediate.sh           # Shell remediation script (cleanup, restart_pod, scale_up)
├── docker-compose.yml         # Containerized stack (ELK + App + Prometheus)
├── Jenkinsfile                # DevSecOps CI/CD Pipeline
├── .dockerignore
├── sonar-project.properties   # SonarQube SAST configuration
└── README.md
```

---

## 🛠 Local Setup & Running

### Option 1: Docker Compose (Full Production Stack)

To spin up the entire production stack including **AI Log Analyzer App, Prometheus, Elasticsearch, Logstash, and Kibana**:

```bash
cd Day-26-AI-Log-Analyzer-Pro
docker-compose up -d --build
```

Access services:
- **FastAPI API**: http://localhost:8000
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Prometheus UI**: http://localhost:9090
- **Kibana UI**: http://localhost:5601

---

### Option 2: Run Python Service Directly

```bash
cd Day-26-AI-Log-Analyzer-Pro
pip install -r app/requirements.txt
PYTHONPATH=. uvicorn app.app:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Running Unit & Integration Tests

Run pytest with complete code coverage report:

```bash
cd Day-26-AI-Log-Analyzer-Pro
PYTHONPATH=. pytest app/test_analyzer.py -v --cov=app --cov-report=term-missing
```

---

## 📡 API Usage Examples (`curl`)

### 1. Health Check
```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Log Analyzer Pro",
  "version": "1.0.0"
}
```

---

### 2. Analyze JSON Logs (`POST /analyze`)

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "logs": [
      "192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] \"GET /api/v1/resource HTTP/1.1\" 200 1024 \"-\" \"Mozilla/5.0\"",
      "2023-10-10T14:05:00Z stderr ERROR [pod-payment-service] Fatal Error: OOMKilled process 102 total-vm:204800kB",
      "2023-10-10T14:06:00Z stderr ERROR Disk full: No space left on device"
    ],
    "auto_remediate": true
  }'
```

**Response:**
```json
{
  "total_logs_processed": 3,
  "anomalies_found": 2,
  "anomalies": [
    {
      "type": "oom_killed",
      "severity": "CRITICAL",
      "confidence_score": 0.98,
      "message": "Out Of Memory (OOM) anomaly detected: 2023-10-10T14:05:00Z stderr ERROR [pod-payment-service] Fatal Error: OOMKilled process 102 total-vm:204800kB",
      "trigger_remediation": "restart_pod"
    },
    {
      "type": "disk_full",
      "severity": "CRITICAL",
      "confidence_score": 0.99,
      "message": "Disk Full anomaly detected: 2023-10-10T14:06:00Z stderr ERROR Disk full: No space left on device",
      "trigger_remediation": "cleanup"
    }
  ],
  "remediations_executed": 2,
  "remediations": [
    {
      "status": "success",
      "action": "restart_pod",
      "message": "Auto-remediation action 'restart_pod' completed successfully."
    },
    {
      "status": "success",
      "action": "cleanup",
      "message": "Auto-remediation action 'cleanup' completed successfully."
    }
  ]
}
```

---

### 3. Retrieve Detected Anomalies (`GET /anomalies`)

```bash
curl -X GET http://localhost:8000/anomalies?limit=10
```

---

### 4. Manually Trigger Remediation (`POST /remediate`)

```bash
curl -X POST http://localhost:8000/remediate \
  -H "Content-Type: application/json" \
  -d '{
    "action": "scale_up",
    "details": {
      "deployment": "frontend-web",
      "replicas": 5
    }
  }'
```

**Response:**
```json
{
  "status": "success",
  "action": "scale_up",
  "message": "Auto-remediation action 'scale_up' completed successfully.",
  "details": {
    "deployment": "frontend-web",
    "replicas": 5
  }
}
```

---

### 5. Prometheus Observability Metrics (`GET /metrics`)

```bash
curl -X GET http://localhost:8000/metrics
```

Exposes standard Prometheus metrics:
- `log_analyzer_logs_parsed_total`
- `log_analyzer_anomalies_detected_total`
- `log_analyzer_remediations_triggered_total`
- `log_analyzer_duration_seconds`
