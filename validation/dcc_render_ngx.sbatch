#!/bin/bash
#SBATCH --job-name=chute-render-ngx
#SBATCH --account=cpslab
#SBATCH --partition=gpu-common
#SBATCH --gres=gpu:5000_ada:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/render-ngx-%j.log
set -euo pipefail
SCRATCH=$(mktemp -d "/tmp/chute-visual-${SLURM_JOB_ID}.XXXXXX")
trap 'rm -rf -- "$SCRATCH"' EXIT
test "$(df -B1 --output=avail "$SCRATCH" | tail -1)" -gt 10737418240
BASE=/work/yr111/chute-direct-answer-20261126
WARP_RUNTIME="${1:?verified Warp 1.16 target directory required}"
R="$BASE/datasets/render-ngx-$SLURM_JOB_ID"
mkdir -p "$R/home" "$R/cache" "$R/candidate"
df -B1 "$SCRATCH" > "$R/scratch-filesystem.txt"
CANDIDATE="$BASE/datasets/candidate-c67a7265.tar.gz"
tar -xzf "$CANDIDATE" -C "$R/candidate"
sha256sum "$CANDIDATE" > "$R/candidate.sha256"
cp "$BASE/datasets/scripts/render_probe.py" "$R/render_probe.py"
mkdir "$R/driver-empty" "$R/driver-ngx"
NGX_PATH=$(/sbin/ldconfig -p | awk '$1 == "libnvidia-ngx.so.1" && !found {print $NF; found=1}')
test -n "$NGX_PATH"
cp -L "$NGX_PATH" "$R/driver-ngx/libnvidia-ngx.so.1"
sha256sum "$NGX_PATH" "$R/driver-ngx/libnvidia-ngx.so.1" > "$R/ngx.sha256"
ldd "$NGX_PATH" > "$R/ngx-ldd.txt"
cp "$BASE/datasets/scripts/gpu_preflight.py" "$R/gpu_preflight.py"
cp "$BASE/datasets/scripts/omnigibson_6_1_0.kit" "$R/"
printf '%s\n' 'Author diagnostic: old SIF plus Kit and Warp1.16 overlays; not exact-image ALE verification' > "$R/image-overlay.txt"
python3 "$R/gpu_preflight.py" --output "$R/gpu-allocation-host.json"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > "$R/hardware.csv"
SIF="$BASE/datasets/chute-task.sif"
apptainer exec --cleanenv --no-home --bind "$R:/results" "$SIF" \
    cp -r /opt/sim/lib/python3.12/site-packages/isaacsim/apps /results/apps
export APPTAINERENV_PYTHONPATH=/warp-runtime
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
# Both cases use separate Kit processes/homes and identical static scene inputs.
# The only intervention is exposing the exact host's NGX library in the second case.
for CASE in empty ngx; do
    mkdir -p "$R/$CASE/home" "$R/$CASE/cache" "$R/$CASE/apps"
    cp -a "$R/apps/." "$R/$CASE/apps/"
    cp "$R/render_probe.py" "$R/gpu_preflight.py" "$R/gpu-allocation-host.json" "$R/nvidia_icd.json" "$R/$CASE/"
    export APPTAINERENV_LD_LIBRARY_PATH=/diagnostic-driver:/.singularity.d/libs
    apptainer exec --nv --cleanenv --containall --home "$R/$CASE/home:/home/user" \
    --bind "$R/$CASE:/results,$R/candidate/tasks/arm/chute_realtime_bimanual_tracking:/task:ro,$SCRATCH:/tmp" \
    --bind "$R/driver-$CASE:/diagnostic-driver:ro" \
    --bind "$R/$CASE/apps:/opt/sim/lib/python3.12/site-packages/isaacsim/apps" \
    --bind "$R/omnigibson_6_1_0.kit:/opt/BEHAVIOR-1K/OmniGibson/omnigibson/omnigibson_6_1_0.kit:ro" \
    --bind "$WARP_RUNTIME:/warp-runtime:ro" \
    --bind "$R/$CASE/cache:/opt/sim/lib/python3.12/site-packages/omni/cache" \
    "$SIF" /bin/bash -euc '
        /opt/sim/bin/python /results/gpu_preflight.py --host-record /results/gpu-allocation-host.json --output /results/gpu-allocation-container.json
        exec /opt/sim/bin/python /results/render_probe.py
    ' > "$R/$CASE/isaac.log" 2>&1
done
printf 'CHUTE_STATIC_RENDER_COMPARISON_COMPLETE\n'
