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
# Apptainer 1.5.4 failed on the compressed docker-archive input. Decompress with
# gzip (which validates its CRC), then use the transport actually present in the
# Docker export. Recent Docker saves include an OCI layout alongside manifest.json.
gzip -dc "$D/chute-task-image.tar.gz" > "$R/chute-task-image.tar"
sha256sum "$R/chute-task-image.tar" > "$R/uncompressed-archive.sha256"
TRANSPORT=$(python3 "$BASE/datasets/scripts/inspect_image_archive.py" \
    "$R/chute-task-image.tar" "$BASE/datasets/vm-pinned-62723900/images.json" "$R/archive-format.json")
cat "$R/archive-format.json"
apptainer build "$R/chute-task.sif" "$TRANSPORT:$R/chute-task-image.tar"
mv "$R/chute-task.sif" "$BASE/datasets/chute-task.sif"
sha256sum "$BASE/datasets/chute-task.sif" > "$R/sif.sha256"
rm "$R/chute-task-image.tar"
printf 'CHUTE_IMAGE_CONVERTED\n'
