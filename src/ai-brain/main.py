import os
import time
import math
from typing import List, Optional, Dict, Any
import numpy as np
from sklearn.ensemble import IsolationForest
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import httpx

app = FastAPI(
    title="PASHA-X AI-Brain",
    description="RAG and IsolationForest Anomaly Explainer Governance Brain",
    version="1.0.0"
)

# Prometheus Metrics
INGESTED_EVENTS_COUNTER = Counter("ai_brain_ingested_events_total", "Total events ingested by AI Brain", ["event_type"])
ANOMALIES_DETECTED_COUNTER = Counter("ai_brain_anomalies_detected_total", "Total anomalies detected by IsolationForest", ["severity"])
ANALYSIS_DURATION_HISTOGRAM = Histogram("ai_brain_analysis_duration_seconds", "Histogram of analysis request processing time")

# In-memory storage for events & security knowledge base mock for Qdrant
EVENTS_DB: List[Dict[str, Any]] = []
ANOMALY_ALERTS: List[Dict[str, Any]] = []

# Mock Qdrant Security Knowledge Base
SECURITY_KNOWLEDGE_BASE = [
    {
        "id": "kb-001",
        "category": "reverse_shell",
        "pattern": ["nc -e", "/bin/sh", "/bin/bash", "socat", "python -c import socket"],
        "title": "Reverse Shell Execution Detected",
        "severity": "CRITICAL",
        "recommendation": "Immediately trigger Argo Rollout pod replacement and isolate container network namespace.",
        "mitre_technique": "T1059.004"
    },
    {
        "id": "kb-002",
        "category": "privilege_escalation",
        "pattern": ["sudo", "su", "chmod +s", "nsenter"],
        "title": "Privilege Escalation Syscall",
        "severity": "HIGH",
        "recommendation": "Deny host privileges via Kyverno policy enforcement and restart deployment.",
        "mitre_technique": "T1068"
    },
    {
        "id": "kb-003",
        "category": "unauthorized_network_egress",
        "pattern": ["curl", "wget", "sys_connect"],
        "title": "Suspicious External Network Egress",
        "severity": "MEDIUM",
        "recommendation": "Verify destination IP reputation and re-check NetworkPolicy egress rules.",
        "mitre_technique": "T1071"
    }
]

# Model initialisation for IsolationForest
# Features extracted: [is_root(0/1), command_length, args_count, is_suspicious_bin(0/1), is_unusual_port(0/1)]
class AnomalyDetector:
    def __init__(self):
        self.clf = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        # Seed initial baseline normal events
        baseline = np.array([
            [0, 15, 2, 0, 0], # normal app startup
            [0, 10, 1, 0, 0], # standard healthcheck
            [0, 25, 3, 0, 0], # standard HTTP request exec
            [0, 18, 2, 0, 0], # DB connection query
            [0, 22, 2, 0, 0], # metric scraping
            [1, 120, 8, 1, 1], # malicious reverse shell sample
        ])
        self.clf.fit(baseline)

    def extract_features(self, event: Dict[str, Any]) -> np.ndarray:
        uid = event.get("uid", 1000)
        is_root = 1 if uid == 0 else 0

        binary_path = event.get("binary_path", "")
        args = event.get("command_args", [])
        cmd_len = len(binary_path) + sum(len(a) for a in args)
        args_count = len(args)

        suspicious_keywords = ["nc", "ncat", "netcat", "socat", "/bin/sh", "chmod", "nsenter", "gdb", "ptrace"]
        is_suspicious_bin = 1 if any(k in binary_path.lower() or any(k in a.lower() for a in args) for k in suspicious_keywords) else 0

        dst_port = event.get("dst_port", 80)
        is_unusual_port = 1 if dst_port not in [80, 443, 8080, 5432, 6379, 0] else 0

        return np.array([[is_root, cmd_len, args_count, is_suspicious_bin, is_unusual_port]])

    def predict(self, event: Dict[str, Any]) -> float:
        features = self.extract_features(event)
        is_root, cmd_len, args_count, is_suspicious_bin, is_unusual_port = features[0]
        score = self.clf.decision_function(features)[0]
        # In IsolationForest lower/negative score implies anomaly
        is_anomaly = self.clf.predict(features)[0] == -1
        # Convert decision function score to anomaly confidence [0, 1]
        if is_anomaly or is_suspicious_bin or (is_root and cmd_len > 15):
            anomaly_score = max(0.85, float(1.0 / (1.0 + math.exp(score * 5.0))))
        else:
            anomaly_score = float(1.0 / (1.0 + math.exp(score * 5.0)))
        return anomaly_score, bool(is_anomaly or anomaly_score >= 0.5)

detector = AnomalyDetector()

class SyscallEventPayload(BaseModel):
    id: str
    timestamp: Optional[str] = None
    event_type: str = Field(..., description="exec or network")
    namespace: str = "default"
    pod_name: str
    container_id: Optional[str] = ""
    binary_path: str
    command_args: List[str] = []
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    dst_port: Optional[int] = 0
    syscall: str = "sys_execve"
    pid: int = 1
    uid: int = 1000

class AnalyzeRequest(BaseModel):
    event_id: str
    top_k: int = 2

class ExplainRequest(BaseModel):
    event_id: str
    anomaly_score: float
    rag_context: Dict[str, Any]

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "ai-brain"}

@app.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_event(event: SyscallEventPayload):
    evt_dict = event.model_dump()
    INGESTED_EVENTS_COUNTER.labels(event_type=event.event_type).inc()

    anomaly_score, is_anomaly = detector.predict(evt_dict)
    evt_dict["anomaly_score"] = anomaly_score
    evt_dict["is_anomaly"] = is_anomaly

    EVENTS_DB.append(evt_dict)

    if is_anomaly or anomaly_score > 0.5:
        severity = "CRITICAL" if anomaly_score > 0.8 else "HIGH"
        ANOMALIES_DETECTED_COUNTER.labels(severity=severity).inc()
        ANOMALY_ALERTS.append({
            "event_id": event.id,
            "anomaly_score": anomaly_score,
            "severity": severity,
            "timestamp": time.time()
        })

    return {
        "status": "ingested",
        "event_id": event.id,
        "anomaly_score": round(anomaly_score, 4),
        "is_anomaly": is_anomaly
    }

@app.post("/analyze")
def analyze_rag(req: AnalyzeRequest):
    start_time = time.time()
    evt = next((e for e in EVENTS_DB if e["id"] == req.event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail=f"Event ID {req.event_id} not found in buffer")

    # Qdrant-style semantic/keyword RAG search
    matched_kb = []
    cmd_full = evt["binary_path"] + " " + " ".join(evt["command_args"])

    for kb in SECURITY_KNOWLEDGE_BASE:
        relevance = 0.0
        for pattern in kb["pattern"]:
            if pattern in cmd_full:
                relevance += 0.5
        if kb["category"] == "unauthorized_network_egress" and evt["event_type"] == "network":
            relevance += 0.4
        if relevance > 0:
            matched_kb.append({
                "kb_item": kb,
                "relevance_score": min(relevance, 1.0)
            })

    matched_kb.sort(key=lambda x: x["relevance_score"], reverse=True)
    results = matched_kb[:req.top_k]

    ANALYSIS_DURATION_HISTOGRAM.observe(time.time() - start_time)

    return {
        "event_id": req.event_id,
        "event_summary": {
            "binary_path": evt["binary_path"],
            "command_args": evt["command_args"],
            "pod_name": evt["pod_name"],
            "anomaly_score": evt.get("anomaly_score", 0.0)
        },
        "rag_matches": results
    }

@app.post("/explain")
def explain_anomaly(req: ExplainRequest):
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama3.1")

    prompt = (
        f"You are PASHA-X AI Security Brain. Analyze the following eBPF syscall anomaly event:\n"
        f"Event ID: {req.event_id}\n"
        f"Anomaly Score: {req.anomaly_score:.2f}\n"
        f"Context: {req.rag_context}\n\n"
        f"Provide a 3-sentence root cause explanation, security risk impact, and recommended zero-trust remediation action."
    )

    try:
        response = httpx.post(
            f"{ollama_url}/api/generate",
            json={"model": model_name, "prompt": prompt, "stream": False},
            timeout=3.0
        )
        if response.status_code == 200:
            explanation = response.json().get("response", "")
            return {
                "event_id": req.event_id,
                "engine": f"Ollama {model_name}",
                "explanation": explanation
            }
    except Exception:
        pass

    # Deterministic high-precision fallback when Ollama offline
    kb_matches = req.rag_context.get("rag_matches", [])
    top_match = kb_matches[0]["kb_item"] if kb_matches else None
    title = top_match["title"] if top_match else "Unusual Syscall Pattern"
    recommendation = top_match["recommendation"] if top_match else "Trigger zero-trust verification and restart pod."

    fallback_explanation = (
        f"CRITICAL ANOMALY EXPLANATION [{req.event_id}]: "
        f"Detected threat pattern matching '{title}' with anomaly confidence {req.anomaly_score:.2f}. "
        f"Action required: {recommendation}"
    )

    return {
        "event_id": req.event_id,
        "engine": "PASHA-X AI-Brain Fallback Engine",
        "explanation": fallback_explanation
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
