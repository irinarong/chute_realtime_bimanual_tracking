#!/bin/bash
#SBATCH --job-name=chute-driver-libs
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --nodelist=dcc-core-gpu-ferc-s-aa32-9
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/driver-libs-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/driver-libs-$SLURM_JOB_ID"
mkdir -p "$R/home"
shopt -s nullglob
ICDS=(/usr/share/vulkan/icd.d/*nvidia*.json /etc/vulkan/icd.d/*nvidia*.json)
test "${#ICDS[@]}" -eq 1
cp "${ICDS[0]}" "$R/host-nvidia-icd.json"
ldconfig -p | grep -E 'libGLX_nvidia|libnvidia-gl|libnvidia-vulkan|libvulkan' > "$R/host-libraries.txt"
# CPU-only dependency inspection: no CUDA/Vulkan initialization or GPU commands.
apptainer exec --nv --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,${ICDS[0]}:/results/nvidia_icd.json:ro" \
    "$BASE/datasets/chute-task.sif" /opt/sim/bin/python -u - <<'PY'
import ctypes,json,os,pathlib,subprocess
root=pathlib.Path('/results')
icd=json.loads((root/'nvidia_icd.json').read_text())
record={'scope':'CPU allocation, shared-library loading only; no GPU runtime test',
        'icd':icd,'ld_library_path':os.environ.get('LD_LIBRARY_PATH')}
name=icd['ICD']['library_path']
try:
    ctypes.CDLL(name)
    record['icd_load']='ok'
except OSError as exc:
    record['icd_load']='failed';record['error']=str(exc)
record['bound_driver_files']={str(p):str(p.resolve()) for p in pathlib.Path('/.singularity.d/libs').glob('*')
                            if any(v in p.name for v in ('GLX','nvidia','vulkan'))}
record['container_library_cache']=subprocess.run(['ldconfig','-p'],capture_output=True,text=True).stdout
for path in pathlib.Path('/.singularity.d/libs').glob(pathlib.Path(name).name+'*'):
    record.setdefault('ldd',{})[str(path)]=subprocess.run(['ldd',str(path)],capture_output=True,text=True).stdout
(root/'libraries.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
PY
