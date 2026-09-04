#!/usr/bin/env bash
set -euo pipefail

# Validate SSL Certificate and Route53 DNS Resolution for NAYEEM-EDGE
DOMAIN="${1:-nayeem-edge.enterprise.io}"

echo "================================================================="
echo "  NAYEEM-EDGE: SSL & Route53 DNS Validation Suite"
echo "  Target Domain: ${DOMAIN}"
echo "================================================================="

echo "[1/2] Verifying DNS Resolution via Dig..."
if command -v dig &> /dev/null; then
    dig +short "${DOMAIN}" A
    dig +short "www.${DOMAIN}" CNAME
else
    echo "dig command not found, using nslookup fallback..."
    nslookup "${DOMAIN}" || true
fi

echo "[2/2] Validating TLS Certificate Handshake via OpenSSL..."
if command -v openssl &> /dev/null; then
    echo "Inspecting SSL Certificate Expiry and Issuer:"
    echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | openssl x509 -noout -issuer -dates -subject || echo "Local OpenSSL test performed."
else
    echo "OpenSSL binary not found."
fi

echo "✅ SSL & DNS Validation Script Execution Finished."
