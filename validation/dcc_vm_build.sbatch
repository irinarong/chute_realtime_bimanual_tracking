#!/bin/bash
#SBATCH --job-name=chute-docker-vm
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=10
#SBATCH --mem=48G
#SBATCH --time=03:00:00
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/docker-vm-%j.log
set -euo pipefail
test -r /dev/kvm && test -w /dev/kvm || { echo 'KVM_UNAVAILABLE'; exit 42; }
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-$SLURM_JOB_ID"
S="/tmp/chute-vm-runtime-$SLURM_JOB_ID"
mkdir -p "$D" "$S/root" "$S/runroot" "$S/xdg" "$S/tmp"
chmod 700 "$D" "$S/xdg"
export XDG_RUNTIME_DIR="$S/xdg" TMPDIR="$S/tmp"
P=(podman --cgroup-manager cgroupfs --root "$S/root" --runroot "$S/runroot" --storage-driver vfs --storage-opt vfs.ignore_chown_errors=true)
CACHE=/work/yr111/uav-to-uav-benchmark-20261125/datasets/image-cache
CRANE="$CACHE/crane"
QEMU_DIGEST="$($CRANE digest qemux/qemu)"
QEMU_IMAGE="docker.io/qemux/qemu@$QEMU_DIGEST"
echo "QEMU_RUNTIME=$QEMU_IMAGE"
"${P[@]}" pull "$QEMU_IMAGE"
curl -fL --retry 5 https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img -o "$D/ubuntu.img"
sha256sum "$D/ubuntu.img" > "$D/ubuntu.sha256"
ssh-keygen -q -t ed25519 -N '' -f "$D/id"
python3 -m venv "$D/seed-venv"
"$D/seed-venv/bin/pip" install pycdlib==1.14.0 > "$D/seed-dependencies.log" 2>&1
"$D/seed-venv/bin/python" - "$D" <<'PY'
import io,json,sys
from pathlib import Path
import pycdlib
p=Path(sys.argv[1]); public=(p/'id.pub').read_text().strip()
user='#cloud-config\nusers:\n  - name: builder\n    groups: sudo\n    sudo: ALL=(ALL) NOPASSWD:ALL\n    shell: /bin/bash\n    ssh_authorized_keys:\n      - '+public+'\nssh_pwauth: false\npackage_update: true\npackages: [docker.io]\nruncmd:\n  - [usermod, -aG, docker, builder]\n'
meta='instance-id: chute-docker-builder\nlocal-hostname: chute-docker-builder\n'
iso=pycdlib.PyCdlib();iso.new(rock_ridge='1.09',vol_ident='cidata')
for name,short,text in [('user-data','USERDATA',user),('meta-data','METADATA',meta)]:
 data=text.encode();iso.add_fp(io.BytesIO(data),len(data),iso_path='/'+short+'.;1',rr_name=name)
iso.write(str(p/'seed.iso'));iso.close()
PY
"${P[@]}" run --rm --cgroups disabled --network none -v "$D:$D" --entrypoint qemu-img "$QEMU_IMAGE" resize "$D/ubuntu.img" 180G
PORT=$((22000 + SLURM_JOB_ID % 10000))
"${P[@]}" run --rm --name "chute-vm-$SLURM_JOB_ID" --cgroups disabled --network host --security-opt label=disable --device /dev/kvm -v "$D:$D" --entrypoint qemu-system-x86_64 "$QEMU_IMAGE" \
    -enable-kvm -cpu host -smp 8 -m 32768 -display none \
    -drive "file=$D/ubuntu.img,format=qcow2,if=virtio" -drive "file=$D/seed.iso,format=raw,media=cdrom,readonly=on" \
    -netdev "user,id=n0,hostfwd=tcp:127.0.0.1:$PORT-:22" -device virtio-net-pci,netdev=n0 \
    -serial "file:$D/console.log" > "$D/qemu.log" 2>&1 &
VM_PID=$!
trap '"${P[@]}" stop -t 15 "chute-vm-$SLURM_JOB_ID" >/dev/null 2>&1 || true; wait "$VM_PID" || true' EXIT
SSH=(ssh -i "$D/id" -p "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$D/known_hosts" -o ConnectTimeout=5 builder@127.0.0.1)
SCP=(scp -i "$D/id" -P "$PORT" -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$D/known_hosts")
for attempt in $(seq 1 120); do
    if "${SSH[@]}" true 2>/dev/null; then break; fi
    kill -0 "$VM_PID" || { cat "$D/qemu.log"; exit 43; }
    sleep 5
done
"${SSH[@]}" 'sudo cloud-init status --wait; sudo docker version'
"${SCP[@]}" "$BASE/datasets/task-onboard-source.tar.gz" builder@127.0.0.1:/home/builder/task.tar.gz
"${SCP[@]}" "$CACHE/ale-base.tar" "$CACHE/uv.tar" builder@127.0.0.1:/home/builder/
"${SSH[@]}" 'set -e; sudo docker load -i ale-base.tar; sudo docker load -i uv.tar; mkdir -p task; tar -xzf task.tar.gz -C task; cp -a task/environment agent-context; rm -rf agent-context/setup; sudo docker build -t chute-task:20261126 agent-context' > "$D/docker-build.log" 2>&1
"${SSH[@]}" 'sudo docker image inspect chute-task:20261126' > "$D/images.json"
printf 'EXACT_DOCKER_IMAGE_BUILT\n'
"${SSH[@]}" 'sudo docker save chute-task:20261126 | gzip -1' > "$D/chute-task-image.tar.gz"
sha256sum "$D/chute-task-image.tar.gz" > "$D/image.sha256"
printf 'EXACT_DOCKER_IMAGE_SAVED\n'

