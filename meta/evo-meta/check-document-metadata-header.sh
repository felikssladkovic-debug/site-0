#!/usr/bin/env bash
set -euo pipefail

META_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$META_DIR/tools/check-document-metadata-header.py" "$@"
