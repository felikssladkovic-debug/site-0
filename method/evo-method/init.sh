#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$(pwd)"
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --name requires a value" >&2
        exit 2
      fi
      PROJECT_NAME="$2"
      shift 2
      ;;
    *)
      echo "ERROR: unknown init option: $1" >&2
      exit 2
      ;;
  esac
done

is_inside_allowed_run_workspace() {
  local path="$1"
  case "$path" in
    */.evo-method/runs/*|*/.evo-meta/runs/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

fail_if_marker_in_self_or_parents() {
  local marker="$1"
  local meaning="$2"
  local current="$TARGET_DIR"

  while true; do
    if [[ -d "$current/$marker" ]]; then
      if [[ "$marker" != ".evo" ]] && is_inside_allowed_run_workspace "$TARGET_DIR"; then
        :
      else
        echo "ERROR: cannot init project inside $meaning: found $current/$marker" >&2
        exit 1
      fi
    fi

    if [[ "$current" == "/" ]]; then
      break
    fi
    current="$(dirname "$current")"
  done
}

fail_if_marker_in_self_or_parents ".evo" "an application project"
fail_if_marker_in_self_or_parents ".evo-method" "a method service area"
fail_if_marker_in_self_or_parents ".evo-meta" "a meta service area"

if [[ -e "$TARGET_DIR/meta" || -e "$TARGET_DIR/method" ]]; then
  echo "ERROR: cannot init project in a directory that contains meta/ or method/" >&2
  exit 1
fi

base_name="$(basename "$TARGET_DIR")"
default_name="$base_name"
if [[ "$base_name" == project--* ]]; then
  default_name="${base_name#project--}"
fi

if [[ -z "$PROJECT_NAME" ]]; then
  if [[ -t 0 ]]; then
    printf "Project name [%s]: " "$default_name" >&2
    read -r PROJECT_NAME
    PROJECT_NAME="${PROJECT_NAME:-$default_name}"
  else
    PROJECT_NAME="$default_name"
  fi
fi

if [[ -z "$PROJECT_NAME" ]]; then
  echo "ERROR: project name must not be empty" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR/.evo/runs" "$TARGET_DIR/spec" "$TARGET_DIR/generated" "$TARGET_DIR/evo"
cat > "$TARGET_DIR/.evo/project.yaml" <<EOF_PROJECT
name: $PROJECT_NAME
kind: application-project
method: project-evo-method
EOF_PROJECT
: > "$TARGET_DIR/.evo/runs/.gitkeep"

if [[ ! -f "$TARGET_DIR/spec/index.md" ]]; then
  cat > "$TARGET_DIR/spec/index.md" <<EOF_SPEC
# $PROJECT_NAME Spec

## Purpose

Describe the application project here.
EOF_SPEC
fi

cat > "$TARGET_DIR/evo/spec-to-code.sh" <<'EOF_SPEC_TO_CODE'
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$PROJECT_DIR/.." && pwd)"
METHOD_DIR="${PROJECT_EVO_METHOD_DIR:-__PROJECT_EVO_METHOD_DIR__}"

export PROJECT_EVO_LLM_COMMAND="${PROJECT_EVO_LLM_COMMAND:-$METHOD_DIR/tools/codex-text-llm.sh}"

python3 "$METHOD_DIR/tools/spec-to-code.py" --project-dir "$PROJECT_DIR"
EOF_SPEC_TO_CODE
python3 - "$TARGET_DIR/evo/spec-to-code.sh" "$METHOD_DIR" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
method_dir = sys.argv[2]
text = path.read_text(encoding="utf-8").replace("__PROJECT_EVO_METHOD_DIR__", method_dir)
path.write_text(text, encoding="utf-8")
PY
chmod +x "$TARGET_DIR/evo/spec-to-code.sh"

cat > "$TARGET_DIR/evo.sh" <<'EOF_EVO'
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
  cat <<EOF_HELP
project-evo application project CLI

Usage:
  ./evo.sh help
  ./evo.sh spec-to-code
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
EOF_EVO
chmod +x "$TARGET_DIR/evo.sh"

echo "project init OK: $PROJECT_NAME"
echo "project dir: $TARGET_DIR"
