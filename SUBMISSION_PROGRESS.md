# Two-task submission work — active, admission pending

## Latest verified checkpoint — 2026-11-26 (supersedes older job descriptions)

- Current task sources: friendc3521f9, UAV8c0ae7a. Both exact source packages
  pass ALE lint and preserve the nine canonical grader files. No upstream PR.
- UAV full image training62727576 completed all24k training steps and exported
  step12k as972cb29f…; all1190 public frames give AP50=.3639820 in53.99s.
  Job completed21m10s/exit0; full logs/source/helper verified and collected under
  uav-validation/full-image-training-62727576. H200 author evidence only.
- Friend62727626 passed CUDA/Vulkan and OmniGibson import but exposed a real
  image bug: missing omnigibson_6_1_0.kit referenced by the compatibility patch.
  Sourcec3521f9 includes the exact original DCC file and an agent-UID launch-file
  check. CPU regression62728007 fails on old image and passes with the file.
- Kit-only imagea318a2a9 built and passed CPU smoke in62728039; export is running.
  GPU overlay62727985 then exposed mixed standaloneWarp1.19 and IsaacWarp1.16
  imports. Current sourcec3521f9 still needs its final dependency correction.
- Corrected Warp1.16 wheel preparation62728189 passed; GPU diagnostic62728194
  is queued. Its overlay is author evidence, never exact-image qualification.
- Known-broken downstream jobs62728071/74/76 were canceled while pending.
  Recreate conversion/GPU/visual jobs only for the corrected final runtime.
  No original /cwork/yr111/rax experiments were changed.
- Official ALE GPU lifecycle, repeated anchors and fresh frontier trajectories
  remain missing; the compatible NVIDIA Docker host request remains unanswered.


## Scope and source of truth

Complete both the friend's chute controller task and our UAV-to-UAV detector-training
task. The user confirmed that mandatory agent model training applies to UAV only.
Preserve the friend's original DCC experiments. No upstream task PR has been opened.
Never interpret a synthetic oracle reward as physical robot success.

- Chute: this managed worktree, branch `codex/chute-submission-ready`. Task source
  now includes corrected process accounting and its Linux regression tests. The
  current source-only snapshot is identified by `chute-validation/PACKAGE.json`;
  it supersedes the `d0f34e0` package. The original image built as `82248cd7aeaa`;
  its final content-pinned image a35d570a7a6f has now built; export completed; exact-image checks remain pending.
- UAV: `/Users/aaronpang/.codex/worktrees/uav-to-uav-task/agentic-robotics-benchmark-review-20261125`,
  branch `codex/uav-to-uav-tracking`. Current committed source is `4a7077eb5cc00b0d9d30373c0493f9ecdf20d3ae`,
  including verified public box calibration and reference provenance. Current source is now 8c0ae7a after the licence-layout correction below; runtime and Docker build inputs are unchanged.
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
| 62723900 | COMPLETED, exit 0, 1h03m47s | Final pinned Docker image build and export |
| 62722412 | COMPLETED, exit 0, 47s | Exact-image Docker CPU smoke |
| 62726037 | RUNNING, local-disk scratch | Saved Docker image to Apptainer SIF |
| 62725056 | PENDING afterok 62726037 | RTX 5000 Ada cameras + one truth-driven friction-only shift, allocation preflight |

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
Solver communication, and reads real /logs/verifier results. Current candidate archive
SHA256: `cb604cff5b9bd683039f2d538a798977a2e6a27e1a4307b2827cd38cb1e33eca`.
It includes 18 SDK/fastjsonschema Python files for author smoke only; preserve these
when rebuilding that archive. `validation/make_candidate.py` does so reproducibly
and records hashes in candidate-manifest.json. This bundle adds an actual agent-UID
run of the Linux CPU tests to the pending exact-image smoke. They do not belong to the submitted task/image.
CPU smoke is not official ALE validation. SIF GPU smoke does not test ALE UID or
match-lock behavior. The GPU smoke now defaults to ordinary physical grasping,
while retaining authorized truth access for the controller. The reset receives no
token; subsequent truth requests do. It asserts `assisted=False`. This separates
physics feasibility diagnosis from privileged assisted-grasp performance. The
optional physical controller now selects its existing finger-pressure/gap fallback
when truth declares `assisted=False`, rather than waiting for an unavailable
attachment. This branch still needs the queued physics run; no score is claimed.

The refreshed source-only chute package is identified by
`chute-validation/PACKAGE.json`. It supersedes the old 61-file package and the
intermediate `195802c` archive; the next package includes the physical-grasp
fallback selection. Verify all archive entries against the manifest when freezing.
Docker build contexts are unchanged by the CPU accounting and optional controller
edits; downstream smokes read the updated candidate at their own start.

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

Both Docker images were built with real Docker. Their original guest disk was later
quarantined after filesystem/containerd corruption and cannot serve as the delivery
artifact; a healthy rebuild/export is in progress (62725367). Current-contract CPU smoke
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
The current source-only package is 82,488 bytes / 50 files, SHA256
`954e33f605c4ead0f216c78085aad58a3b28256a6911fa0a2b6a3a23790111aa`.
It is also staged on DCC at `datasets/uav-submission-4a7077e.tar.gz`. PACKAGE.json
records its commit/tree/file hashes, and both evaluated model source hashes match
the package. The original 11-input comparison covers 3daa2d1. The new verifier licence COPY
changes its Dockerfile and adds a build input; the new build must confirm this image. Repackage only after committing task changes; older package
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

## Latest contract review

The current 20-item shift has two bystanders: the catalogue is exhausted, so the
scene's spare-item branch contributes none and its two sampled duplicates remain.
The instruction had incorrectly promised three; it now agrees with the scene,
fixture and asset notice. Camera flags now explicitly request delayed frames, and
the prompt explains that all cameras requested by one reply are captured together
after the total camera cost. No scene, reward or latency behavior was changed.

Pinned build 62723900 is live and reused simulator/OmniGibson layers. Its immutable
robot ZIP passed revision, size/hash and safe-extraction checks; the asset layer is
still being finalized. No final-image success is inferred from that partial step.

The standalone task source package now retains the original MIT licence and
copyright notice, which previously existed only at repository root and would
have been omitted by task-folder packaging. The canonical robotics_grader remains
byte-identical; its Apache-2.0 licence and upstream NOTICE are included separately
under task/third_party, with attribution in task/NOTICE.md. No image inputs or
runtime behavior changed.

## Collected Docker smoke and GPU allocation checks

The original image CPU smoke passed with current task source and pinned SDK:
three Linux accounting tests under agent UID, root-to-user Solver, untouched zero,
synthetic oracle one twice, unauthorized zero and wrong-answer zero. Its archive
was copied from the guest to DCC and local evidence with matching SHA256
`0b586159dd80367dffe3c99afc75002370361a5227c51885df47900b0bfeb443`.
See `chute-validation/original-smoke-evidence.json`. This does not replace the
queued final-image smoke or establish any physical control result.

GPU job 62723043 was held before execution, then replaced by 62725056 and cancelled.
The replacement checks actual device open permissions and resolves the assigned
Slurm device to its NVIDIA UUID. DCC confirms ConstrainDevices=yes; probe 62725034
assigned physical GPU 4 with CUDA_VISIBLE_DEVICES=0, and open() rejected the other
seven devices with EPERM. The script preserves the assigned UUID through cleanenv,
restricts the Vulkan loader to the NVIDIA ICD, then requires CUDA and Vulkan to
expose the same single GPU before Isaac starts. This is a validation-infrastructure
change; the submitted task/source package and candidate archive are unchanged.
Container-side UUID verification and rendering results remain pending.

## UAV image recovery

Rechecking DCC storage found the original UAV builder disk was already quarantined
after documented concurrent-VM writes (62722692 and 62722844). Do not boot
`datasets/vm-builder-62720446/ubuntu.img.quarantined-20261126` or reuse its old
launchers. Historical build and CPU-smoke logs survive, but the image store is not
a verified deliverable. Datasets, native training and evaluation results are outside
that VM and remain available.

Fresh job 62725136 uses source archive 3daa2d1 on its own new 200 GB sparse VM disk,
an atomic ownership lock, cached official base archives and the recorded QEMU
digest. It rebuilds both unchanged Dockerfiles, reruns the six current-source CPU
contract/isolation cases, streams both Docker image archives to host storage with
SHA256 records, and gracefully shuts down the guest. Its script/provenance are in
`uav-validation/dcc_vm_rebuild_export.sbatch` and `image-recovery.json`. This is not
a GPU ALE gate; completion and export integrity still need checking.


GPU smoke now preserves startup checks and per-1000-step outcome snapshots, labels
partial progress explicitly, and only prints its completion marker after all parts
finish. This avoids confusing a horizon-limited or timed-out rollout with a complete
shift. Only its author helper changed; the 89-file candidate was refreshed while
preserving all 18 SDK files, verified on DCC, and installed atomically. The previous
candidate 74739d9 is retained as datasets/candidate-74739d9.tar.gz and remains the
identity of the collected original-image CPU smoke. The new candidate is cb604cff;
task-only submission packages and Docker image inputs are unchanged.


UAV licence fix 4a7077e retains the original benchmark Apache LICENSE/NOTICE in the
standalone task and embeds the source BSD dataset notice in the separate verifier
image. It changes no training, inference, metric or canonical grader code. The
50-file package was rechecked and uploaded with its SHA256. Job 62725136 was
cancelled during VM preparation and replaced by 62725367 on a new disk because of
this concrete Dockerfile change. The new script additionally compares the embedded
licence byte-for-byte against source. Do not reuse the cancelled job's VM or confuse
its source 3daa2d1 with the corrected candidate. See current image-recovery.json.


Final chute Docker build completed in live job 62723900 as
`sha256:a35d570a7a6f8b5effd0f32fae0488db7ad3a3585b25bd16569fd981460ff1b0`
(21,689,855,559 bytes, linux/amd64). All asset and agent-UID Isaac imports passed.
The job is streaming its archive to chute-task-image.next.tar.gz; export/hash and
subsequent checks remain pending. The inspect output is preserved as
chute-validation/pinned-docker-image.json. Watcher exec session 9721 now follows
62723900, 62722412, 62722552, 62725056 and corrected UAV build 62725367;
old watcher 38785 exited after the intentional cancellation of 62725136.


Final image export completed: job 62723900 exited zero in 1h03m47s. Current archive
is 20,311,928,397 bytes, SHA256
`83eb182723aa03abfd482635d6b03487131e8e3a5547c303e550407875354ea4`.
The original archive at this shared pathname has been replaced; do not use its old
17bb1312 hash to identify the current file. Build log, inspect and hash records are
collected under chute-validation/pinned-*. CPU smoke 62722412 and SIF conversion
62722552 are now RUNNING. GPU 62725056 still depends on conversion. These are not
ALE GPU admission results.


Final-image CPU smoke 62722412 completed with exit zero in 47 seconds. Its archive
SHA256 is 1ae2d922f8be0866a092f6659b23c11207d74748493ea3bc889952691978f115;
local archive hash and inspected image ID both match. Untouched/unauthorized/wrong
answers score zero, synthetic oracle one twice, root-to-user Solver and three Linux
CPU tests pass. See chute-validation/final-image-smoke-evidence.json. No physical
result or official ALE gate is inferred from this.

SIF conversion 62722552 FAILED (255) with gzip invalid header. The outer archive
has a valid gzip header and its SHA256 check passed; its tar begins with OCI blobs.
Replacement 62725756 first decompresses/CRC-checks the archive, verifies the config
against the exact built image ID, detects Docker versus OCI transport, then converts
and installs the final SIF atomically. GPU job 62725056 now depends on 62725756;
the dependency update was verified. Do not relaunch the completed image build.
Watcher 9721 exited on the observed conversion failure; it is no longer active.


Conversion 62725756 passed gzip CRC/decompression and wrote the raw archive/hash,
then stopped at our overly strict config-ID check. Docker's containerd store reports
an OCI manifest digest as image Id/Descriptor, not the config digest. The corrected
inspector independently verified the manifest digest equals a35d570a7a6f, config
05aa3a3b matches the saved config, and rootfs diff_ids/runtime config match docker
inspect. It passed against the actual raw archive and selected oci-archive. There
are 38 mixed plain/gzip Docker/OCI layers; use their native OCI metadata.
Conversion 62725860 reuses and rechecks the completed raw archive instead of
repeating decompression. GPU 62725056 now depends on this job. The raw file remains
at datasets/apptainer-convert-62725756/chute-task-image.tar. Watcher 64051 exited on
the previous conversion failure. No Docker rebuild or CPU re-test is needed.


OCI conversion 62725860 verified format/identity and reached extraction, then failed
because /work NFS refuses removal of inherited system.nfs4_dacl xattrs. This is an
extraction-scratch issue. Replacement 62726037 uses a unique node-local /tmp tree
for rootfs/cache and checks for 80 GiB free local disk (observed 7 TB available).
It reuses the checked raw archive; GPU 62725056 now depends on 62726037. No Docker
image or task inputs changed. Earlier high conversion memory was file cache
(about 22 MB anonymous memory, no OOM events), so no memory-policy change was made.

Diagnostic 62726049 is queued after the basic GPU smoke. It replays the archived
six-file visual controller unchanged through the current task's run_shift and
canonical Solver/ProbeLock, with current CPU/deadline accounting and no truth
access or assisted grasping. Only Solver._spawn is adapted for the same-UID author
container; clear_account=False and a nonroot guard prevent host-account clearing
or root controller execution. This is explicitly not ALE isolation or a fresh
frontier-agent run. Its archive (8 files) SHA256 is
167c4c57f7272687b07cfe54969060eca4a64f71b99f665b76c0d628b72474cc.
The current probe is preserved for measurement; there is no untested lock removal.


## Current package correction: licence placement

Fresh pinned ALE lint rejected the recently added top-level licence files in both
tasks. Friend source 3acb84b moves its MIT/Apache notices under tests/, and UAV
source 8c0ae7a moves Apache notices under tests/licenses and fixes source data-card
paths. Both exact sources now pass ALE lint; friend domain lint also passes and
UAV domain lint reports only missing measured anchor/full_at. The package builders
now enforce lint before writing an archive, avoiding stale pre-edit lint evidence.

Current source-only archives are friend 3f8192dfeb6803517c48d6f5dbc113ec162113060a47a9521dee2521a8a83b67
(68 files, 146439 bytes) and UAV a57f2b0b37f47cb6f77055126ef4ac9b1c710d17877fea55e0b860bb1e8cd8bb
(50 files, 82818 bytes). Both were checked against manifests and uploaded under
commit-specific DCC names. Prior local archives are preserved in snapshots/.
Nine grader files remain canonical, all runtime sources are unchanged, and all
Docker build inputs match the jobs already in progress. See each task evidence
directory licence-layout-verification.json. No image rebuild, repeated training
or candidate replacement was needed; live jobs retain their own source/candidate
identities. UAV agent image finished building; verifier image build is in progress.
Friend OCI conversion reached SIF creation on node-local scratch.


UAV62725367 completed with exit0 in1h11m50s. Both images and archives are now
verified build outputs: agent archive21,878,762,372bytes, SHA256
2b131f7e4b8182d9f84148b25a0281a69a63756418fbaabb8875a6c9529dc133;
verifier archive4,652,762,722bytes, SHA256
4717ca49b9bf30c80383dfb69612336d6d4d9a54666e40df4bf6d9ac37d876e4.
The evidence collector checked terminal scheduler state, all completion markers,
six CPU cases and exact image identities. No archive download or official GPU
validation is claimed. Do not rebuild these images absent new image-input changes.

Friend conversion62726378 is still compressing. Its actual mksquashfs command
contains -mem8G/-processors8; a later observation found3.5GBRSS and1.4GB output
with noOOM. This is confirmed progress past the earlier failure behavior, not yet
a completed SIF or GPU feasibility result.


Final UAV image CUDA compatibility is now being checked separately: conversion
62726871 runs from the completed hash-pinned Docker archive, with local scratch,
8GiB compression buffers and uncompressed data blocks for author runtime use.
Dependent GPU62726873 checks allocated CUDA UUID, two forward/backward/optimizer
steps on public training data, then full1190-frame inference using the immutable
previously trained reference. It preserves per-worker stderr and records public
GPU/CPU deltas. This is same-UID Apptainer development evidence, not official ALE,
new full training or an autonomous agent. Source-only task packages are unchanged.
See uav-validation/image-gpu-plan.json for identities and scripts.

Friend62726378 is still compressing under its bounded8GiB/8CPU configuration;
latest measured output exceeded6.2GB with4.6GBRSS and noOOM. Keep its live handle.
If GPU62725056 later reports startup/camera/truth checks passed while the physical
shift continues, visual62726049 may be released concurrently by changing its
dependency to the completed converter62726378, avoiding an unnecessary full-shift
wait while retaining verified image startup. Do not release it before that evidence.


Friend SIF conversion62726378 COMPLETED with exit0 in30m45s. Final SIF SHA256
is6e2ebf77a65e11d7aa3a143aeda5169b7310526fac6eefa29c4cc6cca06f9ef6; evidence
in chute-validation/final-sif-62726378/evidence.json ties it to the final Docker
image. GPU62725056 is eligible but both healthy RTX5000Ada nodes had all GPUs
allocated. Cleared fixed-node restrictions on62725056 and62726049, retaining
the same GPU type. The scheduler estimated09:42ET for the physical job; that
is only an estimate and must be requeried, not a reason to restart or mark failed.

UAV conversion62726871 reached SIF creation. Its pending GPU check62726873 was
changed via scontrol to scavenger-gpu, gpu:2080:1, with no fixed-node restriction,
because a RTX2080 allocation was free. The helper verifies the assigned CUDA
UUID and records the actual device; task.toml and declaredRTX4090 requirements
are unchanged. This is development compatibility evidence only; no reference
training/full_at or official ALE acceptance is inferred. Override recorded in
uav-validation/image-gpu-plan.json.


UAV final-image GPU check62727211 completed on H200 in1m22s with exit0. Two real
CUDA optimizer steps passed, and immutable reference weights produced AP50
0.32848809584577504 over all1190 public frames in62.88s. CPU baseline was
0.32989755713734764; retain this small device difference, never overwrite the
missing official anchor with it. final-gpu-62727211/evidence.json records scope
and identities. SIF conversion62726871 also completed in9m59s.

GPU preflight corrected a concrete bug: Slurm GRES index6 need not be NVIDIA
minor3. The helper keeps exactly-one assignment/device restrictions, maps the
cgroup-permitted device to NVML UUID and verifies it inside CUDA/Vulkan. An
observed H200 run now passes; multiple devices and assignments still reject.
The RTX2080 attempt62726873 also encountered an actual NVML unknown-device error
and was not reused. Its mapping diagnostics are retained under gpu-map-62727122.

Friend GPU62725056 failed Vulkan initialization before simulation. CPU driver
probe62727192 identified an absolute ICD path pointing at absent/usr/lib64; the
actual injected library is under/.singularity.d/libs. The resolved ICD loaded
successfully in CPU probe62727294. Only author launch helpers changed, preserving
host ICD and submitted Docker/task source. Corrected GPU probe62727328, physical
smoke62727329 and dependent visual replay62727330 are now queued. Old probe
62727090 failed with the original path; old pending visual62726049 was cancelled.
Do not claim actual rendering or physical feasibility until the new jobs run.
