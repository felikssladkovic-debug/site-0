#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$METHOD_DIR/.." && pwd)"

run_meta_tests() {
  "$ROOT_DIR/meta/evo-meta.sh" test check-document-metadata-header
}

run_spec_to_code_tests() {
  python3 "$METHOD_DIR/evo-method/spec-to-code/test-1-fails-if-no-project.py"
  python3 "$METHOD_DIR/evo-method/spec-to-code/test-2-fails-if-no-llm-command.py"
  python3 "$METHOD_DIR/evo-method/spec-to-code/test-3-applies-create-file-block.py"
  python3 "$METHOD_DIR/evo-method/spec-to-code/test-4-rejects-path-traversal.py"
}

case "${1:-all}" in
  all)
    run_meta_tests
    run_spec_to_code_tests
    ;;
  check-document-metadata-header)
    run_meta_tests
    ;;
  spec-to-code)
    run_spec_to_code_tests
    ;;
  *)
    echo "ERROR: unknown method test target: $1" >&2
    exit 2
    ;;
esac
