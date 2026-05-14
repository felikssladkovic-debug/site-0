#!/usr/bin/env bash
set -euo pipefail

PROMPT="$(cat)"

codex \
  --ask-for-approval never \
  exec \
  --sandbox read-only \
  --skip-git-repo-check \
  - <<< "$PROMPT"