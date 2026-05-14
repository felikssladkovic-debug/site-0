#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$ROOT_DIR/project--site-0"

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
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

set -- "${ARGS[@]}"

show_help() {
  cat <<EOF
project-evo-method v0

Usage:
  ./evo-root.sh help
  ./evo-root.sh check-document-metadata-header
  ./evo-root.sh spec-to-code [--project-dir <project-dir>]
  ./evo-root.sh test
  ./evo-root.sh test check-document-metadata-header
  ./evo-root.sh test spec-to-code

Project-local usage:
  cd project--site-0
  ./evo.sh spec-to-code

Commands:
  help
      Show this help.

  check-document-metadata-header
      Validate that method documents in /method have valid v1 metadata headers.

  spec-to-code
      Generate code for the selected project workspace.

  test
      Run all tests, or tests for one tool.

Options:
  --project-dir <project-dir>
      Project workspace directory.
      Defaults to: project--site-0

Environment:
  PROJECT_EVO_LLM_COMMAND
      Command used by spec-to-code.py as text-only LLM executor.
      It must read prompt from stdin and write project-evo-file blocks to stdout.
EOF
}


run_check_document_metadata_header() {
  python3 "$ROOT_DIR/meta/tools/check-document-metadata-header.py" \
    --method-dir "$ROOT_DIR/method"
}

run_spec_to_code() {
  python3 "$ROOT_DIR/method/tools/spec-to-code.py" \
    --project-dir "$PROJECT_DIR"
}

run_test_check_document_metadata_header() {
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-1-required-headers.py"
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-2-no-other-headers.py"
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-3-ids-are-uniq.py"
}

run_test_spec_to_code() {
  python3 "$ROOT_DIR/method/tests/spec-to-code/test-1-fails-if-no-project.py"
  python3 "$ROOT_DIR/method/tests/spec-to-code/test-2-fails-if-no-llm-command.py"
  python3 "$ROOT_DIR/method/tests/spec-to-code/test-3-applies-create-file-block.py"
  python3 "$ROOT_DIR/method/tests/spec-to-code/test-4-rejects-path-traversal.py"
}

run_all_tests() {
  run_test_check_document_metadata_header
  run_test_spec_to_code
}

case "${1:-help}" in
  help|-h|--help)
    show_help
    ;;
  check-document-metadata-header)
    run_check_document_metadata_header
    ;;
  spec-to-code)
    run_spec_to_code
    ;;
  test)
    case "${2:-all}" in
      all)
        run_all_tests
        ;;
      check-document-metadata-header)
        run_test_check_document_metadata_header
        ;;
      spec-to-code)
        run_test_spec_to_code
        ;;
      *)
        echo "ERROR: unknown test target: $2" >&2
        show_help
        exit 2
        ;;
    esac
    ;;
  *)
    echo "ERROR: unknown command: $1" >&2
    show_help
    exit 2
    ;;
esac