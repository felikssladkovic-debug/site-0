#!/usr/bin/env bash
set -euo pipefail

METHOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$METHOD_DIR/.." && pwd)"
PROJECT_DIR="$ROOT_DIR/project--site-0"

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
scope: method
status: $status
created_at: "$created_at"
finished_at: "$finished_at"
source_root: "$ROOT_DIR"
method_dir: "$METHOD_DIR"
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
      --exclude='./method/.evo-method/runs' \
      --exclude='./meta/.evo-meta/runs' \
      --exclude='./project--site-0/.evo/runs' \
      --exclude='./project--site-0/generated' \
      -cf - .
  ) | (
    cd "$workspace"
    tar -xf -
  )
}

run_smoke_in_workspace() {
  echo "[smoke] check-document-metadata-header"
  bash ./method/evo-method.sh check-document-metadata-header

  echo "[smoke] test"
  bash ./method/evo-method.sh test

  echo "[smoke] spec-to-code via fake-llm"
  PROJECT_EVO_LLM_COMMAND="python3 $PWD/method/tools/fake-llm.py" bash ./method/evo-method.sh spec-to-code --project-dir ./project--site-0

  echo "[smoke] generated/index.html exists"
  if [[ ! -f "project--site-0/generated/index.html" ]]; then
    echo "ERROR: smoke check failed: generated/index.html does not exist" >&2
    exit 1
  fi

  echo "smoke OK"
}

keep_workspace="false"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep-workspace)
      keep_workspace="true"
      shift
      ;;
    *)
      echo "ERROR: unknown smoke option: $1" >&2
      exit 2
      ;;
  esac
done

run_id="$(make_run_id)"
runs_root="$METHOD_DIR/.evo-method/runs"
run_dir="$runs_root/$run_id"
workspace="$run_dir/workspace"
log_dir="$run_dir/logs"
log_file="$log_dir/smoke.log"
created_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"

mkdir -p "$log_dir"
write_run_yaml "$run_dir" "$run_id" "running" "present" "$created_at" "" "$workspace"

echo "[smoke] run_id: $run_id"
echo "[smoke] run_dir: $run_dir"

copy_root_to_workspace "$workspace"

status="success"
set +e
(
  cd "$workspace"
  run_smoke_in_workspace
) > "$log_file" 2>&1
exit_code=$?
set -e
cat "$log_file"

finished_at="$(date '+%Y-%m-%dT%H:%M:%S%z')"

if [[ $exit_code -ne 0 ]]; then
  status="failed"
  write_run_yaml "$run_dir" "$run_id" "$status" "present" "$created_at" "$finished_at" "$workspace"
  echo "[smoke] FAILED"
  echo "[smoke] workspace kept for inspection: $workspace"
  echo "[smoke] log: $log_file"
  exit "$exit_code"
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
