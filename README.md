<p align="center">
  <img src="assets/cover.png" alt="PASHA-OS Banner" width="100%">
</p>

<h1 align="center">PASHA-OS & Kubernetes Voting Microservices App</h1>
<p align="center"><strong>Autonomous C-Suite AI Operating System & Microservices Voting Infrastructure</strong><br>7 Agents. 1 Objective. Zero Downtime.</p>

---

## 🚀 What is PASHA-OS?
CEO, CFO, CTO, CMO, COO, CHRO, Legal - 7 AI Agents

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

## 📊 Monitoring (NEW from PR #11)
- **Metrics:** `/metrics` endpoint with prometheus-fastapi-instrumentator
- **K8s:** `monitoring` namespace, ServiceMonitor, PodMonitor
- **Grafana:** Golden Signals Dashboard
- **Alerts:** HTTP 5xx, latency, crash loops
- **Deploy:** `scripts/deploy-monitoring.sh`

## 🛠️ Tech Stack
Python | Node.js | .NET | PostgreSQL | Redis | Kubernetes | Kind | ArgoCD | LangGraph | FastAPI | Streamlit | Docker | Prometheus | Grafana

Built by @mdsubhanpasha
