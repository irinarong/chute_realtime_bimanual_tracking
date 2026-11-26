#!/bin/bash
#SBATCH --job-name=chute-pinned-build
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=10
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/pinned-build-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-62721924"
R="$BASE/datasets/vm-pinned-$SLURM_JOB_ID"
S="/tmp/chute-pinned-runtime-$SLURM_JOB_ID"
mkdir -p "$R" "$S/root" "$S/runroot" "$S/xdg" "$S/tmp"
chmod 700 "$S/xdg"
export XDG_RUNTIME_DIR="$S/xdg" TMPDIR="$S/tmp"
P=(podman --cgroup-manager cgroupfs --root "$S/root" --runroot "$S/runroot" --storage-driver vfs --storage-opt vfs.ignore_chown_errors=true)
QEMU_IMAGE=$(sed -n 's/^QEMU_RUNTIME=//p' "$BASE/logs/docker-vm-62721924.log" | head -n1)
test -n "$QEMU_IMAGE"
"${P[@]}" pull "$QEMU_IMAGE"
PORT=$((22000 + SLURM_JOB_ID % 10000))
"${P[@]}" run --rm --name "chute-pinned-$SLURM_JOB_ID" --cgroups disabled --network host --security-opt label=disable --device /dev/kvm -v "$D:$D" -v "$R:$R" --entrypoint qemu-system-x86_64 "$QEMU_IMAGE" \
 -enable-kvm -cpu host -smp 8 -m 32768 -display none \
 -drive "file=$D/ubuntu.img,format=qcow2,if=virtio" \
 -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$PORT-:22" -device virtio-net-pci,netdev=n0 \
 -serial "file:$R/console.log" > "$R/qemu.log" 2>&1 &
VM_PID=$!
trap '"${P[@]}" stop -t 15 "chute-pinned-$SLURM_JOB_ID" >/dev/null 2>&1 || true; wait "$VM_PID" || true' EXIT
SSH=(ssh -i "$D/id" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts" -o ConnectTimeout=5 builder@127.0.0.1)
SCP=(scp -i "$D/id" -P "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$R/known_hosts")
for attempt in $(seq 1 120); do
 if "${SSH[@]}" true 2>/dev/null; then break; fi
 kill -0 "$VM_PID" || { cat "$R/qemu.log"; exit 43; }
 sleep 5
done
"${SCP[@]}" "$BASE/datasets/candidate.tar.gz" builder@127.0.0.1:/home/builder/pinned-candidate.tar.gz
# Buildx was installed after the original legacy build started. Explicitly retain
# that builder for this rebuild so the large simulator layer remains cached.
"${SSH[@]}" 'set -e; mkdir -p pinned-candidate; tar -xzf pinned-candidate.tar.gz -C pinned-candidate; test ! -e pinned-context; cp -a pinned-candidate/tasks/arm/chute_realtime_bimanual_tracking/environment pinned-context; rm -rf pinned-context/setup; sudo env DOCKER_BUILDKIT=0 docker build -t chute-task:20261126 pinned-context' > "$R/docker-build.log" 2>&1
"${SSH[@]}" 'sudo docker image inspect chute-task:20261126' > "$R/images.json"
# Downstream smoke/conversion depend on this job, so none can consume the old archive.
cp "$D/image.sha256" "$R/original-image.sha256"
"${SSH[@]}" 'set -euo pipefail; sudo docker save chute-task:20261126 | gzip -1' > "$D/chute-task-image.next.tar.gz"
mv "$D/chute-task-image.next.tar.gz" "$D/chute-task-image.tar.gz"
sha256sum "$D/chute-task-image.tar.gz" > "$D/image.sha256"
cp "$D/image.sha256" "$R/image.sha256"
printf 'PINNED_DOCKER_IMAGE_BUILT_AND_SAVED\n'
