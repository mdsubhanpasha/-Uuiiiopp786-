#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Deploying PLG Stack (Loki + Promtail Log Pipeline)"
echo "=================================================="

# Ensure monitoring namespace exists
kubectl apply -f monitoring/namespace.yaml

# Add Grafana Helm repository
echo "[+] Adding Grafana Helm repository..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Apply Promtail ConfigMap
echo "[+] Applying Promtail ConfigMap..."
if [ -f "monitoring/promtail-config.yaml" ]; then
  kubectl apply -f monitoring/promtail-config.yaml --namespace monitoring
fi

# Install / Upgrade Loki & Promtail Stack
echo "[+] Deploying / Upgrading Loki & Promtail Helm stack..."
helm upgrade --install loki grafana/loki-stack \
  --namespace monitoring \
  --set loki.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi \
  --set loki.config.table_manager.retention_deletes_enabled=true \
  --set loki.config.table_manager.retention_period=168h \
  --set loki.resources.requests.cpu=100m \
  --set loki.resources.requests.memory=128Mi \
  --set loki.resources.limits.cpu=500m \
  --set loki.resources.limits.memory=512Mi \
  --set promtail.enabled=true \
  --set promtail.config.file=/etc/promtail/promtail.yaml \
  --set promtail.extraVolumes[0].name=promtail-config \
  --set promtail.extraVolumes[0].configMap.name=promtail-config \
  --set promtail.extraVolumeMounts[0].name=promtail-config \
  --set promtail.extraVolumeMounts[0].mountPath=/etc/promtail

# Apply Loki Data Source Provisioning if exists
if [ -f "monitoring/datasources/loki-datasource.yaml" ]; then
  echo "[+] Provisioning Grafana Loki Data Source..."
  kubectl apply -f monitoring/datasources/loki-datasource.yaml --namespace monitoring
fi

echo "=================================================="
echo " PLG Logging Stack Deployment Complete!"
echo "=================================================="
echo "Verify status using:"
echo "  kubectl get pods -n monitoring -l app=loki"
echo "  kubectl get pods -n monitoring -l app=promtail"
echo "=================================================="
