#!/usr/bin/env bash
set -euo pipefail
CLUSTER_NAME="${CLUSTER_NAME:-aiops-demo}"
kind delete cluster --name "${CLUSTER_NAME}" || true
echo "✅ Cluster deleted."
