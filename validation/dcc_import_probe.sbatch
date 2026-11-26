#!/bin/bash
#SBATCH --job-name=chute-import-probe
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/import-probe-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/import-probe-$SLURM_JOB_ID"
mkdir -p "$R/home"
SCRATCH=$(mktemp -d "/tmp/chute-import-${SLURM_JOB_ID}.XXXXXX")
trap 'rm -rf -- "$SCRATCH"' EXIT
df -B1 "$SCRATCH" > "$R/scratch-filesystem.txt"
export APPTAINERENV_OMNI_KIT_ACCEPT_EULA=YES APPTAINERENV_ACCEPT_EULA=Y
export APPTAINERENV_OMNIGIBSON_HEADLESS=1
export APPTAINERENV_OMP_NUM_THREADS=4 APPTAINERENV_MKL_NUM_THREADS=4
# CPU-only import/Inductor diagnosis. No og.launch(), CUDA or rendering test.
apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$SCRATCH:/tmp" "$BASE/datasets/chute-task.sif" /opt/sim/bin/python -u - <<'PY'
import json, pathlib, shutil, subprocess, traceback
root = pathlib.Path('/results')
record = {'scope': 'CPU-only import diagnostic; no simulator launch', 'official_ale_validate': False}
record['tmp_before'] = shutil.disk_usage('/tmp')._asdict()
assert record['tmp_before']['free'] >= 10 * 1024**3
for command in (['g++', '--version'], ['ls', '-ld', '/usr/include', '/usr/include/stdlib.h']):
    result = subprocess.run(command, capture_output=True, text=True)
    record.setdefault('commands', []).append({'args': command, 'returncode': result.returncode,
                                            'stdout': result.stdout, 'stderr': result.stderr})
try:
    import omnigibson
    record['import_ok'] = True
except Exception:
    record['import_ok'] = False
    record['traceback'] = traceback.format_exc()
    (root / 'traceback.txt').write_text(record['traceback'])
    traceback.print_exc()
finally:
    record['tmp_after'] = shutil.disk_usage('/tmp')._asdict()
    (root / 'import-result.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record), flush=True)
if not record['import_ok']:
    raise SystemExit(1)
PY
