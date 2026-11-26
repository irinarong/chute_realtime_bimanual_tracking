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
mkdir -p "$R"
# OCI unpacking clears xattrs; DCC /work is NFS and rejects removal of its
# system.nfs4_dacl attribute. Rootfs extraction must use local disk, not NFS/tmpfs.
S=$(mktemp -d "/tmp/chute-convert-$SLURM_JOB_ID.XXXXXX")
trap 'chmod -R u+rwX "$S" 2>/dev/null || true; rm -rf -- "$S"' EXIT
FSTYPE=$(stat -f -c %T "$S")
case "$FSTYPE" in nfs*|tmpfs) echo "Unsupported conversion scratch filesystem: $FSTYPE" >&2; exit 42;; esac
df -h "$S" > "$R/scratch-filesystem.txt"
test "$(df -Pk "$S" | awk 'NR==2 {print $4}')" -ge 83886080 || { echo 'Need 80 GiB local scratch space' >&2; exit 43; }
mkdir "$S/tmp" "$S/cache"
export APPTAINER_TMPDIR="$S/tmp" APPTAINER_CACHEDIR="$S/cache" TMPDIR="$S/tmp"
sha256sum -c "$D/image.sha256"
# Apptainer 1.5.4 failed on the compressed docker-archive input. Decompress with
# gzip (which validates its CRC), then use the transport actually present in the
# Docker export. Recent Docker saves include an OCI layout alongside manifest.json.
INPUT_ARCHIVE="${1:-$R/chute-task-image.tar}"
if [ "$INPUT_ARCHIVE" = "$R/chute-task-image.tar" ]; then
    gzip -dc "$D/chute-task-image.tar.gz" > "$INPUT_ARCHIVE"
    sha256sum "$INPUT_ARCHIVE" > "$R/uncompressed-archive.sha256"
else
    # Reuse a previous successful CRC/decompression stage after a later failure.
    sha256sum -c "$(dirname "$INPUT_ARCHIVE")/uncompressed-archive.sha256"
    cp "$(dirname "$INPUT_ARCHIVE")/uncompressed-archive.sha256" "$R/uncompressed-archive.sha256"
fi
TRANSPORT=$(python3 "$BASE/datasets/scripts/inspect_image_archive.py" \
    "$INPUT_ARCHIVE" "$BASE/datasets/vm-pinned-62723900/images.json" "$R/archive-format.json")
cat "$R/archive-format.json"
apptainer build "$R/chute-task.sif" "$TRANSPORT:$INPUT_ARCHIVE"
mv "$R/chute-task.sif" "$BASE/datasets/chute-task.sif"
sha256sum "$BASE/datasets/chute-task.sif" > "$R/sif.sha256"
if [ "$INPUT_ARCHIVE" = "$R/chute-task-image.tar" ]; then rm "$INPUT_ARCHIVE"; fi
printf 'CHUTE_IMAGE_CONVERTED\n'
