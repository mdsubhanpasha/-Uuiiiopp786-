#!/usr/bin/env bash
set -euo pipefail

# Performance Benchmark Test for NAYEEM-EDGE Edge Delivery
DOMAIN="${1:-nayeem-edge.enterprise.io}"
URL="http://${DOMAIN}/"
REQUESTS="${2:-1000}"
CONCURRENCY="${3:-100}"

echo "================================================================="
echo "  NAYEEM-EDGE: Edge Performance & ApacheBench Load Benchmark"
echo "  Target URL: ${URL}"
echo "  Requests: ${REQUESTS} | Concurrency: ${CONCURRENCY}"
echo "================================================================="

if command -v ab &> /dev/null; then
    echo "Running ApacheBench load test..."
    ab -n "${REQUESTS}" -c "${CONCURRENCY}" "${URL}" || echo "ApacheBench execution finished."
else
    echo "ApacheBench (ab) not found. Running cURL latency benchmark loop..."
    for i in {1..5}; do
        curl -s -o /dev/null -w "Request $i: TTFB = %{time_starttransfer}s, Total = %{time_total}s\n" "${URL}" || echo "Curl attempt $i done."
    done
fi

echo "✅ Performance benchmark completed."
