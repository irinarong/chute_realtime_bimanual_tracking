#!/usr/bin/env bash
set -euo pipefail
IMAGE="${1:-chute-task:20261126}"
TASK="${2:-$PWD/candidate/tasks/arm/chute_realtime_bimanual_tracking}"
OUT="${3:-$PWD/docker-smoke-results}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
CID="$(sudo docker run -d --network none --entrypoint /bin/sleep "$IMAGE" infinity)"
trap 'sudo docker rm -f "$CID" >/dev/null' EXIT
sudo docker exec "$CID" bash -c 'mkdir -p /opt/ale; chmod 700 /opt/ale'
sudo docker cp "$TASK" "$CID:/opt/ale/source"
sudo docker cp "$HERE/docker_smoke.py" "$CID:/opt/ale/docker_smoke.py"
set +e
sudo docker exec "$CID" /opt/venv/bin/python /opt/ale/docker_smoke.py > "$OUT/smoke.log" 2>&1
RC=$?
set -e
sudo docker cp "$CID:/tmp/chute-smoke/." "$OUT/" || true
sudo docker image inspect "$IMAGE" > "$OUT/images.json"
cat "$OUT/smoke.log"
exit "$RC"
