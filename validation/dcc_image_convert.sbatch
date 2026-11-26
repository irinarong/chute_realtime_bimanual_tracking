#!/bin/bash
#SBATCH --job-name=chute-image-convert
#SBATCH --account=cpslab
#SBATCH --partition=common
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:30:00
#SBATCH --chdir=/work/yr111/chute-direct-answer-20261126
#SBATCH --output=/work/yr111/chute-direct-answer-20261126/logs/image-convert-%j.log
set -euo pipefail
BASE=/work/yr111/chute-direct-answer-20261126
D="$BASE/datasets/vm-builder-62721924"
R="$BASE/datasets/apptainer-convert-$SLURM_JOB_ID"
mkdir -p "$R/tmp" "$R/cache"
export APPTAINER_TMPDIR="$R/tmp" APPTAINER_CACHEDIR="$R/cache"
sha256sum -c "$D/image.sha256"
apptainer build "$BASE/datasets/chute-task.sif" "docker-archive:$D/chute-task-image.tar.gz"
sha256sum "$BASE/datasets/chute-task.sif" > "$R/sif.sha256"
printf 'CHUTE_IMAGE_CONVERTED\n'
