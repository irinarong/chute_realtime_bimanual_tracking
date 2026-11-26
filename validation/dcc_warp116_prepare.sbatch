#!/bin/bash
#SBATCH --job-name=chute-warp116-prepare
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/warp116-prepare-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
R="$BASE/datasets/warp116-$SLURM_JOB_ID"
mkdir -p "$R/home"
SCRATCH=$(mktemp -d "/tmp/chute-warp-${SLURM_JOB_ID}.XXXXXX")
trap 'rm -rf -- "$SCRATCH"' EXIT
WHEEL=warp_lang-1.16.0-py3-none-manylinux_2_28_x86_64.whl
if [ -n "${1:-}" ]; then
    cp "$1" "$R/$WHEEL"
else
    curl --fail --location --retry 3 \
        "https://files.pythonhosted.org/packages/1d/3d/47feef2eee4739437e19d6949ea231ca4181c9eacbaa39144761e6130d94/$WHEEL" \
        -o "$R/$WHEEL"
fi
echo "96449fc1e3b354185e2f09434fb794b5953ab2e8673b104d7e7f48d5d418bb35  $R/$WHEEL" | sha256sum -c -
apptainer exec --cleanenv --containall --home "$R/home:/home/user" \
    --bind "$R:/results,$SCRATCH:/tmp" "$BASE/datasets/chute-task.sif" \
    /usr/local/bin/uv pip install --python /opt/sim/bin/python --target /results/warp116 \
    --no-deps "/results/$WHEEL"
printf 'WARP116_DIAGNOSTIC_PACKAGE_READY\n'
