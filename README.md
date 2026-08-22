# CloudNative-Ops-Day3: Production CI/CD & Automated Container Security Pipeline

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker Multi-Stage](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP8](https://img.shields.io/badge/code%20style-PEP8-green.svg)](https://www.python.org/dev/peps/pep-0008/)

**CloudNative-Ops-Day3** is an enterprise-grade Day-3 DevOps delivery pipeline featuring an optimized FastAPI microservice, hardened multi-stage Docker build, automated container security scanning, automated GitHub repository deployment, and LinkedIn release announcements.

---

## 🏗️ Key Architectural Components

```text
                                  +-----------------------+
                                  |   FastAPI Microservice|
                                  |     (src/app.py)      |
                                  +-----------+-----------+
                                              |
      +-------------------+-------------------+-------------------+-------------------+
      |                   |                   |                   |                   |
      v                   v                   v                   v                   v
+------------+     +------------+     +------------+     +------------+     +------------+
| GET /      |     | GET /health|     |GET /metrics|     |POST        |     | Multi-Stage|
| Metadata   |     | Uptime     |     | Telemetry  |     |/transaction|     | Dockerfile |
+------------+     +------------+     +------------+     +------------+     +------------+
                                              |
                                              v
                                  +-----------------------+
                                  | Security Auditor      |
                                  |scripts/security_audit |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |  GitHub Actions CI/CD |
                                  | (.github/workflows)   |
                                  +-----------+-----------+
                                              |
                      +-----------------------+-----------------------+
                      |                                               |
                      v                                               v
          +-----------------------+                       +-----------------------+
          | GitHub Deployer       |                       | LinkedIn Announcer    |
          |(scripts/github_deploy)|                       |(scripts/linkedin_post)|
          +-----------------------+                       +-----------------------+
```

1. **Application Microservice (`src/app.py`)**: Production-ready FastAPI service offering metadata (`GET /`), health checks (`GET /health`), real-time operational metrics (`GET /metrics`), and input-validated transaction processing (`POST /transaction`).
2. **Optimized Multi-Stage Dockerfile (`Dockerfile`)**: Production multi-stage build using `python:3.11-slim` builder and runtime stages, running as a non-root system user (`appuser`), minimizing image size, and configuring container health checks (`HEALTHCHECK`).
3. **Automated Security Auditor (`scripts/security_audit.py`)**: Scans `requirements.txt` for dependency vulnerabilities and evaluates `Dockerfile` against 6 CloudNative container hardening rules.
4. **GitHub Deployment Automation (`scripts/github_deploy.py`)**: Automates git status checks, commit creation, and code deployment targeting the repository `devops-day3-cloudnative-pipeline`.
5. **LinkedIn Release Announcer (`scripts/linkedin_poster.py`)**: Reads pipeline completion status and automatically posts technical release announcements to LinkedIn via API.
6. **Automated CI/CD Pipeline (`.github/workflows/ci_cd.yml`)**: GitHub Actions workflow executing PEP8 linting (Flake8), unit & integration tests (Pytest), security scans, Docker build verification, and deployment simulations.

---

## 📁 Repository Structure

```text
devops-day3-cloudnative-pipeline/
├── .github/
│   └── workflows/
│       └── ci_cd.yml             # GitHub Actions CI/CD Pipeline
├── src/
│   ├── __init__.py               # Package exports
│   └── app.py                    # FastAPI Microservice
├── tests/
│   ├── __init__.py               # Test package initialization
│   └── test_app.py               # Unit & Integration tests
├── scripts/
│   ├── security_audit.py         # Container & dependency security scanner
│   ├── github_deploy.py          # GitHub repository deployment automation
│   └── linkedin_poster.py        # Automated LinkedIn technical announcer
├── Dockerfile                    # Multi-stage production Dockerfile
├── .dockerignore                 # Docker build exclusions
├── .env.example                  # Environment configuration template
├── requirements.txt              # Python dependencies
├── README.md                     # System documentation
└── main.py                       # CLI orchestrator & entry point
```

---

## 🚀 Quickstart & Usage Guide

### 1. Installation & Environment Setup
Clone the repository and install the dependencies:
```bash
git clone https://github.com/username/devops-day3-cloudnative-pipeline.git
cd devops-day3-cloudnative-pipeline
pip install -r requirements.txt
cp .env.example .env
```

### 2. Run Complete Pipeline Demo
Run the end-to-end pipeline in dry-run mode (Security Audit -> Deployment Sync -> LinkedIn Announcement):
```bash
python main.py --mode demo
```

### 3. Start Microservice Locally
```bash
python main.py --mode serve --port 8000
```
Then visit http://localhost:8000/docs for the interactive Swagger API documentation.

---

## 🔒 Container Security Audit

Run the automated container security auditor:
```bash
python scripts/security_audit.py
```
The auditor checks:
- Multi-stage build separation (`AS builder` / `AS runtime`).
- Non-root runtime execution (`USER appuser`).
- Minimal base image footprint (`python:3.11-slim`).
- Container health checking (`HEALTHCHECK`).
- Secret/Credential exposure analysis.
- Unpinned base tag prevention.

---

## 🐳 Docker Deployment & Containerization

Build and run the containerized FastAPI microservice:
```bash
# Build multi-stage Docker image
docker build -t devops-day3-cloudnative-pipeline:1.0.0 .

# Run container on port 8000
docker run -d --name cloudnative-app -p 8000:8000 devops-day3-cloudnative-pipeline:1.0.0

# Inspect container health
docker inspect --format='{{json .State.Health}}' cloudnative-app
```

---

## 🤖 Deployment Automation Scripts

### 1. GitHub Deployment Automation
Simulate or execute synchronization to `devops-day3-cloudnative-pipeline`:
```bash
# Dry-run simulation
python scripts/github_deploy.py --dry-run

# Live push execution
python scripts/github_deploy.py --live
```

### 2. LinkedIn Technical Release Announcer
Simulate or publish release updates:
```bash
# Dry-run preview
python scripts/linkedin_poster.py

# Live publish via LinkedIn API
python scripts/linkedin_poster.py --publish
```

---

## 🧪 Testing & Code Quality

Execute Flake8 linting and Pytest test suite:
```bash
# Code linting
flake8 src scripts tests main.py

# Unit & Integration tests
PYTHONPATH=. python -m pytest tests/ -v
```

---

## 📄 License
Distributed under the MIT License.
