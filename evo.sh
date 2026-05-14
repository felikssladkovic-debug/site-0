#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
  cat <<'HELP'
project-evo-method v0

Usage:
  ./evo.sh help
  ./evo.sh check-document-metadata-header
  ./evo.sh spec-to-code
  ./evo.sh test
  ./evo.sh test check-document-metadata-header
  ./evo.sh test spec-to-code

Commands:
  help
      Show this help.

  check-document-metadata-header
      Validate that method documents in /method have valid v1 metadata headers.

  spec-to-code
      Generate code for the default project workspace: project--site-0.

  test
      Run all tests, or tests for one tool.

Notes:
  - v0 assumes project--site-0 as the default project.
  - All user-facing commands should go through evo.sh.
HELP
}

run_check_document_metadata_header() {
  python3 "$ROOT_DIR/meta/tools/check-document-metadata-header.py" \
    --method-dir "$ROOT_DIR/method"
}

run_spec_to_code() {
  python3 "$ROOT_DIR/method/tools/spec-to-code.py" \
    --project-dir "$ROOT_DIR/project--site-0"
}

run_test_check_document_metadata_header() {
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-1-required-headers.py"
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-2-no-other-headers.py"
  python3 "$ROOT_DIR/meta/tests/check-document-metadata-header/test-3-ids-are-uniq.py"
}

run_test_spec_to_code() {
  python3 "$ROOT_DIR/method/tests/spec-to-code/test-1-fails-if-no-project.py"
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
        echo "Unknown test target: $2" >&2
        show_help
        exit 2
        ;;
    esac
    ;;
  *)
    echo "Unknown command: $1" >&2
    show_help
    exit 2
    ;;
esac
