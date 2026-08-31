# Day 25: Production-Grade DevSecOps Pipeline Project 🚀🔒

[![Build Status](https://img.shields.io/badge/Jenkins-Pipeline%20Passing-brightgreen?logo=jenkins)](https://jenkins.io)
[![Security Gate](https://img.shields.io/badge/Trivy-HIGH%2FCRITICAL%20PASS-blue?logo=aquasec)](https://aquasecurity.github.io/trivy)
[![SonarQube Quality Gate](https://img.shields.io/badge/SonarQube-Passed-success?logo=sonarqube)](https://sonarqube.org)
[![Docker Multi-Stage](https://img.shields.io/badge/Docker-Multi--Stage%20Non--Root-blue?logo=docker)](https://docker.com)
[![AWS ECR](https://img.shields.io/badge/AWS%20ECR-Registry%20Ready-orange?logo=amazon-aws)](https://aws.amazon.com/ecr/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Summary & Architecture

**DevSecOps Pipeline Pro** is a production-grade, enterprise-ready automated security & CI/CD pipeline built to demonstrate **Shift-Left Security** principles. This project integrates automated SAST (Static Application Security Testing) code quality scanning, container vulnerability scanning, multi-stage non-root container image construction, and secure cloud container registry publishing to AWS Elastic Container Registry (ECR).

### 🏗️ End-to-End DevSecOps Pipeline Architecture (Text Diagram)

```text
  +-------------------------------------------------------------------------------------------------------+
  |                                        DEVSECOPS CI/CD PIPELINE                                      |
  +-------------------------------------------------------------------------------------------------------+

 [ Developer ]
      │
      │ git push origin main
      ▼
+──────────────────┐       +───────────────────────────────────┐       +─────────────────────────────────┐
│ Stage 1:         │       │ Stage 2:                          │       │ Stage 3:                        │
│ GitHub Checkout  ├──────►│ SonarQube Code Quality Analysis   ├──────►│ Build Docker Image              │
│ (Source Control) │       │ (SAST / Security & Bugs Scan)     │       │ (Multi-Stage, Non-Root User)    │
+──────────────────┘       +───────────────────────────────────┘       +─────────────────────────────────┘
                                                                                        │
                                                                                        ▼
+──────────────────┐       +───────────────────────────────────┐       +─────────────────────────────────┐
│ Stage 6:         │       │ Stage 5:                          │       │ Stage 4:                        │
│ Workspace        │◄──────┤ Push to AWS ECR                   │◄──────┤ Trivy Vulnerability Scan        │
│ Cleanup          │       │ (Secure Authentication & Publish) │       │ (Gate: Fail on HIGH/CRITICAL)   │
+──────────────────┘       +───────────────────────────────────┘       +─────────────────────────────────┘
```

---

## 📂 Directory Structure

```text
Day-25-DevSecOps-Pipeline-Pro/
├── app/
│   ├── app.py                  # Production Python Flask REST API (/ and /health endpoints)
│   ├── test_app.py             # Pytest unit & integration test suite
│   ├── requirements.txt        # Application dependencies (Flask, Gunicorn, Pytest)
│   ├── Dockerfile              # Multi-stage build, non-root user (appuser), HEALTHCHECK
│   └── .dockerignore           # Excludes local caches, logs, git & pipeline files
├── Jenkinsfile                 # Full declarative pipeline (6 Stages + Security Gates)
├── sonar-project.properties    # SonarQube Scanner configuration
├── docker-compose.yml          # Local environment orchestration (Jenkins, SonarQube, App)
├── .dockerignore               # Project-wide Docker exclusion rules
└── README.md                   # Complete documentation & interview readiness guide
```

---

## 🔒 Key DevSecOps & Security Best Practices Implemented

1. **Shift-Left Security:**
   Security checks (SonarQube SAST & Trivy Container Vulnerability Scanning) are integrated directly inside the CI/CD pipeline prior to artifact deployment.
2. **Principle of Least Privilege (Non-Root User):**
   The application container executes under a dedicated non-root UID/GID (`appuser:10001`), protecting the host container runtime against privilege escalation attacks (CVE-2019-5736 mitigations).
3. **Multi-Stage Container Construction:**
   Build tools and build-time dependencies (`gcc`, build caches) are kept strictly in the builder stage (`python:3.9-slim`), resulting in a minimal, attack-surface-reduced runtime image.
4. **Automated Container Health Probes (`HEALTHCHECK`):**
   Configured Docker `HEALTHCHECK` ensures orchestration engines (Docker, K8s, ECS) can monitor container liveness dynamically.
5. **Strict Automated Security Gate (Trivy Scan):**
   The pipeline enforces zero-tolerance for unmitigated vulnerabilities; if Trivy detects any **HIGH** or **CRITICAL** CVEs, the build fails immediately (`--exit-code 1`).
6. **Isolated Secrets & ECR Authentication:**
   AWS IAM Credentials and ECR URL endpoints are managed safely via Jenkins environment variables and credential stores (`AWS_REGION`, `ECR_URL`).

---

## 🛠️ Pipeline Stages (Jenkinsfile Deep Dive)

| Stage | Name | Action & Security Gate |
| :--- | :--- | :--- |
| **Stage 1** | **Checkout from GitHub** | Pulls application source code securely from Git version control. |
| **Stage 2** | **SonarQube Analysis** | Performs SAST scanning for code smells, bugs, security hotspots, and vulnerabilities. |
| **Stage 3** | **Build Docker Image** | Builds a hardened multi-stage image tagged with unique `${BUILD_NUMBER}` and `latest`. |
| **Stage 4** | **Trivy Vulnerability Scan** | Scans container OS packages & dependencies. **Fails pipeline** if `HIGH` or `CRITICAL` found. |
| **Stage 5** | **Push to AWS ECR** | Authenticates securely via AWS CLI and pushes container images to AWS Elastic Container Registry. |
| **Stage 6** | **Cleanup** | Cleans up local untagged Docker images and temporary build artifacts to maintain disk hygiene. |

---

## 🚀 Quickstart: Running Locally with Docker Compose

To test Jenkins, SonarQube, and the target Flask app locally on your machine:

### 1. Launch Services
```bash
cd Day-25-DevSecOps-Pipeline-Pro
docker-compose up -d --build
```

### 2. Verify Services
- **Flask App:** `http://localhost:5000` (Healthcheck: `http://localhost:5000/health`)
- **Jenkins:** `http://localhost:8080`
- **SonarQube:** `http://localhost:9000` (Default creds: `admin` / `admin`)

### 3. Test Flask Application Endpoints
```bash
# Test Root Endpoint
curl -s http://localhost:5000/ | jq

# Test Healthcheck Endpoint
curl -s http://localhost:5000/health | jq
```

---

## 💬 Interview Readiness & DevSecOps Q&A

### Q1: Why use multi-stage Docker builds in DevSecOps?
> **Answer:** Multi-stage builds separate build-time toolchains (compilers, dev libraries) from the final runtime image. This significantly decreases container image size, reduces the attack surface by eliminating unnecessary binaries, and eliminates potential security vulnerabilities introduced by build utilities.

### Q2: How does Trivy fit into the container security lifecycle?
> **Answer:** Trivy acts as an automated security gate during the CI/CD pipeline execution. It scans container images for known vulnerabilities (CVEs) across OS packages and language-specific dependencies. By configuring Trivy with `--exit-code 1 --severity HIGH,CRITICAL`, we ensure that vulnerable container images are caught before being published to registries like AWS ECR.

### Q3: Why is running containers as non-root critical?
> **Answer:** By default, containers run as `root` (UID 0), which matches host root privileges inside container namespaces. If a container breakout vulnerability occurs, an attacker gains root control over the underlying host node. Creating a dedicated non-root user (`USER appuser`) enforces the principle of least privilege and prevents container escape exploits.

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
