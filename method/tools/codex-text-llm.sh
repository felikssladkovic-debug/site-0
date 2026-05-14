#!/usr/bin/env bash
set -euo pipefail

PROMPT="$(cat)"

codex \
  --sandbox read-only \
  --ask-for-approval never \
  --skip-git-repo-check \
  exec \
  - <<< "$PROMPT"