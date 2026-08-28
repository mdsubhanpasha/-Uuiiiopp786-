# డైరెక్టరీలు క్రియేట్ చేయడం
mkdir -p scripts monitoring/datasources

# 1. Loki డెవలప్‌మెంట్ స్క్రిప్ట్ రాయడం
cat << 'EOF' > scripts/deploy-logging.sh
#!/usr/bin/env bash
set -e
echo "=== Deploying Enterprise PLG Stack (Loki + Promtail) ==="
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm upgrade --install loki-stack grafana/loki-stack \
  --namespace monitoring \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=10Gi
echo "=== Loki & Promtail Stack Successfully Deployed ==="
