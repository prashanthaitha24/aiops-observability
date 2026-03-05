#!/usr/bin/env bash
set -euo pipefail

OTEL_NS="${OTEL_NS:-otel-demo}"
AIOPS_NS="${AIOPS_NS:-aiops}"

echo "Store/Grafana/Jaeger:"
echo "  http://localhost:8080/"
echo "  http://localhost:8080/grafana/"
echo "  http://localhost:8080/jaeger/ui"
echo ""
echo "AIOps Detector:"
echo "  http://localhost:8081/health"
echo "  http://localhost:8081/metrics"
echo ""

kubectl -n "${OTEL_NS}" port-forward svc/frontend-proxy 8080:8080 &
PF1=$!

# Only if aiops-detector exists
if kubectl -n "${AIOPS_NS}" get svc aiops-detector >/dev/null 2>&1; then
  kubectl -n "${AIOPS_NS}" port-forward svc/aiops-detector 8081:8080 &
  PF2=$!
else
  PF2=""
  echo "aiops-detector service not found yet. (Added next.)"
fi

trap 'echo "Stopping port-forwards..."; kill $PF1; if [ -n "${PF2}" ]; then kill $PF2; fi' INT TERM
wait
