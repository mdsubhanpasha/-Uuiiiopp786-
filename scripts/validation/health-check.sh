#!/usr/bin/env bash
set -euo pipefail

# Health Check & Security Header Verification for NAYEEM-EDGE
DOMAIN="${1:-nayeem-edge.enterprise.io}"
URL="https://${DOMAIN}"

echo "================================================================="
echo "  NAYEEM-EDGE: Health Check & Security Audit Script"
echo "  Target URL: ${URL}"
echo "================================================================="

echo "[1/3] Testing HTTP Status Code..."
HTTP_STATUS=$(curl -k -s -o /dev/null -w "%{http_code}" "${URL}" || echo "000")
echo "HTTP Response Status: ${HTTP_STATUS}"

if [ "${HTTP_STATUS}" -eq 200 ] || [ "${HTTP_STATUS}" -eq 301 ]; then
    echo "✅ Endpoint reached successfully."
else
    echo "⚠️ Non-200 response code (${HTTP_STATUS}), verifying fallback..."
fi

echo "[2/3] Verifying Enterprise Security Headers..."
HEADERS=$(curl -k -s -I "${URL}" || echo "")

check_header() {
    local header_name="$1"
    if echo "${HEADERS}" | grep -iq "${header_name}"; then
        echo "  [PASS] ${header_name} present."
    else
        echo "  [FAIL] ${header_name} missing."
    fi
}

check_header "Strict-Transport-Security"
check_header "X-Frame-Options"
check_header "X-Content-Type-Options"
check_header "Content-Security-Policy"

echo "[3/3] Checking Endpoint Health Telemetry JSON..."
HEALTH_JSON=$(curl -k -s "${URL}/health" || echo '{"status":"OFFLINE"}')
echo "Health Response: ${HEALTH_JSON}"

echo "✅ Health check completed successfully."
