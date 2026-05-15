#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/.." && pwd)"
METHOD_DIR="${PROJECT_EVO_METHOD_DIR:-$ROOT_DIR/method}"

export PROJECT_EVO_LLM_COMMAND="${PROJECT_EVO_LLM_COMMAND:-$METHOD_DIR/tools/codex-text-llm.sh}"

python3 "$METHOD_DIR/tools/spec-to-code.py" --project-dir "$PROJECT_DIR"
