"""Comprehensive Unit & Integration Test Suite for NAYEEM-FLOW-OS 5-Layer Security Engine."""

from fastapi.testclient import TestClient

from api.main import app
from security_engine import (
    DependencyScanner,
    DriftRemediator,
    FairnessChecker,
    ImageScanner,
    KyvernoEngine,
    OPAGatekeeper,
    SASTScanner,
    SealedSecretsManager,
    VaultESOManager,
)

client = TestClient(app)


def test_sast_scanner_clean():
    """Test SAST scanner with clean code snippet."""
    scanner = SASTScanner()
    res = scanner.scan_code_repository(
        code_snippet="def add(a, b):\n    return a + b\n"
    )
    assert res["status"] == "COMPLETED"
    assert res["issues"] == 0
    assert res["score"] == 9.8
    assert res["secrets"]["found"] == 0


def test_sast_scanner_secret_detection():
    """Test SAST scanner detecting secrets and code injection."""
    scanner = SASTScanner()
    res = scanner.scan_code_repository(
        code_snippet="secret_key='supersecret'\neval('2+2')\n"
    )
    assert res["status"] == "COMPLETED"
    assert res["issues"] == 2
    assert res["secrets"]["found"] == 1
    assert res["score"] < 9.8


def test_dependency_scanner():
    """Test dependency scanner on requirements.txt."""
    scanner = DependencyScanner()
    res = scanner.scan_requirements("requirements.txt")
    assert res["status"] == "COMPLETED"
    assert res["vulns"] == 0
    assert res["critical"] == 0
    assert "Trivy" in res["scanners_used"]


def test_image_scanner():
    """Test container image scanner and Cosign signer."""
    scanner = ImageScanner("nayeem-flow-os:v1.2.3")
    res = scanner.scan_image()
    assert res["status"] == "COMPLETED"
    assert res["image"] == "nayeem-flow-os:v1.2.3"
    assert res["cves"] == 0
    assert res["signed"] is True
    assert res["sbom_generated"] is True


def test_opa_gatekeeper_15_policies():
    """Test OPA Gatekeeper evaluating 15 policies."""
    opa = OPAGatekeeper()
    res = opa.evaluate_manifest()
    assert res["passed"] == 15
    assert res["failed"] == 0
    assert len(res["policies"]) == 15
    assert res["violations"] == []


def test_opa_gatekeeper_violations():
    """Test OPA Gatekeeper detecting manifest violations."""
    opa = OPAGatekeeper()
    manifest = (
        "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n "
        " name: test\nspec:\n  containers:\n  - name: app\n   "
        " image: myapp:latest\n    securityContext:\n      privileged: true\n"
    )
    res = opa.evaluate_manifest(manifest)
    assert res["failed"] == 2
    assert res["passed"] == 13
    assert len(res["violations"]) == 2


def test_kyverno_engine_12_policies():
    """Test Kyverno engine evaluating 12 policies."""
    kyv = KyvernoEngine()
    res = kyv.evaluate_manifest()
    assert res["passed"] == 12
    assert res["failed"] == 0
    assert len(res["policies"]) == 12


def test_sealed_secrets_manager():
    """Test Sealed Secrets encryption mock."""
    sealed_mgr = SealedSecretsManager()
    res = sealed_mgr.seal_secret("db-password", "supersecret123")
    assert res["status"] == "SEALED"
    assert res["encrypted"] is True
    assert "SEALED" in res["sealed_payload"]
    assert sealed_mgr.get_sealed_secrets_count() == 8


def test_vault_eso_manager():
    """Test Vault & External Secrets Operator manager status and rotation."""
    vault_mgr = VaultESOManager()
    status = vault_mgr.get_status()
    assert status["vault"] == "healthy"
    assert status["eso_sync"] == "active"
    assert status["sealed_secrets"] == 8
    assert status["rotation_due"] == "in 5 days"
    assert len(status["secrets_inventory"]) == 8

    rot_res = vault_mgr.rotate_secret("db-password")
    assert rot_res["status"] == "SUCCESS"


def test_drift_remediator():
    """Test runtime drift detection and auto-remediation engine."""
    drift = DriftRemediator()
    res = drift.check_cluster_drift()
    assert res["detected"] is False
    assert res["last"] is None
    assert res["auto_remediate"] == "Active"


def test_fairness_checker():
    """Test AI model fairness parity and data drift checker."""
    fairness = FairnessChecker()
    res = fairness.evaluate_model_fairness()
    assert res["fairness"]["bias"] == 0.02
    assert res["fairness"]["status"] == "passed"
    assert res["data_drift"] == 0.01


def test_api_security_scan_endpoint():
    """Test POST /security/scan REST endpoint."""
    resp = client.post("/security/scan", json={"code_repo": "."})
    assert resp.status_code == 200
    data = resp.json()
    assert "sast" in data
    assert data["sast"]["issues"] == 0
    assert data["sast"]["score"] == 9.8
    assert data["deps"]["vulns"] == 0
    assert data["deps"]["critical"] == 0
    assert data["secrets"]["found"] == 0
    assert data["image"]["cves"] == 0
    assert data["image"]["signed"] is True


def test_api_security_policy_check_endpoint():
    """Test POST /security/policy/check REST endpoint."""
    resp = client.post("/security/policy/check", json={"k8s_manifest": ""})
    assert resp.status_code == 200
    data = resp.json()
    assert data["opa"]["passed"] == 15
    assert data["opa"]["failed"] == 0
    assert data["opa"]["violations"] == []
    assert data["kyverno"]["passed"] == 12
    assert data["kyverno"]["failed"] == 0


def test_api_security_secrets_status_endpoint():
    """Test GET /security/secrets/status REST endpoint."""
    resp = client.get("/security/secrets/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["vault"] == "healthy"
    assert data["eso_sync"] == "active"
    assert data["sealed_secrets"] == 8
    assert data["rotation_due"] == "in 5 days"
    assert data["last_rotation"] == "2026-09-01"


def test_api_security_runtime_check_endpoint():
    """Test POST /security/runtime/check REST endpoint."""
    resp = client.post("/security/runtime/check")
    assert resp.status_code == 200
    data = resp.json()
    assert data["drift"]["detected"] is False
    assert data["drift"]["last"] is None
    assert data["fairness"]["bias"] == 0.02
    assert data["fairness"]["status"] == "passed"
    assert data["data_drift"] == 0.01
