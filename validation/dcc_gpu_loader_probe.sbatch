#!/bin/bash
#SBATCH --job-name=chute-vulkan-probe
#SBATCH --account=cpslab
#SBATCH --partition=gpu-common
#SBATCH --gres=gpu:5000_ada:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/gpu-loader-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/gpu-loader-$SLURM_JOB_ID"
mkdir -p "$R/home"
cp "$BASE/datasets/scripts/gpu_preflight.py" "$R/gpu_preflight.py"
python3 "$R/gpu_preflight.py" --output "$R/host.json"
shopt -s nullglob
ICDS=(/usr/share/vulkan/icd.d/*nvidia*.json /etc/vulkan/icd.d/*nvidia*.json)
test "${#ICDS[@]}" -eq 1
cp "${ICDS[0]}" "$R/host-nvidia-icd.json"
ldconfig -p | grep -E 'libGLX_nvidia|libnvidia-gl|libnvidia-vulkan|libvulkan' > "$R/host-libraries.txt"
export APPTAINERENV_CUDA_VISIBLE_DEVICES="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["uuid"])' "$R/host.json")"
export APPTAINERENV_VK_DRIVER_FILES=/results/nvidia_icd.json
export APPTAINERENV_VK_ICD_FILENAMES=/results/nvidia_icd.json
export APPTAINERENV_VK_LOADER_DEBUG=all
apptainer exec --nv --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,${ICDS[0]}:/results/nvidia_icd.json:ro" \
    "$BASE/datasets/chute-task.sif" /opt/sim/bin/python -u - <<'PY'
import ctypes, json, os, pathlib, subprocess, sys
print('LD_LIBRARY_PATH', os.environ.get('LD_LIBRARY_PATH'), flush=True)
icd=json.loads(pathlib.Path('/results/nvidia_icd.json').read_text())
print('ICD', json.dumps(icd), flush=True)
print('CONTAINER_LIBRARIES', subprocess.run(['ldconfig','-p'],capture_output=True,text=True).stdout, flush=True)
print('BOUND_NVIDIA_LIBRARIES', [str(p) for p in pathlib.Path('/.singularity.d/libs').glob('*') if any(x in p.name for x in ('vulkan','GLX','glcore','glvk'))], flush=True)
try:
    ctypes.CDLL(icd['ICD']['library_path'])
    print('ICD_CDLL_LOAD_OK', flush=True)
except OSError as exc:
    print('ICD_CDLL_LOAD_FAILED',str(exc),flush=True)
import torch
print('CUDA', torch.cuda.is_available(), torch.cuda.device_count(), flush=True)
if torch.cuda.is_available():
    print('CUDA_DEVICE',str(torch.cuda.get_device_properties(0)),flush=True)
sys.path.insert(0,'/results')
from gpu_preflight import container
result=container('/results/host.json')
pathlib.Path('/results/preflight.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
PY
