"""
Log Parser module for Day 26 - AI Log Analyzer Pro.
Parses Nginx (access/error), Kubernetes pod logs, and Docker container logs.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional


class LogParser:
    """Parser for Nginx, Kubernetes, and Docker log formats."""

    # Regex patterns
    NGINX_ACCESS_PATTERN = re.compile(
        r'^(?P<client_ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<body_bytes_sent>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )

    NGINX_ERROR_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) \[(?P<level>\w+)\] \d+#\d+: \*(?P<connection_id>\d+) (?P<message>.*)'
    )

    K8S_LOG_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(?P<stream>stdout|stderr)\s+(?P<log_level>INFO|WARN|WARNING|ERROR|FATAL|DEBUG)?\s*(\[(?P<pod_info>[^\]]+)\])?\s*(?P<message>.*)$'
    )

    DOCKER_LOG_PATTERN = re.compile(
        r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(?P<stream>stdout|stderr)\s+(?P<container_id>[a-f0-9]{12}|[a-f0-9]{64})?\s*(?P<message>.*)$'
    )

    @classmethod
    def parse_nginx_access(cls, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse single Nginx access log entry."""
        match = cls.NGINX_ACCESS_PATTERN.match(log_line.strip())
        if not match:
            return None
        data = match.groupdict()
        return {
            "log_type": "nginx_access",
            "timestamp": data["timestamp"],
            "client_ip": data["client_ip"],
            "method": data["method"],
            "path": data["path"],
            "status_code": int(data["status"]),
            "body_bytes_sent": int(data["body_bytes_sent"]),
            "user_agent": data["user_agent"],
            "message": f"{data['method']} {data['path']} -> {data['status']}",
            "is_error": int(data["status"]) >= 400,
            "is_5xx": int(data["status"]) >= 500,
        }

    @classmethod
    def parse_nginx_error(cls, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse single Nginx error log entry."""
        match = cls.NGINX_ERROR_PATTERN.match(log_line.strip())
        if not match:
            return None
        data = match.groupdict()
        level = data["level"].upper()
        return {
            "log_type": "nginx_error",
            "timestamp": data["timestamp"],
            "log_level": level,
            "message": data["message"],
            "is_error": level in ("ERROR", "CRIT", "ALERT", "EMERG"),
            "is_5xx": "500" in data["message"] or "502" in data["message"] or "504" in data["message"],
        }

    @classmethod
    def parse_k8s_log(cls, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse single Kubernetes pod log entry."""
        line = log_line.strip()
        match = cls.K8S_LOG_PATTERN.match(line)
        if not match:
            # Fallback for structured or simple k8s log lines
            if "CrashLoopBackOff" in line or "OOMKilled" in line or "Error" in line:
                return {
                    "log_type": "k8s",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "stream": "stderr",
                    "log_level": "ERROR",
                    "pod_name": "unknown-pod",
                    "message": line,
                    "is_error": True,
                    "is_5xx": False,
                }
            return None

        data = match.groupdict()
        msg = data["message"]
        level = data.get("log_level") or ("ERROR" if data["stream"] == "stderr" or "error" in msg.lower() else "INFO")

        return {
            "log_type": "k8s",
            "timestamp": data["timestamp"],
            "stream": data["stream"],
            "log_level": level,
            "pod_name": data.get("pod_info") or "k8s-pod",
            "message": msg,
            "is_error": level in ("ERROR", "FATAL") or "error" in msg.lower() or "oom" in msg.lower(),
            "is_5xx": "500" in msg or "502" in msg or "503" in msg,
        }

    @classmethod
    def parse_docker_log(cls, log_line: str) -> Optional[Dict[str, Any]]:
        """Parse single Docker container log entry."""
        line = log_line.strip()
        match = cls.DOCKER_LOG_PATTERN.match(line)
        if not match:
            if "error" in line.lower() or "fatal" in line.lower() or "oom" in line.lower():
                return {
                    "log_type": "docker",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "stream": "stderr",
                    "container_id": "unknown-container",
                    "message": line,
                    "is_error": True,
                    "is_5xx": "500" in line,
                }
            return None

        data = match.groupdict()
        msg = data["message"]
        is_err = data["stream"] == "stderr" or "error" in msg.lower() or "failed" in msg.lower() or "oom" in msg.lower()

        return {
            "log_type": "docker",
            "timestamp": data["timestamp"],
            "stream": data["stream"],
            "container_id": data.get("container_id") or "container-1",
            "message": msg,
            "is_error": is_err,
            "is_5xx": "500" in msg or "502" in msg or "503" in msg,
        }

    @classmethod
    def parse_line(cls, log_line: str) -> Dict[str, Any]:
        """Detect format and parse line automatically."""
        line = log_line.strip()
        if not line:
            return {"log_type": "unknown", "message": "", "is_error": False, "is_5xx": False}

        # Try Nginx access first
        res = cls.parse_nginx_access(line)
        if res:
            return res

        # Try Nginx error
        res = cls.parse_nginx_error(line)
        if res:
            return res

        # Try K8s log
        res = cls.parse_k8s_log(line)
        if res:
            return res

        # Try Docker log
        res = cls.parse_docker_log(line)
        if res:
            return res

        # Generic fallback
        is_err = any(k in line.lower() for k in ["error", "fatal", "fail", "oom", "crashloopbackoff", "disk full"])
        is_5xx = any(f" {status} " in f" {line} " or f"HTTP/{status}" in line for status in [500, 502, 503, 504]) or "5xx" in line.lower()

        return {
            "log_type": "generic",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message": line,
            "is_error": is_err,
            "is_5xx": is_5xx,
        }

    @classmethod
    def parse_bulk(cls, logs: List[str]) -> List[Dict[str, Any]]:
        """Parse multiple log lines."""
        return [cls.parse_line(line) for line in logs if line and line.strip()]
