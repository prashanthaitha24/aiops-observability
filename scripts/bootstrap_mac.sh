#!/usr/bin/env bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install it first:"
  echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  exit 1
fi

brew install kind kubectl helm jq yq || true

echo ""
echo "✅ Tools installed. Ensure Docker Desktop is installed and RUNNING."
echo "Next: ./scripts/demo_up.sh"
