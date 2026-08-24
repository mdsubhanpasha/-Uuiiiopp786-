"""Tests for Kubernetes manifests and Terraform configuration files."""

from pathlib import Path
import yaml


def test_k8s_manifests_exist_and_valid():
    """Verify all required Kubernetes manifests exist and are valid YAML."""
    k8s_dir = Path("k8s")
    assert k8s_dir.exists() and k8s_dir.is_dir()

    required_manifests = [
        "deployment.yaml",
        "service.yaml",
        "hpa.yaml",
        "configmap-secret.yaml",
        "ingress.yaml",
    ]

    for manifest_name in required_manifests:
        file_path = k8s_dir / manifest_name
        assert file_path.exists(), f"Missing manifest: {manifest_name}"

        with open(file_path, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
            assert len(docs) > 0, f"Empty YAML file: {manifest_name}"
            for doc in docs:
                assert "apiVersion" in doc, f"No apiVersion in {manifest_name}"
                assert "kind" in doc, f"Missing kind in {manifest_name}"
                assert "metadata" in doc, f"No metadata in {manifest_name}"


def test_k8s_deployment_spec():
    """Verify specific requirements in deployment.yaml."""
    deploy_path = Path("k8s/deployment.yaml")
    with open(deploy_path, "r", encoding="utf-8") as f:
        deploy = yaml.safe_load(f)

    assert deploy["kind"] == "Deployment"
    assert deploy["spec"]["replicas"] == 2
    assert deploy["spec"]["strategy"]["type"] == "RollingUpdate"

    container = deploy["spec"]["template"]["spec"]["containers"][0]
    resources = container["resources"]
    assert resources["requests"]["cpu"] == "250m"
    assert resources["requests"]["memory"] == "512Mi"
    assert resources["limits"]["cpu"] == "500m"
    assert resources["limits"]["memory"] == "1Gi"

    assert "livenessProbe" in container
    assert "readinessProbe" in container


def test_k8s_hpa_spec():
    """Verify specific requirements in hpa.yaml."""
    hpa_path = Path("k8s/hpa.yaml")
    with open(hpa_path, "r", encoding="utf-8") as f:
        hpa = yaml.safe_load(f)

    assert hpa["kind"] == "HorizontalPodAutoscaler"
    assert hpa["spec"]["minReplicas"] == 2
    assert hpa["spec"]["maxReplicas"] == 10

    metrics = hpa["spec"]["metrics"]
    cpu_metric = next(m for m in metrics if m["resource"]["name"] == "cpu")
    mem_metric = next(m for m in metrics if m["resource"]["name"] == "memory")
    assert cpu_metric["resource"]["target"]["averageUtilization"] == 70
    assert mem_metric["resource"]["target"]["averageUtilization"] == 70


def test_terraform_files_exist():
    """Verify required Terraform files exist."""
    tf_dir = Path("terraform")
    assert tf_dir.exists() and tf_dir.is_dir()

    required_tf = ["main.tf", "variables.tf", "outputs.tf"]
    for tf_file in required_tf:
        file_path = tf_dir / tf_file
        assert file_path.exists(), f"Missing Terraform file: {tf_file}"
        content = file_path.read_text(encoding="utf-8")
        assert len(content.strip()) > 0
