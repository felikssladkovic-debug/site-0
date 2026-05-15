#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METHOD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$METHOD_ROOT/.." && pwd)"

chmod +x "$METHOD_ROOT"/*.sh || true
find "$METHOD_ROOT" -type f -name "*.sh" -exec chmod +x {} \;

META_ROOT="$REPO_ROOT/meta"
if [ -d "$META_ROOT" ]; then
  chmod +x "$META_ROOT"/*.sh || true
  find "$META_ROOT" -type f -name "*.sh" -exec chmod +x {} \;
fi

echo "chmod OK"
