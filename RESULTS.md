# Chute task: direct-answer candidate (2026-11-26)

This branch prepares the friend's `chute_realtime_bimanual_tracking` task. It does not change the UAV task.
It is a review candidate, not a claim of upstream acceptance or completed GPU validation.

## Changes

- Base: GitHub `6bb5bc4e7fcf8bddd004cd7b6d9db24df9b39d73`, followed by an isolated copy of the DCC task snapshot
  from `/hpc/home/yr111/research/projects/dynamic-grasp-rsi/ale_tasks/chute_realtime_bimanual_tracking`.
  The import is a separate commit. Active DCC source and experiments were not modified.
- Default reference copies `ideal_answer.json`. The protected evaluator checks its terminal states using shared
  placement and aggregation functions. No simulated robot is run for this reference; all results label this fact.
- Reference raw score and normalized reward are 1.0. The anchor is a measured **synthetic scoring ceiling**.
  Ordinary controllers still execute the physical simulation; their raw metric is unchanged, but the previous
  0.5542/0.95 normalization is replaced by 1.0/1.0.
- The prior privileged physical controller is available through `solution/solve_physical.sh`.
- Fixed inherited shift-time accounting: a reply above the documented wall cap now contributes to the cumulative
  program budget as well as the individual reply deadline. Added a regression test; CPU-meter and match-lock
  qualification remains outstanding.

## Evidence and outstanding checks

| Check | Status |
|---|---|
| Host tests of artifacts, authorization, scoring and simulator protocol | 19 passed |
| Bootstrap with null anchor | raw synthetic metric 1.0 over 120 snapshots; bootstrap reward 0 |
| Actual host solve + verify entry points | untouched 0; synthetic reference 1 |
| Domain lint | passed |
| Canonical grader byte identity | all 9 files match |
| Pinned ALE lint | passed on bfb7505 |
| Exact Dockerfile build with original chown/runuser checks | DCC isolated job 62721924 |
| Docker user/asset/synthetic scoring smoke test | pending image build |
| Official ALE validation with declared GPU resources | pending |
| GPU rollout on this exact image and hardened source | pending |
| Current difficulty run and physical feasibility evidence | pending |

Logs and reproduction scripts are under `validation/` (not part of the submitted task folder). See
`tasks/arm/chute_realtime_bimanual_tracking/tests/README.md` for the precise oracle contract and limitations.

## Submission considerations

The benchmark permits hand-made reference artifacts, but the calibration answer-file precedent does not establish
that a synthetic terminal-state fixture is sufficient for a closed-loop robotics task. This proposal explicitly
bypasses physics and match-lock checks for the privileged fixture. Request maintainer review of that design and
supply separate physical feasibility and difficulty measurements. Do not describe the synthetic score as 100%
physical grasping success.

The historical four-hour visual controller achieved high raw scores on an older, easier environment. Its saved
verdicts failed the match lock, so the previous report's normalized reward 1.0 is not a verified final reward.
Those measurements also predate the imported physical-grasping, latency and independent-feeding changes; they
cannot certify this candidate's difficulty.

The image uses Isaac Sim 6.1, patched OmniGibson at a fixed source commit, the R1Pro robot model, and NVIDIA public
YCB/Simple_Room assets. Robot assets are now fixed to an immutable Hugging Face revision and verified by SHA256; all 277 NVIDIA files have
measured size/hash pins; `usd-core` is fixed at the observed 26.11. Final-image rebuild and smoke checks are pending. The earlier rootless
Podman build modified UID checks; it is not evidence that the original Dockerfile or official validation passed.
