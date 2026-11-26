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
  its final content-pinned image a35d570a7a6f has now built; export completed; exact-image checks remain pending.
- UAV: `/Users/aaronpang/.codex/worktrees/uav-to-uav-task/agentic-robotics-benchmark-review-20261125`,
  branch `codex/uav-to-uav-tracking`. Current committed source is `4a7077eb5cc00b0d9d30373c0493f9ecdf20d3ae`,
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
| 62723900 | COMPLETED, exit 0, 1h03m47s | Final pinned Docker image build and export |
| 62722412 | COMPLETED, exit 0, 47s | Exact-image Docker CPU smoke |
| 62725756 | RUNNING, replaces failed 62722552 | Saved Docker image to Apptainer SIF |
| 62725056 | PENDING afterok 62725756 | RTX 5000 Ada cameras + one truth-driven friction-only shift, allocation preflight |

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
