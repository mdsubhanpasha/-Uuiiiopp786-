"""
Comprehensive Unit and Integration Tests for Day 26 - AI Log Analyzer Pro.
Tests log_parser, anomaly_detector, auto_remediation, analyzer, and FastAPI app endpoints.
Targeting > 80% code coverage.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.log_parser import LogParser
from app.anomaly_detector import AnomalyDetector
from app.auto_remediation import AutoRemediationEngine
from app.analyzer import AILogAnalyzer
from app.app import app


# ------------------------------------------------------------------------------
# 1. LogParser Unit Tests
# ------------------------------------------------------------------------------
def test_parse_nginx_access_valid():
    line = '192.168.1.10 - - [10/Oct/2023:13:55:36 +0000] "GET /api/v1/resource HTTP/1.1" 200 1024 "-" "Mozilla/5.0"'
    res = LogParser.parse_nginx_access(line)
    assert res is not None
    assert res["log_type"] == "nginx_access"
    assert res["client_ip"] == "192.168.1.10"
    assert res["method"] == "GET"
    assert res["path"] == "/api/v1/resource"
    assert res["status_code"] == 200
    assert res["is_error"] is False
    assert res["is_5xx"] is False


def test_parse_nginx_access_5xx():
    line = '10.0.0.1 - - [10/Oct/2023:13:56:00 +0000] "POST /checkout HTTP/1.1" 500 256 "-" "curl/7.68.0"'
    res = LogParser.parse_nginx_access(line)
    assert res is not None
    assert res["status_code"] == 500
    assert res["is_error"] is True
    assert res["is_5xx"] is True


def test_parse_nginx_error():
    line = '2023/10/10 14:00:00 [error] 1234#5678: *1 open() "/var/www/html/index.html" failed (2: No such file or directory)'
    res = LogParser.parse_nginx_error(line)
    assert res is not None
    assert res["log_type"] == "nginx_error"
    assert res["log_level"] == "ERROR"
    assert res["is_error"] is True


def test_parse_k8s_log():
    line = '2023-10-10T14:05:00.123456Z stderr ERROR [my-pod-1] Pod crashed with CrashLoopBackOff status'
    res = LogParser.parse_k8s_log(line)
    assert res is not None
    assert res["log_type"] == "k8s"
    assert res["stream"] == "stderr"
    assert res["pod_name"] == "my-pod-1"
    assert res["is_error"] is True


def test_parse_docker_log():
    line = '2023-10-10T14:10:00Z stderr a1b2c3d4e5f6 OOMKilled process 102 (nginx) total-vm:204800kB'
    res = LogParser.parse_docker_log(line)
    assert res is not None
    assert res["log_type"] == "docker"
    assert res["container_id"] == "a1b2c3d4e5f6"
    assert res["is_error"] is True


def test_parse_line_auto_detection():
    nginx_access = '192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 500 "-" "Mozilla/5.0"'
    res1 = LogParser.parse_line(nginx_access)
    assert res1["log_type"] == "nginx_access"

    generic_line = "Just a standard application print statement"
    res2 = LogParser.parse_line(generic_line)
    assert res2["log_type"] == "generic"
    assert res2["is_error"] is False

    empty_line = ""
    res3 = LogParser.parse_line(empty_line)
    assert res3["log_type"] == "unknown"


def test_parse_bulk():
    lines = [
        '192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 500 "-" "user-agent"',
        '2023-10-10T14:05:00Z stderr ERROR [pod-a] Out of memory condition',
    ]
    parsed = LogParser.parse_bulk(lines)
    assert len(parsed) == 2


# ------------------------------------------------------------------------------
# 2. AnomalyDetector Unit Tests
# ------------------------------------------------------------------------------
def test_anomaly_detector_disk_full():
    logs = [
        {"message": "Error: Disk full. No space left on device", "status_code": 500, "is_error": True, "is_5xx": True}
    ]
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(logs)
    assert len(anomalies) >= 1
    disk_anomaly = next((a for a in anomalies if a["type"] == "disk_full"), None)
    assert disk_anomaly is not None
    assert disk_anomaly["trigger_remediation"] == "cleanup"


def test_anomaly_detector_oom_killed():
    logs = [
        {"message": "Fatal error: OOMKilled process killed due to memory limit", "status_code": 500, "is_error": True, "is_5xx": False}
    ]
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(logs)
    oom_anomaly = next((a for a in anomalies if a["type"] == "oom_killed"), None)
    assert oom_anomaly is not None
    assert oom_anomaly["trigger_remediation"] == "restart_pod"


def test_anomaly_detector_crash_loop():
    logs = [
        {"message": "Pod restarting failed container CrashLoopBackOff", "status_code": 500, "is_error": True, "is_5xx": False}
    ]
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(logs)
    crash_anomaly = next((a for a in anomalies if a["type"] == "crash_loop_backoff"), None)
    assert crash_anomaly is not None
    assert crash_anomaly["trigger_remediation"] == "restart_pod"


def test_anomaly_detector_5xx_spike():
    logs = [
        {"message": f"GET /api -> 500 Internal Server Error {i}", "status_code": 500, "is_error": True, "is_5xx": True}
        for i in range(12)
    ]
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(logs)
    spike_anomaly = next((a for a in anomalies if a["type"] == "5xx_spike"), None)
    assert spike_anomaly is not None
    assert spike_anomaly["trigger_remediation"] == "scale_up"


def test_anomaly_detector_ml_fit_and_detect():
    detector = AnomalyDetector(contamination=0.2)
    normal_logs = [
        {"message": "Normal GET /home 200", "status_code": 200, "is_error": False, "is_5xx": False}
        for _ in range(20)
    ]
    detector.fit_model(normal_logs)
    assert detector.is_fitted is True

    abnormal_logs = [
        {"message": "UNEXPECTED SYSTEM FAILURE ERROR CODE 9999999999999999", "status_code": 503, "is_error": True, "is_5xx": True}
    ]
    anomalies = detector.detect_anomalies(abnormal_logs)
    assert isinstance(anomalies, list)


# ------------------------------------------------------------------------------
# 3. AutoRemediationEngine Unit Tests
# ------------------------------------------------------------------------------
def test_auto_remediation_simulated():
    engine = AutoRemediationEngine(script_path="/nonexistent/remediate.sh")
    res = engine.execute_remediation("cleanup")
    assert res["status"] == "success"
    assert res["action"] == "cleanup"
    assert res["executed_via"] == "simulated_engine"


def test_auto_remediation_real_script(tmp_path):
    script_file = tmp_path / "test_remediate.sh"
    script_file.write_text("#!/bin/bash\necho 'Mock remediation output'\nexit 0\n")
    os.chmod(script_file, 0o755)

    engine = AutoRemediationEngine(script_path=str(script_file))
    res = engine.execute_remediation("restart_pod")
    assert res["status"] == "success"
    assert "Mock remediation output" in res["stdout"]


def test_auto_remediation_script_failure(tmp_path):
    script_file = tmp_path / "test_remediate.sh"
    script_file.write_text("#!/bin/bash\necho 'Error details' >&2\nexit 1\n")
    os.chmod(script_file, 0o755)

    engine = AutoRemediationEngine(script_path=str(script_file))
    res = engine.execute_remediation("scale_up")
    assert res["status"] == "failed"
    assert "Error details" in res["stderr"]


def test_auto_remediation_remediate_anomaly():
    engine = AutoRemediationEngine(script_path="/nonexistent/remediate.sh")
    anomaly = {
        "type": "disk_full",
        "trigger_remediation": "cleanup",
        "message": "Disk is full"
    }
    res = engine.remediate_anomaly(anomaly)
    assert res is not None
    assert res["action"] == "cleanup"

    no_trigger = {"type": "info", "message": "all good"}
    assert engine.remediate_anomaly(no_trigger) is None


# ------------------------------------------------------------------------------
# 4. AILogAnalyzer Orchestrator Unit Tests
# ------------------------------------------------------------------------------
def test_ai_log_analyzer_process():
    analyzer = AILogAnalyzer(remediation_script="/nonexistent/remediate.sh")
    raw_logs = [
        '192.168.1.10 - - [10/Oct/2023:13:55:36 +0000] "GET /api HTTP/1.1" 200 1024 "-" "curl"',
        '2023-10-10T14:05:00Z stderr ERROR [pod-a] Out of memory OOMKilled condition encountered'
    ]
    summary = analyzer.process_logs(raw_logs, auto_remediate=True)
    assert summary["total_logs_processed"] == 2
    assert summary["anomalies_found"] >= 1
    assert summary["remediations_executed"] >= 1

    history = analyzer.get_recent_anomalies(limit=10)
    assert len(history) >= 1


# ------------------------------------------------------------------------------
# 5. FastAPI Integration Tests
# ------------------------------------------------------------------------------
client = TestClient(app)


def test_endpoint_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_endpoint_analyze_json():
    payload = {
        "logs": [
            '192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 500 "-" "test"',
            '2023-10-10T14:05:00Z stderr ERROR Disk Full no space left on device'
        ],
        "auto_remediate": True
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_logs_processed"] == 2
    assert data["anomalies_found"] >= 1


def test_endpoint_analyze_file():
    log_content = b'192.168.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 500 "-" "test"\n'
    files = {"file": ("test.log", log_content, "text/plain")}
    response = client.post("/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["total_logs_processed"] == 1


def test_endpoint_analyze_empty():
    response = client.post("/analyze", json={"logs": []})
    assert response.status_code == 200
    data = response.json()
    assert data["total_logs_processed"] == 0


def test_endpoint_anomalies_get():
    response = client.get("/anomalies?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "anomalies" in data


def test_endpoint_remediate_valid():
    payload = {"action": "cleanup", "details": {"target": "sys_logs"}}
    response = client.post("/remediate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "cleanup"


def test_endpoint_remediate_invalid():
    payload = {"action": "invalid_action_name"}
    response = client.post("/remediate", json=payload)
    assert response.status_code == 400


def test_endpoint_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "log_analyzer_logs_parsed_total" in response.text
