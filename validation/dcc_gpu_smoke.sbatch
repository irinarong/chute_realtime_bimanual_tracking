#!/bin/bash
#SBATCH --job-name=chute-image-gpu
#SBATCH --account=cpslab
#SBATCH --partition=gpu-common
#SBATCH --gres=gpu:5000_ada:1
#SBATCH --nodelist=dcc-core-gpu-ferc-s-aa32-9
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/gpu-smoke-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/gpu-smoke-$SLURM_JOB_ID"
mkdir -p "$R/home" "$R/cache" "$R/candidate"
tar -xzf "$BASE/datasets/candidate.tar.gz" -C "$R/candidate"
cp "$BASE/datasets/scripts/gpu_preflight.py" "$R/gpu_preflight.py"
python3 "$R/gpu_preflight.py" --output "$R/gpu-allocation-host.json"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > "$R/hardware.csv"
SIF="$BASE/datasets/chute-task.sif"
apptainer exec --cleanenv --no-home --bind "$R:/results" "$SIF" \
    cp -r /opt/sim/lib/python3.12/site-packages/isaacsim/apps /results/apps
export APPTAINERENV_OMNI_KIT_ACCEPT_EULA=YES APPTAINERENV_ACCEPT_EULA=Y
export APPTAINERENV_OMNIGIBSON_HEADLESS=1 APPTAINERENV_OMNIGIBSON_GPU_ID=0
export APPTAINERENV_CUDA_VISIBLE_DEVICES="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["uuid"])' "$R/gpu-allocation-host.json")"
export APPTAINERENV_OMP_NUM_THREADS=4 APPTAINERENV_MKL_NUM_THREADS=4
shopt -s nullglob
NVIDIA_ICDS=(/usr/share/vulkan/icd.d/*nvidia*.json /etc/vulkan/icd.d/*nvidia*.json)
test "${#NVIDIA_ICDS[@]}" -eq 1
VULKAN=(--bind "${NVIDIA_ICDS[0]}:/results/nvidia_icd.json:ro")
export APPTAINERENV_VK_DRIVER_FILES=/results/nvidia_icd.json
export APPTAINERENV_VK_ICD_FILENAMES=/results/nvidia_icd.json
apptainer exec --nv --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$R/candidate/tasks/arm/chute_realtime_bimanual_tracking:/task:ro" \
    --bind "$R/apps:/opt/sim/lib/python3.12/site-packages/isaacsim/apps" \
    --bind "$R/cache:/opt/sim/lib/python3.12/site-packages/omni/cache" \
    "${VULKAN[@]}" "$SIF" /bin/bash -euc '
        /opt/sim/bin/python /results/gpu_preflight.py --host-record /results/gpu-allocation-host.json --output /results/gpu-allocation-container.json
        exec /opt/venv/bin/python /results/candidate/gpu_smoke.py
    '
printf 'CHUTE_IMAGE_GPU_SMOKE_COMPLETE\n'
