#!/bin/bash
#SBATCH --job-name=chute-kit-assets
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/kit-assets-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/kit-assets-$SLURM_JOB_ID"
mkdir -p "$R/home"
cp "$BASE/datasets/scripts/omnigibson_6_1_0.kit" "$R/"
cp "$BASE/datasets/scripts/check_sim_assets.py" "$R/"
if apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results" "$BASE/datasets/chute-task.sif" \
    /opt/sim/bin/python -I /results/check_sim_assets.py > "$R/before.log" 2>&1; then
    echo 'Expected missing-kit failure was not reproduced' >&2
    exit 45
fi
grep -q "No such file or directory.*omnigibson_6_1_0.kit" "$R/before.log"
apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$R/omnigibson_6_1_0.kit:/opt/BEHAVIOR-1K/OmniGibson/omnigibson/omnigibson_6_1_0.kit:ro" \
    "$BASE/datasets/chute-task.sif" /opt/sim/bin/python -I /results/check_sim_assets.py > "$R/after.log" 2>&1
cat "$R/after.log"
printf 'KIT_ASSET_REGRESSION_CHECK_PASSED\n'
