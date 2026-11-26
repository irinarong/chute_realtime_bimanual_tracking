# Two-task submission work — active, not yet ready

## Scope

Complete the friend's chute task and our UAV-to-UAV detector-training task through genuine ALE submission gates.
Keep direct-answer reference results distinct from physical robot success. The UAV agent must actually train its
model and leave reproducible source, checkpoint and training records. The user clarified that mandatory model training applies to UAV-to-UAV. The friend's task
continues to allow controller development, with optional model training.

## Authoritative working trees

- Chute: this managed worktree, branch `codex/chute-submission-ready`.
  The initial async managed worktree creation eventually completed. It was fast-forwarded to the actual work from
  the temporary visualization worktree; new changes belong here. The original visualization checkout is a historical
  copy, not the current head.
- UAV: `/Users/aaronpang/.codex/worktrees/uav-to-uav-task/agentic-robotics-benchmark-review-20261125`,
  current task source `7fae778` (training artifact validation). The other chat is idle; no message was sent to it.

## Verified progress

Chute: isolated DCC snapshot imported, direct-answer fixture implemented with protected authorization and independent
geometric/scoring checks, prior physical controller preserved, 19 host tests passed. Empty submission gives zero;
two actual host solve/verify runs give full synthetic reference reward. Pinned ALE lint, domain lint, and canonical
shared-grader byte identity passed. No claim of physical task success is inferred from the synthetic reference.

UAV: original agent and verifier Docker images already built under real Docker in a KVM guest. Public train/val data
are frozen and hosted; verifier-only frames are reconstructed in its separate image. Existing CPU container checks
cover missing/truncated artifacts, all hidden frames, user permissions and denied Internet sockets. The native
reference generalizes poorly and no anchor was fabricated. Public annotation overlays and per-clip box-size statistics
were inspected again; no obvious annotation displacement was found in the sampled frames.

## Live DCC work

| Job | Work | Dependency / location |
|---|---|---|
| 62721924 | Build original chute Dockerfile, retain chown/runuser checks, export image | `/work/yr111/chute-direct-answer-20261126/datasets/vm-builder-62721924/` |
| 62723330 | Rebuild the final content/version-pinned Dockerfile in the original VM | after successful 62721924 |
| 62722412 | Exact-image Docker CPU smoke | after successful 62723330 |
| 62722552 | Convert the saved image to Apptainer for DCC GPU execution | after successful 62723330 |
| 62723043 | Test cameras and one physical privileged-controller shift in that image | after successful 62722552; not formal ALE UID/lifecycle validation |
| 62722844 | COMPLETED: UAV current-contract Docker CPU smoke, six cases, all 2,475 hidden frames | `/work/yr111/uav-to-uav-benchmark-20261125/datasets/vm-verify-62722844/` |
| 62722505 | COMPLETED: UAV 24k training; public AP50 7.08% / 12.03% / 11.91% at 6k/12k/24k | `/work/yr111/uav-to-uav-benchmark-20261125/runs/reference-v2-62722505/` |

UAV experiment sources:
`/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f/uav-reference-v2/`.
They are author experiments and have not replaced the task reference. Changes: frozen BatchNorm, frozen early backbone,
lower backbone learning rate, sequence-balanced sampling, multiscale crops, photometric augmentation. Only training
frames are used for fitting; public validation selects candidates. Do not inspect hidden evaluation results to tune it.

UAV now validates a nonempty tensor state dictionary, a nonempty config object and finite, increasing step/loss
records in the deprivileged worker, before importing submitted Python. Public practice uses identical checks.
All 18 host tests and pinned ALE lint passed. Domain lint still correctly fails on the unmeasured anchor/full_at.
Format checks are not proof of training; archived agent trajectories and reproduction remain required.
The experiment export helper keeps the original 24k schedule when selecting a 6k/12k snapshot, and exports an
exact log prefix plus original full log and artifact hashes.

Re-poll live jobs before any restart. The chute dependency installation completed with exit zero; Docker was still
compressing/committing the large layer, with containerd actively using CPU. That is not a hung or failed build.
Buildx installation in this guest was started separately to support the pinned engine's future image preparation.

The first H200 rendering smoke job 62722564 was cancelled while queued and replaced with 62723043 on
RTX 5000 Ada; Isaac camera testing needs an RTX-capable GPU. Only this task's queued validation was changed.
UAV tiled-inference experiment 62723029 evaluates 512/768-pixel crops of each current RGB frame on public val.
Tiled evaluation completed: AP50 10.88% at 512 pixels and 12.72% at 768 pixels. Job 62723393 (H200 development inference) compares
a small fixed grid of global box expansion/NMS on public validation, retaining all public predictions for diagnosis. Its first attempt 62723142 failed before inference because the
author helper passed a relative worker path; the corrected helper uses absolute paths. This was not a model failure. RTX job 62723201 was then cancelled
while queued and replaced by 62723393 to avoid waiting for the RTX rendering allocation. Its report records
the actual GPU and includes an unchanged baseline on that same host; this is still not official ALE validation.
The GPU diagnostic job 62723003 was replaced by a short CPU diagnostic inside our existing 62721924 allocation.
CPU diagnosis completed on 24 selected public frames. See `uav-reference-v2/public-predictions.json`,
`val-predictions-a.jpg`, and `val-predictions-b.jpg` in the visualization directory above. It shows detected targets,
some tight predicted boxes and high-confidence false positives; it does not establish a dataset error or a full
validation result. The 12k checkpoint was exported to DCC `runs/reference-v2-62722505/export-12000/`, preserving
its 24k training schedule, exact tensor-file bytes and the corresponding 12k log prefix. It is not promoted yet.
`uav-validation/artifact-contract-validation.json` and `cpu-smoke.json` hold current Docker/host evidence.
Native reference results remain author development results, not autonomous agent training or ALE validation.

## Remaining acceptance evidence

- Chute exact build and CPU/GPU smoke outcomes; fix real failures without bypassing UID checks.
- Assess the privileged physical controller on the hardened DCC snapshot; synthetic reward cannot establish feasibility.
- Review/fix visual match-lock and timing behavior using actual controller traces before declaring fair difficulty.
- Strengthen UAV reference, promote only measured improvements, and retain exact source/checkpoint provenance.
- Actual autonomous agent training/difficulty runs, with full trajectories and reproducible checkpoints.
- Repeated official ALE oracle runs, genuine untouched/oracle gates, calibrated UAV anchor/full_at, and all domain gates.
- Final source-only packages, hashes, reviewer instructions and PR drafts for both tasks. No GitHub task PR has been opened.

## External execution constraint

The verified DCC KVM Docker guest has no GPU passthrough. DCC's unprivileged host account lacks subordinate UID/GID
ranges required for full Docker root/user isolation. Native CUDA and Apptainer runs are useful development evidence,
but must not be reported as official ALE GPU validation. The user has been asked for an alternate NVIDIA Docker SSH
host while independent work continues. Do not narrow the completion standard because that environment is missing.

## Asset pinning update

Final Docker source adds `fetch_robot_assets.py`, immutable robot zip revision/SHA256, `nvidia-assets.json` with
277 measured NVIDIA file hashes, and `usd-core==26.11`. Three new build-integrity tests passed (19 total host tests).
The exact original build 62721924 supplies cached layers; new job 62723330 rebuilds with pins and atomically replaces
the exported archive. CPU smoke and SIF conversion must wait for 62723330, never boot the same qcow2 concurrently.
The original and final build logs/image identities remain distinguishable. Do not report the final Dockerfile as
built until the pinned rebuild succeeds. The metadata/source bundle was refreshed after the NOTICE/README edits; both downstream dependencies were confirmed
by `scontrol show job` as afterok:62723330.

Current frozen source/package: chute branch `769cafb` (plus this status update); UAV branch `7fae778`.
The latest UAV source-only package and PR draft are in the adjacent `uav-validation/` directory, with SHA256
`55ffac738524126bf1382d040b0b5f840637991376cbf96f9d0321b33492770f`. They remain admission-pending and retain
the old task reference until experimental postprocessing is selected and promoted with a working training recipe.
