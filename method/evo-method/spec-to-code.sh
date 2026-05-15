#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --project-dir requires a value" >&2
        exit 2
      fi
      PROJECT_DIR="$(cd "$2" && pwd)"
      shift 2
      ;;
    *)
      echo "ERROR: unknown spec-to-code option: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$PROJECT_DIR" ]]; then
  echo "ERROR: --project-dir is required" >&2
  exit 2
fi

python3 "$METHOD_DIR/tools/spec-to-code.py" --project-dir "$PROJECT_DIR"
