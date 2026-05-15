#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$METHOD_DIR/.." && pwd)"
DEFAULT_PROJECT_DIR="$ROOT_DIR/project--site-0"

show_help() {
  cat <<EOF_HELP
project-evo-method foundation-00-minimal

Usage:
  ./evo-method.sh help
  ./evo-method.sh init [--name <project-name>]
  ./evo-method.sh check-document-metadata-header
  ./evo-method.sh spec-to-code [--project-dir <project-dir>]
  ./evo-method.sh smoke [--keep-workspace]
  ./evo-method.sh test
  ./evo-method.sh test check-document-metadata-header
  ./evo-method.sh test spec-to-code

Project-local usage:
  cd project--site-0
  ./evo.sh spec-to-code

Commands:
  init
      Initialize an application project in the current directory.

  check-document-metadata-header
      Validate that method documents in /method have valid v1 metadata headers.

  spec-to-code
      Generate code for the selected project workspace.

  smoke
      Run the minimal foundation smoke check using fake-llm in a managed method run workspace.

  test
      Run all tests, or tests for one command.

Options:
  --project-dir <project-dir>
      Project workspace directory. Defaults to: ../project--site-0 from this method directory.

  --keep-workspace
      For smoke only: keep the run workspace even after a successful run.

Environment:
  PROJECT_EVO_LLM_COMMAND
      Command used by spec-to-code.py as text-only LLM executor.
EOF_HELP
}

PROJECT_DIR="$DEFAULT_PROJECT_DIR"
ARGS=()
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
    chmod)
  exec "$SCRIPT_DIR/evo-method/chmod.sh" "$@"
  ;;

*)
      ARGS+=("$1")
      shift
      ;;
  esac
done
set -- "${ARGS[@]}"

case "${1:-help}" in
  help|-h|--help)
    show_help
    ;;
  init)
    shift || true
    exec "$METHOD_DIR/evo-method/init.sh" "$@"
    ;;
  check-document-metadata-header)
    exec "$METHOD_DIR/evo-method/check-document-metadata-header.sh"
    ;;
  spec-to-code)
    exec "$METHOD_DIR/evo-method/spec-to-code.sh" --project-dir "$PROJECT_DIR"
    ;;
  smoke)
    shift || true
    exec "$METHOD_DIR/evo-method/smoke.sh" "$@"
    ;;
  test)
    shift || true
    exec "$METHOD_DIR/evo-method/test.sh" "$@"
    ;;
  *)
    echo "ERROR: unknown method command: $1" >&2
    show_help
    exit 2
    ;;
esac
