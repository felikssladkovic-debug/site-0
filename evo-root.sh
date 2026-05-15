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
  cat <<EOF_HELP
project-evo-method foundation-00-minimal

Usage:
  ./evo-root.sh help
  ./evo-root.sh check-document-metadata-header
  ./evo-root.sh spec-to-code [--project-dir <project-dir>]
  ./evo-root.sh smoke [--keep-workspace]
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

  smoke
      Run the minimal foundation smoke check using fake-llm in a managed run workspace.
      By default, the workspace is deleted on success and kept on failure.

  test
      Run all tests, or tests for one tool.

Options:
  --project-dir <project-dir>
      Project workspace directory.
      Defaults to: project--site-0

  --keep-workspace
      For smoke only: keep the run workspace even after a successful run.

Environment:
  PROJECT_EVO_LLM_COMMAND
      Command used by spec-to-code.py as text-only LLM executor.
      It must read prompt from stdin and write project-evo-file blocks to stdout.
EOF_HELP
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

make_run_id() {
  python3 - <<'PY'
from datetime import datetime
from uuid import uuid4
print(f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}-smoke-{uuid4().hex[:8]}")
PY
}

write_run_yaml() {
  local run_dir="$1"
  local run_id="$2"
  local status="$3"
  local workspace_state="$4"
  local created_at="$5"
  local finished_at="$6"
  local workspace_path="$7"

  cat > "$run_dir/run.yaml" <<EOF_RUN
id: $run_id
command: smoke
status: $status
created_at: "$created_at"
finished_at: "$finished_at"
source_root: "$ROOT_DIR"
workspace: "$workspace_path"
workspace_state: $workspace_state
cleanup_policy: delete_on_success_keep_on_failure
log: "$run_dir/logs/smoke.log"
EOF_RUN
}

copy_root_to_workspace() {
  local workspace="$1"
  mkdir -p "$workspace"

  (
    cd "$ROOT_DIR"
    tar \
      --exclude='./.git' \
      --exclude='./.project-evo' \
      --exclude='./project--site-0/generated' \
      -cf - .
  ) | (
    cd "$workspace"
    tar -xf -
  )
}

run_smoke_in_current_root() {
  echo "[smoke] check-document-metadata-header"
  bash ./evo-root.sh check-document-metadata-header

  echo "[smoke] test"
  bash ./evo-root.sh test

  echo "[smoke] spec-to-code via fake-llm"
  PROJECT_EVO_LLM_COMMAND="python3 $PWD/method/tools/fake-llm.py" bash ./evo-root.sh spec-to-code

  echo "[smoke] generated/index.html exists"
  if [[ ! -f "project--site-0/generated/index.html" ]]; then
    echo "ERROR: smoke check failed: generated/index.html does not exist" >&2
    exit 1
  fi

  echo "smoke OK"
}

run_smoke() {
  local keep_workspace="false"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --keep-workspace)
        keep_workspace="true"
        shift
        ;;
      *)
        echo "ERROR: unknown smoke option: $1" >&2
        show_help
        exit 2
        ;;
    esac
  done

  local run_id
  run_id="$(make_run_id)"

  local runs_root="$ROOT_DIR/.project-evo/runs"
  local run_dir="$runs_root/$run_id"
  local workspace="$run_dir/workspace"
  local log_dir="$run_dir/logs"
  local log_file="$log_dir/smoke.log"
  local created_at
  created_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"

  mkdir -p "$log_dir"
  write_run_yaml "$run_dir" "$run_id" "running" "present" "$created_at" "" "$workspace"

  echo "[smoke] run_id: $run_id"
  echo "[smoke] run_dir: $run_dir"

  copy_root_to_workspace "$workspace"

  local status="success"
  set +e
  (
    cd "$workspace"
    run_smoke_in_current_root
  ) > >(tee "$log_file") 2> >(tee -a "$log_file" >&2)
  local exit_code=$?
  set -e

  local finished_at
  finished_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"

  if [[ $exit_code -ne 0 ]]; then
    status="failed"
    write_run_yaml "$run_dir" "$run_id" "$status" "present" "$created_at" "$finished_at" "$workspace"
    echo "[smoke] FAILED"
    echo "[smoke] workspace kept for inspection: $workspace"
    echo "[smoke] log: $log_file"
    return "$exit_code"
  fi

  if [[ "$keep_workspace" == "true" ]]; then
    write_run_yaml "$run_dir" "$run_id" "$status" "present" "$created_at" "$finished_at" "$workspace"
    echo "[smoke] workspace kept: $workspace"
  else
    rm -rf "$workspace"
    write_run_yaml "$run_dir" "$run_id" "$status" "deleted" "$created_at" "$finished_at" "$workspace"
    echo "[smoke] workspace deleted after success"
  fi

  echo "[smoke] log: $log_file"
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
  smoke)
    shift || true
    run_smoke "$@"
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
