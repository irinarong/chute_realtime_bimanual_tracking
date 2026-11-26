#!/bin/bash
#SBATCH --job-name=chute-warp-assets
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/warp-assets-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/warp-assets-$SLURM_JOB_ID"
mkdir -p "$R/home"
cp "$BASE/datasets/scripts/omnigibson_6_1_0.kit" "$R/"
cp "$BASE/datasets/scripts/check_sim_assets_warp116.py" "$R/check_sim_assets.py"
BIND="$R:/results,$R/omnigibson_6_1_0.kit:/opt/BEHAVIOR-1K/OmniGibson/omnigibson/omnigibson_6_1_0.kit:ro"
if apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$BIND" "$BASE/datasets/chute-task.sif" \
    /opt/sim/bin/python -I /results/check_sim_assets.py > "$R/before.log" 2>&1; then
    echo 'Expected Warp mismatch was not reproduced' >&2
    exit 45
fi
grep -q 'Warp version mismatch: standalone=1.19.0' "$R/before.log"
# Author-only overlay; a real rebuild must pass the same check without PYTHONPATH.
export APPTAINERENV_PYTHONPATH=/warp-runtime
apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$BIND,$BASE/datasets/warp116-62728189/warp116:/warp-runtime:ro" \
    "$BASE/datasets/chute-task.sif" /opt/sim/bin/python /results/check_sim_assets.py > "$R/after.log" 2>&1
cat "$R/after.log"
printf 'WARP_VERSION_REGRESSION_CHECK_PASSED\n'
