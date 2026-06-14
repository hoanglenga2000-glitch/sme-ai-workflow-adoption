#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$AGENT_DIR/.." && pwd)"
cd "$REPO_ROOT"

python3 -m venv .venv-gpu
source .venv-gpu/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "=== Python ==="
python --version
echo "=== Optional CUDA / NVIDIA ==="
nvidia-smi || true
echo "=== Data hash audit ==="
python "$AGENT_DIR/agent_tools/audit_data_file.py" --manifest-audit
echo "Bootstrap complete. Use: source .venv-gpu/bin/activate"
