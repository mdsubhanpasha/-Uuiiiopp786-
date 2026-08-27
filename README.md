<p align="center">
  <img src="assets/cover.png" alt="PASHA-OS Banner" width="100%">
</p>

<h1 align="center">PASHA-OS & Kubernetes Voting Microservices App</h1>
<p align="center"><strong>Autonomous C-Suite AI Operating System & Microservices Voting Infrastructure</strong><br>7 Agents. 1 Objective. Zero Downtime.</p>

---

## 🚀 What is PASHA-OS?
CEO, CFO, CTO, CMO, COO, CHRO, Legal - 20-Agent Autonomous MNC Operating System.

## 📊 Monitoring & Telemetry Architecture

### 1. Prometheus & Metrics
- **Metrics Endpoint:** `/metrics` endpoint with Prometheus FastAPI metrics (`pasha_os_requests_total`, `pasha_os_request_duration_seconds`)
- **K8s Custom Resources:** `monitoring` namespace, ServiceMonitor, PodMonitor
- **Deploy Script:** `scripts/deploy-monitoring.sh`

### 2. Centralized Observability & PLG Stack (Promtail + Loki + Grafana)
See [`pasha-os-plg-observability/`](./pasha-os-plg-observability/) for the full standalone documentation and runbooks.
- **Structured JSON Telemetry:** Standardized log format outputting single-line JSON streams to `stdout` (`timestamp`, `level`, `logger_name`, `correlation_id`, `http_method`, `path`, `status_code`, `client_ip`, `latency_ms`, `message`).
- **Distributed Tracing & Correlation ID:** `asgi-correlation-id` middleware injects and propagates `X-Correlation-ID` across HTTP requests and responses.
- **Promtail Pipeline:** Custom parsing stages (`monitoring/promtail-config.yaml`) extract log labels (`level`, `http_method`, `status_code`) without high-cardinality bottlenecks.
- **Loki Data Source Provisioning:** Auto-provisioned Loki data source (`monitoring/datasources/loki-datasource.yaml`) pointing to `http://loki.monitoring.svc.cluster.local:3100`.
- **LogQL Grafana Dashboard:** Embedded LogQL streaming panel in `monitoring/dashboards/finagent-dashboard.json` for real-time error log correlation.
- **Deployment Script:** `scripts/deploy-logging.sh`

### 3. Operational Runbook & LogQL Queries
- **Deploy Logging Pipeline:**
  ```bash
  ./scripts/deploy-logging.sh
  ```
- **Validation Commands:**
  ```bash
  # Verify Promtail and Loki pod status
  kubectl get pods -n monitoring -l app=loki
  kubectl get pods -n monitoring -l app=promtail

  # Query correlation ID header
  curl -i -H "X-Correlation-ID: test-123" http://localhost:8000/health
  ```
- **LogQL Debugging Query Snippets:**
  - Query errors: `{job="kubernetes-pods"} | json | status_code >= 500 or level="ERROR"`
  - Filter by Correlation ID: `{job="kubernetes-pods"} | json | correlation_id="YOUR-CORRELATION-ID"`
  - Slow request latency (>500ms): `{job="kubernetes-pods"} | json | latency_ms > 500`

---

## 🗳️ Kubernetes Voting Microservices Application (GitOps Ready)

Production-ready microservices voting application built for Kubernetes Kind cluster with GitOps auto-sync via ArgoCD.

### Architecture Components:
- **Vote app (Python Flask):** Port `5000` (NodePort `31000`)
- **Redis queue:** In-memory queue storing incoming votes
- **Worker (.NET 8):** Background worker processing queue and persisting votes to Postgres
- **Postgres DB:** Relational database storing votes result state
- **Result app (Node.js):** Real-time web result dashboard on port `5001` (NodePort `31001`)

---

## 🛠️ Deployment Instructions

### 1. Create Kind Cluster
Create a 3-node cluster (1 control-plane, 2 worker nodes) mapping host ports `5000` and `5001`:

```bash
kind create cluster --config kind-config.yaml --name voting-cluster
```

### 2. Build & Load Container Images
Build the application container images and load them directly into your Kind cluster:

```bash
docker build -t vote:latest ./vote
docker build -t result:latest ./result
docker build -t worker:latest ./worker

kind load docker-image vote:latest --name voting-cluster
kind load docker-image result:latest --name voting-cluster
kind load docker-image worker:latest --name voting-cluster
```

### 3. Deploy via `kubectl`
Apply all Kubernetes manifests directly to the cluster:

```bash
kubectl apply -f k8s/
```

Verify all pods and services:

```bash
kubectl get pods -w
kubectl get svc
```

Access the applications:
- **Vote App:** [http://localhost:5000](http://localhost:5000)
- **Result App:** [http://localhost:5001](http://localhost:5001)

---

## 🔄 GitOps with ArgoCD Setup

### 1. Install ArgoCD
Install ArgoCD onto the cluster:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Apply ArgoCD Application Manifest
Deploy the ArgoCD Application resource watching your repository with automated sync enabled:

```bash
kubectl apply -f argocd/application.yaml
```

Check ArgoCD application sync status:

```bash
kubectl get application -n argocd
```

---

## 🛠️ Tech Stack
Python | Node.js | .NET | PostgreSQL | Redis | Kubernetes | Kind | ArgoCD | LangGraph | FastAPI | Streamlit | Docker | Prometheus | Promtail | Loki | Grafana

## 📸 Demo
![Dashboard](assets/cover.png)

Built by @mdsubhanpasha
