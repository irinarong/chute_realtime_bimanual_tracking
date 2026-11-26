# Current submission status

The user selected the friend's latest main and its physical reference on2026-11-26.
Base: c657bc8. Current task source:398d93ca93bbd02e2d718f35f8902ee3a014ec5d,
tree e78e1786bb33c75fe75c8abf9f241f1d36a9f62b (73 files). Only the review notes differ
from upstream task sources: the actual time allowance is10s, and the image was built
with Docker inside a DCC KVM guest. Controller, scoring and resources are unchanged.

## Friend's physical task

Default `solution/solve.sh` runs the ground-truth controller with assisted grasping.
The synthetic-answer path is removed. Anchor0.8583/full_at0.95 is the upstream author's
six-shift calibration; we have not independently reproduced it through official ALE.
Both stages request H200,8CPUs,32GiB. The GPU registry accepts this name without a patch.
The earlier synthetic variant is preserved in commit7e94d71 and local archive branch
`codex/chute-direct-answer-archive-20261126`; it is no longer the submission candidate.

The existing image f2155903 is reused: Dockerfile and every copied build input match
build source17b6d4f. Author checks never rebuild this unchanged image.

- Current local tests:7 passed,3 Linux-only skips; ALE/domain/GPU-model lint all pass.
- Current Docker CPU check62742402: completed1m00s/exit0. Untouched and malformed wire
  score0; normal and reference startup under the real agent UID pass;3 Linux process
  CPU-accounting cases pass. This does not measure physical reward.
- Earlier first-shift physical check62738655:16/20 placed,raw0.80,60/60 probes,
  no late replies. Same physical controller and scoring functions, but RTX5000Ada,
  the prior source wrapper and a single-UID SIF adapter. It is not current H200/ALE proof.
- Current H200 physical check62742430 is running. An ordinary RGB-D camera capture is
  queued separately; its public seed, empty token and unmodified reset path test what
  a visual controller actually receives. No controller optimization or hidden tuning.

Reviewable CPU evidence: `validation/results/physical-main-cpu-62742402/`.
Author bundle c2955435 contains explicit task provenance and verifies all73 source hashes.
Source package SHA256:2ff077150eae4b2c8f8151145b0fdd9668849db71797713b345ab763cdfd8b26.

PR1 was merged by irinarong, incorporating the image/accounting fixes. Main then restored
the physical reference. This branch now follows that choice and carries validation updates.
No benchmark task PR is open. The old synthetic verdicts do not validate the current task.

## UAV

Source8c0ae7a. Both images built/exported; all50 clips available. Packaged reference
trained24000 steps from generic ImageNet initialization onH200 (62727576), selecting12000.
Public AP50=.3639820. Fixed-model full hidden CPU Docker check62728682 passed with
AP50=.5451401442 on2475 frames/10sequences. Anchor is still null, so normalized reward0
is expected. No autonomous-agent training trajectory or official RTX4090/ALE gate exists.
Do not repeat training or hidden inference without a new cause.

## Remaining admission gates

Official GPU Docker/ALE lifecycle; repeated anchors/full_at under declared resources;
fresh independent agent trajectories (UAV agent must train); numerical portability;
and the joint-only observation-lock fairness review. Local/SIF/CPU checks do not replace
these. A compatible GPU Docker host was requested previously and is still unavailable.
No active goal completion is claimed. Do not restart completed image builds or obsolete
controller diagnostics. Original /cwork/yr111/rax experiments remain untouched.
