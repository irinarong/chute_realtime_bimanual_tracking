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
  current task base `0f6147d`. The other chat is idle; no message was sent to it.

## Verified progress

Chute: isolated DCC snapshot imported, direct-answer fixture implemented with protected authorization and independent
geometric/scoring checks, prior physical controller preserved, 15 host tests passed. Empty submission gives zero;
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
| 62722412 | Exact-image Docker CPU smoke | after successful 62721924 |
| 62722552 | Convert the saved image to Apptainer for DCC GPU execution | after successful 62721924 |
| 62722564 | Test cameras and one physical privileged-controller shift in that image | after successful 62722552; not formal ALE UID/lifecycle validation |
| 62722505 | UAV stronger reference experiment, 24,000 steps and public validation at 6k/12k/24k | `/work/yr111/uav-to-uav-benchmark-20261125/runs/reference-v2-62722505/` |

UAV experiment sources:
`/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f/uav-reference-v2/`.
They are author experiments and have not replaced the task reference. Changes: frozen BatchNorm, frozen early backbone,
lower backbone learning rate, sequence-balanced sampling, multiscale crops, photometric augmentation. Only training
frames are used for fitting; public validation selects candidates. Do not inspect hidden evaluation results to tune it.

Re-poll live jobs before any restart. The chute dependency installation completed with exit zero; Docker was still
compressing/committing the large layer, with containerd actively using CPU. That is not a hung or failed build.
Buildx installation in this guest was started separately to support the pinned engine's future image preparation.

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
