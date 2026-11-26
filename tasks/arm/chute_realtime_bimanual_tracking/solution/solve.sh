#!/usr/bin/env bash
# Privileged synthetic reference: copies terminal snapshots, never runs a controller.
# See tests/README.md. This verifies the scoring path, NOT physical task feasibility.
set -euo pipefail
SUB="${ALE_HOME:-/home/user}/submission"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$SUB"
cp "$HERE/privileged/ideal_answer.json" "$SUB/ideal_answer.json"
cp "$HERE/privileged/oracle_token" "$SUB/.oracle_token"
echo "[oracle] synthetic ideal-answer fixture ready; no physical rollout" >&2
