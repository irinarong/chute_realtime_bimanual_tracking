> Remote update (2026-11-26): Irina merged PR1 at b83042c, then changed main to
> physical-reference mode and H200 (current c657bc8). This branch still preserves the
> explicitly requested synthetic variant. The results below are source-bound to960d2c3,
> not full validation of current main. Source selection is awaiting the user's choice.
> See `validation/REMOTE_MAIN_STATUS.json`. No upstream changes were overwritten.

# Two-task status after upstream merge

Chute merged source:`960d2c32f247443b5a4fb057e6bb15c2dbfe39e4` (parents502f9a5 and upstreambc8ba0c).
Archive SHA256:`1e5f3c80d6a70cd9ec3d34a40257f8a7147d9c13af220f555d66ebce0469d378`;80 source files. `PACKAGE.json` and
`package-integrity.json` are refreshed; earlier packages are archived as pre-merge snapshots.
Branch:`codex/chute-submission-ready` was successfully pushed to the friend's origin
on2026-11-26 after write access was granted. Remote branch initially verified at7d9d241.
Irina merged PR1 atb83042c; main is nowc657bc8 with the physical default restored.
No benchmark task PR has occurred.

## Chute

Adopted the stronger physical reference and its geometry/URDF/modules, updated hidden seeds,
9–13s feed timing, tote/end-stop correction,0.30m pile allowance and bounded actions.
Retained pinned Docker/Kit/Warp fixes, canonical shared grader, corrected CPU accounting,
and the requested direct-answer default. Physical reference is `solve_physical.sh`; its
staging now excludes a stale synthetic answer and retains unrelated user outputs.

Merged-version portable tests:21 passed,3 Linux-only skips. Actual entrypoints:untouched0,
reference1 twice,unauthorized0,wrong0. Fixture regenerated for the new hidden set; anchor
remeasured at1 in author CPU checks. ALE lint and domain lint pass. Upstream physical
anchor0.8583 and reported agent raw0.3375 are kept as attributed separate evidence; not
independently reproduced here or substituted for the synthetic denominator.

Final corrected Docker build62728274 completed2h15m26s/exit0;imageID:
sha256:f2155903863e515cb0cda8c7fa764e4e13a3700636bf2ab8f363d99baab901dd.
Its CPU smoke passes. Conversion62728280 completed24m41s; GPU checks62728568/62728569
completed7m10s/7m34s,all exit0; detailed results collected. The old-source privileged
ordinary-grasp shift placed3/20 (raw0.15); archived visual replay placed0/20 and passed3/45
lock probes. These are historical diagnostics, not results for the new controller.
These tests used runtime17b6d4f. The merge changes no Dockerfile or copied build input, so
reuse the image and verify new staged runtime. Do not restart the image build.

Merged-source author candidate SHA256:
`e29745750a5a04a4ee56f04e0bc53f7602df82e3332884eebb5491e0b448a305`.
All80 task files match960d2c3. New exact-image Docker CPU job62738654 completed
in1m06s/exit0; collected evidence confirms all CPU checks passed. It adds the actual merged physical
entrypoint startup under the agent UID. GPU job62738655 uses the new physical reference
through unchanged run_shift, first hidden shift only. It is an explicitly labelled
same-UID Apptainer author check, not official ALE. It completed9m36s/exit0:
16/20 placed, raw score0.80,60/60 probes passed, no late replies or time-budget failure.
It uses ground truth and assisted grasping; it is not a visual-agent result or six-shift
anchor measurement. Source/dependency/candidate/image identities were checked.
Evidence: `validation/results/merged-physical-62738655/`.

Merged integration PR: https://github.com/irinarong/chute_realtime_bimanual_tracking/pull/1.
Code and reviewable CPU/GPU results are pushed to the friend's repository. Main includes
CPU evidence from the merged PR; the GPU evidence commitf411a0e was pushed after that merge
and is on the codex branch. Current main has a different default reference and GPU contract.

## UAV

Source8c0ae7a; both Docker images built/exported. Complete packaged reference training on
H200 and fixed-checkpoint full hidden CPU Docker inference passed. Public AP50=.3639820;
hidden AP50=.5451401442 on2475 frames across10 sequences. Normalized reward0 is expected
with the still-null official anchor. No tuning or anchor update; author training is not
an autonomous-agent trajectory. See fixed-reference-cpu-62728682/evidence.json.

## Remaining work

Merged checks62738654/62738655 are complete and collected. Remaining: official ALE GPU lifecycle, repeated anchors/full_at and new agent trajectories;
qualify numerical portability and observation-lock fairness. One assisted privileged
physical shift has now been independently reproduced; ordinary camera-based feasibility
and the complete six-shift measurement remain unqualified. Prepare the
one-line upstream GPU-model registry addition before task CI. No upstream task PR is open.
A compatible NVIDIA Docker host was already requested; no repeat question needed.

Evidence root:`/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f`.
`validation/MERGE_REPORT.md` records merge choices. `LIVE_PIPELINE.json` records job state.
Always recheck VM ownership before booting; new source-only smoke uses an exclusive lock.
Old-controller diagnostics remain closed; merged-reference verification is a separate task.
