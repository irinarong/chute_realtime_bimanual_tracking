#!/bin/bash
#SBATCH --job-name=chute-docker-smoke
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=00:45:00
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/docker-smoke-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-62721924"
R="$BASE/datasets/vm-smoke-$SLURM_JOB_ID"
S="/tmp/chute-smoke-runtime-$SLURM_JOB_ID"
mkdir -p "$R" "$S/root" "$S/runroot" "$S/xdg" "$S/tmp"
chmod 700 "$S/xdg"
export XDG_RUNTIME_DIR="$S/xdg" TMPDIR="$S/tmp"
P=(podman --cgroup-manager cgroupfs --root "$S/root" --runroot "$S/runroot" --storage-driver vfs --storage-opt vfs.ignore_chown_errors=true)
QEMU_IMAGE=$(sed -n 's/^QEMU_RUNTIME=//p' "$BASE/logs/docker-vm-62721924.log" | head -n1)
test -n "$QEMU_IMAGE"
"${P[@]}" pull "$QEMU_IMAGE"
PORT=$((22000 + SLURM_JOB_ID % 10000))
"${P[@]}" run --rm --name "chute-smoke-$SLURM_JOB_ID" --cgroups disabled --network host --security-opt label=disable --device /dev/kvm -v "$D:$D" -v "$R:$R" --entrypoint qemu-system-x86_64 "$QEMU_IMAGE" \
 -enable-kvm -cpu host -smp 4 -m 16384 -display none \
 -drive "file=$D/ubuntu.img,format=qcow2,if=virtio" \
 -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$PORT-:22" -device virtio-net-pci,netdev=n0 \
 -serial "file:$R/console.log" > "$R/qemu.log" 2>&1 &
VM_PID=$!
trap '"${P[@]}" stop -t 15 "chute-smoke-$SLURM_JOB_ID" >/dev/null 2>&1 || true; wait "$VM_PID" || true' EXIT
SSH=(ssh -i "$D/id" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts" -o ConnectTimeout=5 builder@127.0.0.1)
SCP=(scp -i "$D/id" -P "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts")
for attempt in $(seq 1 120); do
 if "${SSH[@]}" true 2>/dev/null; then break; fi
 kill -0 "$VM_PID" || { cat "$R/qemu.log"; exit 43; }
 sleep 5
done
"${SCP[@]}" "$BASE/datasets/candidate.tar.gz" builder@127.0.0.1:/home/builder/candidate.tar.gz
"${SSH[@]}" 'set -e; mkdir -p candidate; tar -xzf candidate.tar.gz -C candidate; cd candidate; bash docker_smoke.sh chute-task:20261126 "$PWD/tasks/arm/chute_realtime_bimanual_tracking" /home/builder/chute-smoke-results' > "$R/smoke-command.log" 2>&1
"${SSH[@]}" 'tar -czf /home/builder/chute-smoke-results.tar.gz -C /home/builder chute-smoke-results'
"${SCP[@]}" builder@127.0.0.1:/home/builder/chute-smoke-results.tar.gz "$R/"
printf 'CHUTE_DOCKER_CPU_SMOKE_COMPLETE\n'
