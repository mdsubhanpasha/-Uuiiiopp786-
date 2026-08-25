#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Deploying Monitoring Stack (kube-prometheus-stack)"
echo "=================================================="

# Create monitoring namespace if it doesn't exist
kubectl apply -f monitoring/namespace.yaml

# Add prometheus-community helm repository
echo "[+] Adding Helm repo: prometheus-community..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install or Upgrade kube-prometheus-stack
echo "[+] Deploying kube-prometheus-stack release..."
helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword="admin" \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false

# Apply Application ServiceMonitor & Custom Alert Rules
echo "[+] Applying ServiceMonitor and PrometheusRules manifests..."
kubectl apply -f monitoring/service-monitor.yaml --namespace monitoring
kubectl apply -f monitoring/alerts/app-alerts.yaml --namespace monitoring

echo "=================================================="
echo " Validation & Access Instructions"
echo "=================================================="
echo "1. Verify monitoring pods status:"
echo "   kubectl get pods -n monitoring"
echo ""
echo "2. Port-forward Prometheus UI:"
echo "   kubectl port-forward -n monitoring svc/prometheus-stack-kube-prometheus-prometheus 9090:9090 &"
echo "   Access Prometheus UI: http://localhost:9090"
echo ""
echo "3. Port-forward Grafana UI:"
echo "   kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80 &"
echo "   Access Grafana UI: http://localhost:3000 (User: admin / Pass: admin)"
echo "=================================================="
