#!/bin/bash
#SBATCH --job-name=chute-physical-reference
#SBATCH --account=cpslab_h200_s
#SBATCH --partition=scavenger-h200
#SBATCH --gres=gpu:h200:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/physical-reference-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/physical-reference-$SLURM_JOB_ID"
mkdir -p "$R/home" "$R/cache" "$R/candidate"
SCRATCH=$(mktemp -d "/tmp/chute-gpu-${SLURM_JOB_ID}.XXXXXX")
trap 'rm -rf -- "$SCRATCH"' EXIT
df -B1 "$SCRATCH" > "$R/scratch-filesystem.txt"
test "$(df -B1 --output=avail "$SCRATCH" | tail -1)" -gt 10737418240
CANDIDATE="${2:?Pass immutable author candidate path}"
EXPECTED="${3:?Pass author candidate SHA256}"
printf '%s  %s\n' "$EXPECTED" "$CANDIDATE" | sha256sum -c -
tar -xzf "$CANDIDATE" -C "$R/candidate"
sha256sum "$CANDIDATE" > "$R/candidate.sha256"
cp "$R/candidate/physical_reference_smoke.py" "$R/physical_reference_smoke.py"
cp "$BASE/datasets/scripts/gpu_preflight.py" "$R/gpu_preflight.py"
python3 "$R/gpu_preflight.py" --output "$R/gpu-allocation-host.json"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > "$R/hardware.csv"
SIF="${1:?Pass exact SIF path}"
printf '%s  %s\n' 680741dffceac7953eb5b6d6ab175f8a00a9998f1306ceff519e7c33e4dbf87b "$SIF" | sha256sum -c - > "$R/sif-check.txt"
apptainer exec --cleanenv --no-home --bind "$R:/results" "$SIF" \
    cp -r /opt/sim/lib/python3.12/site-packages/isaacsim/apps /results/apps
export APPTAINERENV_OMNI_KIT_ACCEPT_EULA=YES APPTAINERENV_ACCEPT_EULA=Y
export APPTAINERENV_OMNIGIBSON_HEADLESS=1 APPTAINERENV_OMNIGIBSON_GPU_ID=0
export APPTAINERENV_CUDA_VISIBLE_DEVICES="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["uuid"])' "$R/gpu-allocation-host.json")"
export APPTAINERENV_OMP_NUM_THREADS=4 APPTAINERENV_MKL_NUM_THREADS=4
shopt -s nullglob
NVIDIA_ICDS=(/usr/share/vulkan/icd.d/*nvidia*.json /etc/vulkan/icd.d/*nvidia*.json)
test "${#NVIDIA_ICDS[@]}" -eq 1
python3 "$BASE/datasets/scripts/prepare_vulkan_icd.py" "${NVIDIA_ICDS[0]}" "$R/nvidia_icd.json"
export APPTAINERENV_VK_DRIVER_FILES=/results/nvidia_icd.json
export APPTAINERENV_VK_ICD_FILENAMES=/results/nvidia_icd.json
# DCC's default Apptainer NVIDIA list omits NGX; its absence corrupts RGB quality.
python3 "$BASE/datasets/scripts/prepare_ngx_library.py" "$R/nvidia-ngx"
export APPTAINERENV_LD_LIBRARY_PATH=/nvidia-ngx:/.singularity.d/libs
apptainer exec --nv --cleanenv --containall --bind "$R/nvidia-ngx:/nvidia-ngx:ro" --home "$R/home:/home/user" \
    --bind "$R:/results,$R/candidate/tasks/arm/chute_realtime_bimanual_tracking:/task:ro,$SCRATCH:/tmp" \
    --bind "$R/apps:/opt/sim/lib/python3.12/site-packages/isaacsim/apps" \
    --bind "$R/cache:/opt/sim/lib/python3.12/site-packages/omni/cache" \
    "$SIF" /bin/bash -euc '
        /opt/sim/bin/python -c '"'"'import ctypes; ctypes.CDLL("libnvidia-ngx.so.1")'"'"'
        /opt/sim/bin/python /results/gpu_preflight.py --host-record /results/gpu-allocation-host.json --output /results/gpu-allocation-container.json
        exec /opt/venv/bin/python /results/physical_reference_smoke.py
    '
printf 'CHUTE_PHYSICAL_REFERENCE_SMOKE_COMPLETE\n'
