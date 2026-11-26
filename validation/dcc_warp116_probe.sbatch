#!/bin/bash
#SBATCH --job-name=chute-warp116-probe
#SBATCH --account=cpslab
#SBATCH --partition=gpu-common
#SBATCH --gres=gpu:5000_ada:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/warp116-probe-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
WARP_RUNTIME="${1:?path to verified Warp 1.16 target installation required}"
R="$BASE/datasets/warp116-probe-$SLURM_JOB_ID"
mkdir -p "$R/home" "$R/cache" "$R/candidate"
SCRATCH=$(mktemp -d "/tmp/chute-gpu-${SLURM_JOB_ID}.XXXXXX")
trap 'rm -rf -- "$SCRATCH"' EXIT
df -B1 "$SCRATCH" > "$R/scratch-filesystem.txt"
test "$(df -B1 --output=avail "$SCRATCH" | tail -1)" -gt 10737418240
tar -xzf "$BASE/datasets/candidate.tar.gz" -C "$R/candidate"
cp "$BASE/datasets/scripts/omnigibson_6_1_0.kit" "$R/omnigibson_6_1_0.kit"
cp "$BASE/datasets/scripts/check_sim_assets.py" "$R/check_sim_assets.py"
export APPTAINERENV_CHUTE_IMAGE_OVERLAY=author-diagnostic-kit-and-warp116
export APPTAINERENV_PYTHONPATH=/warp-runtime
# Negative control: old image must fail its new build-time check.
if apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$SCRATCH:/tmp" "$BASE/datasets/chute-task.sif" \
    /opt/sim/bin/python -I /results/check_sim_assets.py > "$R/check-before.log" 2>&1; then
    echo 'Expected missing-kit regression was not reproduced' >&2
    exit 45
fi
grep -q "No such file or directory.*omnigibson_6_1_0.kit" "$R/check-before.log"
cp "$BASE/datasets/scripts/gpu_smoke.py" "$R/gpu_smoke.py"
cp "$BASE/datasets/scripts/diagnostic_cell_server.py" "$R/diagnostic_cell_server.py"
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
python3 "$BASE/datasets/scripts/prepare_vulkan_icd.py" "${NVIDIA_ICDS[0]}" "$R/nvidia_icd.json"
export APPTAINERENV_VK_DRIVER_FILES=/results/nvidia_icd.json
export APPTAINERENV_VK_ICD_FILENAMES=/results/nvidia_icd.json
apptainer exec --nv --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$R/candidate/tasks/arm/chute_realtime_bimanual_tracking:/task:ro,$SCRATCH:/tmp" \
    --bind "$R/apps:/opt/sim/lib/python3.12/site-packages/isaacsim/apps" \
    --bind "$R/omnigibson_6_1_0.kit:/opt/BEHAVIOR-1K/OmniGibson/omnigibson/omnigibson_6_1_0.kit:ro" \
    --bind "$WARP_RUNTIME:/warp-runtime:ro" \
    --bind "$R/cache:/opt/sim/lib/python3.12/site-packages/omni/cache" \
    "$SIF" /bin/bash -euc '
        /opt/sim/bin/python -c "import warp; assert warp.__version__ == \"1.16.0\", warp.__version__; print(warp.__file__)" > /results/warp-version.txt
        /opt/sim/bin/python -I /results/check_sim_assets.py > /results/check-after.log
        /opt/sim/bin/python /results/gpu_preflight.py --host-record /results/gpu-allocation-host.json --output /results/gpu-allocation-container.json
        exec /opt/venv/bin/python /results/gpu_smoke.py --server /results/diagnostic_cell_server.py
    '
printf 'CHUTE_WARP116_OVERLAY_DIAGNOSTIC_COMPLETE\n'
