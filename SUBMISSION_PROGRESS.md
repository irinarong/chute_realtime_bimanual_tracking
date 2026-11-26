# Two-task submission work — active, admission pending

## Scope and source of truth

Complete both the friend's chute controller task and our UAV-to-UAV detector-training
task. The user confirmed that mandatory agent model training applies to UAV only.
Preserve the friend's original DCC experiments. No upstream task PR has been opened.
Never interpret a synthetic oracle reward as physical robot success.

- Chute: this managed worktree, branch `codex/chute-submission-ready`. Task source
  now includes corrected process accounting and its Linux regression tests. The
  current source-only snapshot is identified by `chute-validation/PACKAGE.json`;
  it supersedes the `d0f34e0` package. The original image built as `82248cd7aeaa`;
  its final content-pinned rebuild and exact-image checks remain pending.
- UAV: `/Users/aaronpang/.codex/worktrees/uav-to-uav-task/agentic-robotics-benchmark-review-20261125`,
  branch `codex/uav-to-uav-tracking`. Current committed source is `3daa2d123c6f694f4d2b9e883dc52d5e7f0a97da`,
  including verified public box calibration and reference provenance.
- ALE: `bfb75050aca2c54b45c5ab23bae6028a834a468a`, installed at
  `/tmp/chute-ale-pinned-20261126`. The canonical shared grader is unchanged.

## Chute: measured work and live jobs

Nineteen portable tests, three real Linux process-accounting tests, pinned ALE lint
and domain lint passed. The Linux-only cases skip on macOS; they were run on DCC. Real host entrypoint
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
| 62721924 | COMPLETED, 1h55m34s, exit 0 | Original Docker build and image export |
| 62723900 | RUNNING | Final pinned Docker rebuild, same VM |
| 62722412 | PENDING afterok 62723900 | Exact-image Docker CPU smoke |
| 62722552 | PENDING afterok 62723900 | Saved Docker image to Apptainer SIF |
| 62723043 | PENDING afterok 62722552 | RTX 5000 Ada cameras + one truth-driven friction-only shift |

Recheck job states before any restart. VM disk:
`/work/yr111/chute-direct-answer-20261126/datasets/vm-builder-62721924/ubuntu.img`.
Never boot it concurrently. The original image archive was saved successfully, SHA256
`17bb1312780c222e36a05685e8b44f17a53500b3e1185fb11257545e731b6ad3`.
This is the original image, not the final pinned rebuild. Large layer commits can be quiet
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
SHA256: `bd774a94c269a897cb3a19dab3c7e8e7b572d7bb100bcc804f2dcef90bf984b5`.
It includes 18 SDK/fastjsonschema Python files for author smoke only; preserve these
when rebuilding that archive. `validation/make_candidate.py` does so reproducibly
and records hashes in candidate-manifest.json. This bundle adds an actual agent-UID
run of the Linux CPU tests to the pending exact-image smoke. They do not belong to the submitted task/image.
CPU smoke is not official ALE validation. SIF GPU smoke does not test ALE UID or
match-lock behavior. The GPU smoke now defaults to ordinary physical grasping,
while retaining authorized truth access for the controller. The reset receives no
token; subsequent truth requests do. It asserts `assisted=False`. This separates
physics feasibility diagnosis from privileged assisted-grasp performance.

The refreshed source-only chute package (64 files, 140,564 bytes) is frozen at
`195802c17881c1e30dec636e25329ce6728569ce`, SHA256
`431075a2965f0459c23e6b8418a05722c6e6305b6cc5be69a08b490db668b941`.
It supersedes the old 61-file package. Its 64 archive entries match the manifest.

The process CPU meter was corrected in both private and practice grading. It now
discovers every sample, includes kernel-retained waited-child/grandchild CPU, reads
ancestors before descendants and never refunds consumed time. All three real Linux
worker cases failed against the previous meter and passed against the new one,
including no double charge when a live worker is reaped. Practice also uses a
monotonic wall clock. Full ALE process-isolation/timing qualification still remains.

The proprioception-only ProbeLock can reject visual absolute-target controllers.
A fresh reproduction using the archived four-hour controller found zero carry-phase
action changes under 100 joint perturbations, while head-depth ablation removed the
tracked object and changed the action by 0.184334. Evidence is in
`chute-agent-audit/mechanism_check_v2.py` and `mechanism_result_v2.json`; the older
pose-perturbation result was not valid evidence for that visual claim. This is a
constructed-phase diagnostic, not physical replay or a replacement probe. Do not delete the lock or claim fair difficulty without evidence.
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
