#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

REPO_NAME="$(basename "$ROOT_DIR")"
HEAD_SHA="$(git rev-parse --short HEAD)"
LOG_PATH="docs/derivations/main.log"
PATTERN="Undefined control sequence|LaTeX Error|Fatal error|Emergency stop|^!"

make compile

if [[ ! -f "$LOG_PATH" ]]; then
  echo "[FAIL] $REPO_NAME latex gate: missing log at $LOG_PATH"
  exit 1
fi

TMP_HITS="$(mktemp)"
if grep -En "$PATTERN" "$LOG_PATH" >"$TMP_HITS"; then
  echo "[FAIL] $REPO_NAME latex gate: fatal patterns found in $LOG_PATH"
  cat "$TMP_HITS"
  rm -f "$TMP_HITS"
  exit 1
fi
rm -f "$TMP_HITS"

echo "[PASS] $REPO_NAME latex gate @ $HEAD_SHA"
