#!/bin/bash
#SBATCH --job-name=chute-kit-build
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=10
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/kit-build-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-62721924"
R="$BASE/datasets/vm-kit-$SLURM_JOB_ID"
S="/tmp/chute-kit-runtime-$SLURM_JOB_ID"
LOCK="$D/active-operation.lock"
mkdir "$LOCK" || { echo 'VM disk already has an owner; refusing concurrent boot' >&2; exit 44; }
printf '%s\n' "$SLURM_JOB_ID" > "$LOCK/job_id"
# Unique output/context; keep every previous image archive untouched.
mkdir -p "$R" "$S/root" "$S/runroot" "$S/xdg" "$S/tmp"
chmod 700 "$S/xdg"
export XDG_RUNTIME_DIR="$S/xdg" TMPDIR="$S/tmp"
P=(podman --cgroup-manager cgroupfs --root "$S/root" --runroot "$S/runroot" --storage-driver vfs --storage-opt vfs.ignore_chown_errors=true)
QEMU_IMAGE=$(sed -n 's/^QEMU_RUNTIME=//p' "$BASE/logs/docker-vm-62721924.log" | head -n1)
test -n "$QEMU_IMAGE"
"${P[@]}" pull "$QEMU_IMAGE"
PORT=$((22000 + SLURM_JOB_ID % 10000))
"${P[@]}" run --rm --name "chute-kit-$SLURM_JOB_ID" --cgroups disabled --network host --security-opt label=disable --device /dev/kvm -v "$D:$D" -v "$R:$R" --entrypoint qemu-system-x86_64 "$QEMU_IMAGE" \
 -enable-kvm -cpu host -smp 8 -m 32768 -display none \
 -drive "file=$D/ubuntu.img,format=qcow2,if=virtio" \
 -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$PORT-:22" -device virtio-net-pci,netdev=n0 \
 -serial "file:$R/console.log" > "$R/qemu.log" 2>&1 &
VM_PID=$!
cleanup() {
    "${P[@]}" stop -t 30 "chute-kit-$SLURM_JOB_ID" >/dev/null 2>&1 || true
    wait "$VM_PID" || true
    rm -f "$LOCK/job_id"
    rmdir "$LOCK"
}
trap cleanup EXIT
SSH=(ssh -i "$D/id" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts" -o ConnectTimeout=5 builder@127.0.0.1)
SCP=(scp -i "$D/id" -P "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts")
for attempt in $(seq 1 120); do
 if "${SSH[@]}" true 2>/dev/null; then break; fi
 kill -0 "$VM_PID" || { cat "$R/qemu.log"; exit 43; }
 sleep 5
done
CANDIDATE="$BASE/datasets/candidate-3f5843be.tar.gz"
echo "3f5843be7799202dd9eeb93592fb933947bd4a05d2f28cc91630d786751947fa  $CANDIDATE" | sha256sum -c -
"${SCP[@]}" "$CANDIDATE" "builder@127.0.0.1:/home/builder/kit-candidate-$SLURM_JOB_ID.tar.gz"
"${SSH[@]}" bash -s -- "$SLURM_JOB_ID" > "$R/docker-build-smoke.log" 2>&1 <<'GUEST'
set -euo pipefail
RUN="/home/builder/kit-candidate-$1"
mkdir "$RUN"
tar -xzf "$RUN.tar.gz" -C "$RUN"
cp -a "$RUN/tasks/arm/chute_realtime_bimanual_tracking/environment" "$RUN/context"
rm -rf "$RUN/context/setup"
sudo env DOCKER_BUILDKIT=0 docker build -t chute-task:kit-c3521f9 "$RUN/context"
cd "$RUN"
bash docker_smoke.sh chute-task:kit-c3521f9 "$RUN/tasks/arm/chute_realtime_bimanual_tracking" "$RUN/smoke-results"
tar -czf "$RUN/smoke-results.tar.gz" -C "$RUN" smoke-results
GUEST
"${SCP[@]}" "builder@127.0.0.1:/home/builder/kit-candidate-$SLURM_JOB_ID/smoke-results.tar.gz" "$R/"
"${SSH[@]}" 'sudo docker image inspect chute-task:kit-c3521f9' > "$R/images.json"
"${SSH[@]}" 'set -euo pipefail; sudo docker save chute-task:kit-c3521f9 | gzip -1' > "$R/chute-task-image.next.tar.gz"
mv "$R/chute-task-image.next.tar.gz" "$R/chute-task-image.tar.gz"
sha256sum "$R/chute-task-image.tar.gz" > "$R/image.sha256"
printf 'KIT_DOCKER_IMAGE_BUILT_CHECKED_AND_SAVED\n'
# Shut the filesystem down cleanly before releasing exclusive ownership.
"${SSH[@]}" 'sudo shutdown -h now' || true
for attempt in $(seq 1 60); do
    if ! kill -0 "$VM_PID" 2>/dev/null; then break; fi
    sleep 2
done
