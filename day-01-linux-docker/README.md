# TestGen AI Platform - Day 1: Linux & Docker Infrastructure

Welcome to Day 1 of the **TestGen AI Platform** DevOps engineering project. This repository contains the core containerization and Linux automation scripts required to deploy and maintain the platform infrastructure.

---

## 🛠️ Components Overview

This module provides three key infrastructure components:

1. **Linux Backup Automation Script (`backup.sh`)**:
   - Automated archive creation (`.tar.gz`) for platform data and logs.
   - SHA256 integrity checksum generation.
   - Configurable retention policy pruning backups older than $N$ days (default: 7 days).
   - Structured logging with timestamped logs.

2. **Production-Ready FastAPI Dockerfile (`Dockerfile`)**:
   - Lightweight multi-stage build based on `python:3.11-slim`.
   - Security-hardened execution using non-root system user (`appuser`).
   - Integrated healthcheck probes (`curl -f http://localhost:8000/health`).

3. **Multi-Service Container Orchestration (`docker-compose.yml`)**:
   - **Service 1 (`api`)**: FastAPI core application server.
   - **Service 2 (`db`)**: PostgreSQL database with volume persistence and healthcheck.
   - **Service 3 (`redis`)**: Redis in-memory cache and task queue broker.
   - Isolated Docker bridge network (`testgen_network`).

---

## 🏗️ Architecture

```
                       +-----------------------------+
                       |    Client / HTTP Requests   |
                       +--------------+--------------+
                                      |
                                      v (Port 8000)
                    +----------------------------------+
                    |  FastAPI Backend (testgen_api)   |
                    +-----------------+----------------+
                                      |
              +-----------------------+-----------------------+
              | (Port 5432)                                   | (Port 6379)
              v                                               v
+---------------------------+                   +---------------------------+
| PostgreSQL (testgen_db)   |                   |  Redis Cache (testgen_redis)
| Volume: postgres_data     |                   | Volume: redis_data        |
+---------------------------+                   +---------------------------+
```

---

## 📋 Prerequisites

- **Docker Engine**: v20.10+
- **Docker Compose**: v2.0+
- **Bash / Linux Environment**: Standard GNU utilities (`tar`, `gzip`, `sha256sum`, `find`)

---

## 🚀 Quick Start Guide

### 1. Environment Setup

Copy the sample environment configuration:
```bash
cp .env.example .env
```

Edit `.env` to set your credentials and API keys if necessary.

---

### 2. Launch Services with Docker Compose

Start all 3 services in detached mode:
```bash
docker compose up -d --build
```

Verify that all containers are running and healthy:
```bash
docker compose ps
```

---

### 3. Verify API Health Endpoint

Send an HTTP GET request to verify the FastAPI backend:
```bash
curl -i http://localhost:8000/health
```

Expected Response:
```json
HTTP/1.1 200 OK
content-type: application/json

{"status":"healthy"}
```

---

### 4. Monitor Container Logs

Stream logs from all services:
```bash
docker compose logs -f
```

Stream logs from a specific service (e.g. `api` or `db`):
```bash
docker compose logs -f api
docker compose logs -f db
```

---

### 5. Execute Linux Backup Script

Make sure the backup script is executable:
```bash
chmod +x backup.sh
```

Run a manual backup specifying custom source and target directories:
```bash
./backup.sh --source ../api --backup-dir ./backups --retention 7
```

Output Example:
```text
[2025-02-16 12:00:00] [INFO] Starting TestGen AI Platform Backup Process
[2025-02-16 12:00:00] [INFO] Source Directory : ../api
[2025-02-16 12:00:00] [INFO] Backup Directory : ./backups
[2025-02-16 12:00:00] [INFO] Target Archive   : ./backups/testgen-ai_backup_20250216_120000.tar.gz
[2025-02-16 12:00:00] [INFO] Creating compressed backup archive...
[2025-02-16 12:00:00] [INFO] Generating SHA256 checksum...
[2025-02-16 12:00:00] [INFO] Backup archive created successfully. Size: 24K
[2025-02-16 12:00:00] [INFO] Applying retention policy (removing archives older than 7 days)...
[2025-02-16 12:00:00] [INFO] Retention cleanup completed. 0 old backup(s) pruned.
[2025-02-16 12:00:00] [INFO] Backup process finished successfully!
```

---

### 6. Automate Backups via Linux Cron Job

To run the backup script automatically every night at 2:00 AM:
```bash
crontab -e
```

Add the following entry:
```cron
0 2 * * * /bin/bash /path/to/day-01-linux-docker/backup.sh -s /app/data -b /app/backups -r 7 >> /var/log/testgen_backup.log 2>&1
```

---

### 7. Stopping Services and Cleanup

Stop all running services:
```bash
docker compose stop
```

Stop and remove all containers, networks, and persistent volumes:
```bash
docker compose down -v
```

---

## 🛠️ Verification & Useful Commands

| Task | Command |
|---|---|
| Check container health | `docker compose ps` |
| View active container stats | `docker stats` |
| Execute command inside API container | `docker compose exec api bash` |
| Verify checksum of backup archive | `sha256sum -c backups/<archive_name>.sha256` |
| Validate docker compose configuration | `docker compose config` |

---

## 🔐 Security & Best Practices Applied

- **Non-root Docker User**: FastAPI app runs as UID `10001` (`appuser`).
- **Healthcheck Probes**: Added to all 3 containers to ensure dependency ordering and auto-healing.
- **Data Integrity**: SHA256 hashes created for all backup archives.
- **Network Isolation**: Custom bridge network prevents unauthorized access to database & cache.
