#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/.." && pwd)"

export PROJECT_EVO_LLM_COMMAND="${PROJECT_EVO_LLM_COMMAND:-$ROOT_DIR/method/tools/codex-text-llm.sh}"

exec "$ROOT_DIR/evo-root.sh" "$@" --project-dir "$PROJECT_DIR"