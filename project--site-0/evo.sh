#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/.." && pwd)"
METHOD_DIR="${PROJECT_EVO_METHOD_DIR:-$ROOT_DIR/method}"

show_help() {
  cat <<EOF_HELP
project-evo application project CLI

Usage:
  ./evo.sh help
  ./evo.sh spec-to-code

Commands:
  help
      Show this help.

  spec-to-code
      Generate code for this application project.
EOF_HELP
}

case "${1:-help}" in
  help|-h|--help)
    show_help
    ;;
  spec-to-code)
    shift || true
    exec "$PROJECT_DIR/evo/spec-to-code.sh" "$@"
    ;;
  *)
    echo "ERROR: unknown project command: $1" >&2
    show_help
    exit 2
    ;;
esac
