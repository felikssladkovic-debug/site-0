#!/usr/bin/env bash
set -euo pipefail

META_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$META_DIR/.." && pwd)"
METHOD_DIR="$ROOT_DIR/method"

show_help() {
  cat <<EOF_HELP
project-evo meta CLI

Usage:
  ./evo-meta.sh help
  ./evo-meta.sh check-document-metadata-header
  ./evo-meta.sh test check-document-metadata-header
  ./evo-meta.sh test

Commands:
  check-document-metadata-header
      Validate that method documents in /method have valid v1 metadata headers.

  test
      Run meta command tests.
EOF_HELP
}

case "${1:-help}" in
  help|-h|--help)
    show_help
    ;;
  check-document-metadata-header)
    exec "$META_DIR/evo-meta/check-document-metadata-header.sh" --method-dir "$METHOD_DIR"
    ;;
  test)
    case "${2:-all}" in
      all|check-document-metadata-header)
        python3 "$META_DIR/evo-meta/check-document-metadata-header/test-1-required-headers.py"
        python3 "$META_DIR/evo-meta/check-document-metadata-header/test-2-no-other-headers.py"
        python3 "$META_DIR/evo-meta/check-document-metadata-header/test-3-ids-are-uniq.py"
        ;;
      *)
        echo "ERROR: unknown meta test target: $2" >&2
        show_help
        exit 2
        ;;
    esac
    ;;
  *)
    echo "ERROR: unknown meta command: $1" >&2
    show_help
    exit 2
    ;;
esac
