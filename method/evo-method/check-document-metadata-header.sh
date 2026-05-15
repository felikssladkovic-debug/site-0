#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$METHOD_DIR/.." && pwd)"

exec "$ROOT_DIR/meta/evo-meta.sh" check-document-metadata-header
