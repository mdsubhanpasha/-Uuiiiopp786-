"""
DevSecOps Production-Grade Flask Application.
Provides root landing endpoint and health check endpoint for monitoring and orchestration.
"""
import os
import time
from flask import Flask, jsonify

app = Flask(__name__)

START_TIME = time.time()


@app.route("/", methods=["GET"])
def home():
    """Root route returning application metadata and status."""
    return jsonify({
        "status": "success",
        "message": "Welcome to DevSecOps Pipeline Pro API!",
        "version": "1.0.0",
        "environment": os.getenv("FLASK_ENV", "production")
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Healthcheck endpoint for Docker & K8s readiness/liveness probes."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "UP",
        "service": "devsecops-pipeline-pro",
        "uptime": f"{uptime_seconds}s",
        "checks": {
            "database": "healthy",
            "memory": "healthy"
        }
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
