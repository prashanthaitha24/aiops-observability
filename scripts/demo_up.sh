#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-aiops-demo}"
OTEL_NS="${OTEL_NS:-otel-demo}"
AIOPS_NS="${AIOPS_NS:-aiops}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop and retry."
  exit 1
fi

echo "==> kind cluster: ${CLUSTER_NAME}"
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "${CLUSTER_NAME}" --config "${ROOT_DIR}/deploy/kind/kind-config.yaml"
else
  echo "kind cluster already exists"
fi

echo "==> OpenTelemetry Helm repo"
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

kubectl get ns "${OTEL_NS}" >/dev/null 2>&1 || kubectl create namespace "${OTEL_NS}"

if helm -n "${OTEL_NS}" status my-otel-demo >/dev/null 2>&1; then
  echo "otel demo already installed"
else
  helm install my-otel-demo open-telemetry/opentelemetry-demo -n "${OTEL_NS}"
fi

kubectl get ns "${AIOPS_NS}" >/dev/null 2>&1 || kubectl create namespace "${AIOPS_NS}"

# aiops-detector helm chart (we’ll add in Step 2)
if [ -d "${ROOT_DIR}/deploy/helm/aiops-detector" ]; then
  if helm -n "${AIOPS_NS}" status aiops-detector >/dev/null 2>&1; then
    echo "aiops-detector already installed"
  else
    helm install aiops-detector "${ROOT_DIR}/deploy/helm/aiops-detector" -n "${AIOPS_NS}"
  fi
else
  echo "NOTE: deploy/helm/aiops-detector not found yet (will be added next)."
fi

echo ""
echo "✅ Demo up."
echo "Next: ./scripts/demo_portforward.sh"
