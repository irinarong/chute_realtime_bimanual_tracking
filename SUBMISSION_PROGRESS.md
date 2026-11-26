# Two-task submission work — active, admission pending

## Scope and source of truth

Complete both the friend's chute controller task and our UAV-to-UAV detector-training
task. The user confirmed that mandatory agent model training applies to UAV only.
Preserve the friend's original DCC experiments. No upstream task PR has been opened.
Never interpret a synthetic oracle reward as physical robot success.

- Chute: this managed worktree, branch `codex/chute-submission-ready`. Task source
  and the SDK-based CPU smoke were frozen at `dce541a`; current changes improve
  the author build runner and this status, without changing the submitted task.
- UAV: `/Users/aaronpang/.codex/worktrees/uav-to-uav-task/agentic-robotics-benchmark-review-20261125`,
  branch `codex/uav-to-uav-tracking`. Current committed source is `3daa2d123c6f694f4d2b9e883dc52d5e7f0a97da`,
  including verified public box calibration and reference provenance.
- ALE: `bfb75050aca2c54b45c5ab23bae6028a834a468a`, installed at
  `/tmp/chute-ale-pinned-20261126`. The canonical shared grader is unchanged.

## Chute: measured work and live jobs

Nineteen host tests, pinned ALE lint and domain lint passed. Real host entrypoint
checks measured untouched zero, synthetic oracle one twice, unauthorized/wrong
answers zero. The direct-answer fixture independently validates 120 terminal
snapshots against hidden layouts and the shared scoring. Its verdict explicitly
labels `synthetic_reference=1`, `physical_rollout=0`. The prior privileged physical
controller is preserved; neither path establishes ordinary visual-control success.

Final Docker sources pin the MIT robot ZIP by immutable revision/hash, all 277
NVIDIA files by measured sizes/hashes, and usd-core 26.11. Build-integrity checks
reject corrupted downloads and unsafe ZIP entries.

| Job | State at latest check | Work |
|---|---|---|
| 62721924 | RUNNING, final import checks passed | Original Docker build and image export |
| 62723900 | PENDING afterok 62721924 | Final pinned Docker rebuild, same VM |
| 62722412 | PENDING afterok 62723900 | Exact-image Docker CPU smoke |
| 62722552 | PENDING afterok 62723900 | Saved Docker image to Apptainer SIF |
| 62723043 | PENDING afterok 62722552 | RTX 5000 Ada cameras + one privileged physical shift |

Recheck job states before any restart. VM disk:
`/work/yr111/chute-direct-answer-20261126/datasets/vm-builder-62721924/ubuntu.img`.
Never boot it concurrently. The original build's large layer commits can be quiet
for minutes while actively compressing; silence is not a hang.

Job 62723330 was replaced while pending by 62723900. Buildx 0.30.1 had been installed
after the original legacy build began; the new script explicitly uses
`DOCKER_BUILDKIT=0` to retain the original simulator cache. Both downstream
CPU/conversion dependencies were updated and confirmed before the old queued job
was cancelled. The submitted replacement script is
`datasets/dcc_vm_pinned_build_cached.sbatch` under the DCC task root.

The CPU smoke uses the actual pinned ale_verify result SDK and read_result, runs
the oracle entrypoint as user, checks protected files/assets and root-to-user
Solver communication, and reads real /logs/verifier results. Candidate archive
SHA256: `007efbc08ea6339a5d4ab8c8adbc7ebe92ed9cd4e3ec04fcaba3dc1851b6cbf9`.
It includes 18 SDK/fastjsonschema Python files for author smoke only; preserve these
when rebuilding that archive. They do not belong to the submitted task/image.
CPU smoke is not official ALE validation. SIF GPU smoke does not test ALE UID or
match-lock behavior.

Outstanding grader qualifications: the proprioception-only ProbeLock can reject
visual absolute-target controllers; CpuMeter can omit short-lived/exited worker
CPU. The known cumulative-wall-time bug was fixed and tested, but these broader
issues remain. Do not delete the lock or claim fair difficulty without evidence.
Synthetic-fixture acceptance for a closed-loop task also needs maintainer review.

## UAV: measured reference and current verification

Data is present: all 50 original NPS clips; 51,951 train frames, 1,190 public val
frames, 2,475 held-out frames. Public asset revision:
`c1fca946a5936294a2cf23874040493ac148239b`. Source YX ordering and 1-based time
indices were corrected; exact JPEG overlap is zero. AOT downloads are not used.

Both Docker images were built with real Docker. Current-contract CPU smoke
62722844 passed six cases across all held-out frames, including actual UID/file/
network isolation. It did not evaluate reference accuracy. The deprivileged worker
checks tensor weights, nonempty config and increasing finite training records
before importing agent code. Those checks do not prove training; trajectories and
reproduction remain necessary.

The v2 recipe uses Faster R-CNN/ResNet-18 FPN, frozen BatchNorm and early layers,
sequence-balanced multiscale crops, augmentation and AdamW. Native job 62722505
trained 24,000 steps in 1,155.71 seconds. The task reproduces that schedule and
selects its 12,000-step checkpoint with exact log/source/weight provenance.
Selected weight SHA256:
`3853cd1caf386eef5b6134d130d9c0b1c7c84b9e54f62ca241ff62826d9ac8c5`.

CPU public calibration 62723478 completed successfully: baseline AP50 0.1200373361;
global box scale 1.75 + NMS 0.3 AP50 0.3298975571. A cached follow-up tested larger
scales through 3.0; all degraded AP50. No hidden tuning or label edits occurred.
The packaged postprocessor reproduced every cached box with zero coordinate
difference. Architecture ASTs are unchanged; training differs only in recording
postprocessing metadata. Full selected-source public inference job 62723806 completed in 9m51s
with exit zero; all 1,190 frames reproduce AP50 0.3298975571 and the other metrics
exactly. Inference took 569.89 seconds on CPU. Eighteen host tests and pinned ALE lint passed. Domain lint
correctly reports only the null anchor and missing full_at.

Evidence root:
`/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f/`.
`uav-reference-v2/` contains calibration/results/source audits; `uav-validation/`
contains the current package builder, PR draft, status and GPU-host instructions.
The committed source-only package is 77,560 bytes / 47 files, SHA256
`98f8324ce191455a3af88952963b1a8b995daa423f1c35fec5a71f793ed29ed9`.
It is also staged on DCC at `datasets/uav-submission-3daa2d1.tar.gz`. PACKAGE.json
records its commit/tree/file hashes, and both evaluated model source hashes match
the package. All 11 recorded Docker build inputs remain byte-identical to the
already-built images. Repackage only after committing task changes; older package
hashes must not be described as current.

## Remaining acceptance evidence and execution constraint

1. Finish/collect exact image and reference runs, fix actual failures, freeze packages.
2. Qualify chute physical feasibility, observation lock and timing; declare only
   supported rendering hardware after measured evidence.
3. Run real ALE untouched/oracle/truncated gates under declared GPU resources;
   measure repeated oracle anchors/full_at, including the UAV retraining recipe.
4. Run autonomous frontier agents on the final tasks and archive full trajectories.
5. Refresh final PR drafts with run provenance; only then call either task ready.

The DCC KVM Docker VM lacks GPU passthrough. Native DCC has no subordinate UID/GID
ranges for full Docker root/user isolation. Native CUDA and Apptainer are useful
development evidence, not official ALE GPU gates. An alternative NVIDIA Docker
SSH host has already been requested; do not repeatedly ask the same question.
Keep the goal active while concrete work continues; no blocked audit threshold
has been reached in this continuation.
