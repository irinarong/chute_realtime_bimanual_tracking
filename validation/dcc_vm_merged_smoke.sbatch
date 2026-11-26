#!/bin/bash
#SBATCH --job-name=chute-merged-smoke
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/merged-smoke-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-62721924"
R="$BASE/datasets/merged-smoke-$SLURM_JOB_ID"
S="/tmp/chute-merged-smoke-$SLURM_JOB_ID"
CANDIDATE="${1:?Pass immutable candidate path}"
EXPECTED="${2:?Pass candidate SHA256}"
printf '%s  %s\n' "$EXPECTED" "$CANDIDATE" | sha256sum -c -
LOCK="$D/active-operation.lock"
mkdir "$LOCK" || { echo 'VM disk already owned; refusing concurrent boot' >&2; exit 44; }
printf '%s\n' "$SLURM_JOB_ID" > "$LOCK/job_id"
P=(podman --cgroup-manager cgroupfs --root "$S/root" --runroot "$S/runroot" --storage-driver vfs --storage-opt vfs.ignore_chown_errors=true)
cleanup() {
    local rc=$?
    if [ -n "${VM_PID:-}" ] && kill -0 "$VM_PID" 2>/dev/null; then
        "${P[@]}" stop -t 30 "chute-merged-$SLURM_JOB_ID" >/dev/null 2>&1 || true
        if kill -0 "$VM_PID" 2>/dev/null; then
            echo 'VM still running; retaining ownership lock' >&2
            return 45
        fi
    fi
    if [ -n "${VM_PID:-}" ]; then wait "$VM_PID" || true; fi
    rm -f "$LOCK/job_id"
    rmdir "$LOCK"
    return "$rc"
}
trap cleanup EXIT
mkdir -p "$R" "$S/root" "$S/runroot" "$S/xdg" "$S/tmp"
chmod 700 "$S/xdg"
export XDG_RUNTIME_DIR="$S/xdg" TMPDIR="$S/tmp"
sha256sum "$CANDIDATE" > "$R/candidate.sha256"
QEMU_IMAGE=$(sed -n 's/^QEMU_RUNTIME=//p' "$BASE/logs/docker-vm-62721924.log" | head -n1)
test -n "$QEMU_IMAGE"
"${P[@]}" pull "$QEMU_IMAGE"
PORT=$((22000 + SLURM_JOB_ID % 10000))
"${P[@]}" run --rm --name "chute-merged-$SLURM_JOB_ID" --cgroups disabled --network host --security-opt label=disable --device /dev/kvm -v "$D:$D" --entrypoint qemu-system-x86_64 "$QEMU_IMAGE" \
 -enable-kvm -cpu host -smp 4 -m 16384 -display none \
 -drive "file=$D/ubuntu.img,format=qcow2,if=virtio" \
 -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$PORT-:22" -device virtio-net-pci,netdev=n0 \
 -serial stdio > "$R/qemu.log" 2>&1 &
VM_PID=$!
SSH=(ssh -i "$D/id" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts" -o ConnectTimeout=5 builder@127.0.0.1)
SCP=(scp -i "$D/id" -P "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts")
for attempt in $(seq 1 120); do
    if "${SSH[@]}" true 2>/dev/null; then break; fi
    kill -0 "$VM_PID" || { cat "$R/qemu.log"; exit 43; }
    sleep 5
done
"${SCP[@]}" "$CANDIDATE" "builder@127.0.0.1:/home/builder/merged-$SLURM_JOB_ID.tar.gz"
RC=0
"${SSH[@]}" bash -s -- "$SLURM_JOB_ID" "$EXPECTED" > "$R/smoke-command.log" 2>&1 <<'GUEST' || RC=$?
set -euo pipefail
RUN="/home/builder/merged-$1"
printf '%s  %s\n' "$2" "$RUN.tar.gz" | sha256sum -c -
mkdir "$RUN"
tar -xzf "$RUN.tar.gz" -C "$RUN"
IMAGE=chute-task:warp-17b6d4f
test "$(sudo docker image inspect --format '{{.Id}}' "$IMAGE")" = sha256:f2155903863e515cb0cda8c7fa764e4e13a3700636bf2ab8f363d99baab901dd
cd "$RUN"
RC=0
bash docker_smoke.sh "$IMAGE" "$RUN/tasks/arm/chute_realtime_bimanual_tracking" "$RUN/smoke-results" || RC=$?
tar -czf "$RUN/smoke-results.tar.gz" -C "$RUN" smoke-results
exit "$RC"
GUEST
"${SCP[@]}" "builder@127.0.0.1:/home/builder/merged-$SLURM_JOB_ID/smoke-results.tar.gz" "$R/" || RC=46
if [ -f "$R/smoke-results.tar.gz" ]; then sha256sum "$R/smoke-results.tar.gz" > "$R/results.sha256"; fi
"${SSH[@]}" 'sudo shutdown -h now' || true
for attempt in $(seq 1 30); do
    if ! kill -0 "$VM_PID" 2>/dev/null; then break; fi
    sleep 2
done
printf 'MERGED_DOCKER_CPU_SMOKE_EXIT=%s\n' "$RC"
exit "$RC"
