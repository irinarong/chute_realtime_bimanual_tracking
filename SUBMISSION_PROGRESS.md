# Two-task status after upstream merge

Chute merged source:`960d2c32f247443b5a4fb057e6bb15c2dbfe39e4` (parents502f9a5 and upstreambc8ba0c).
Archive SHA256:`1e5f3c80d6a70cd9ec3d34a40257f8a7147d9c13af220f555d66ebce0469d378`;80 source files. `PACKAGE.json` and
`package-integrity.json` are refreshed; earlier packages are archived as pre-merge snapshots.
Branch:`codex/chute-submission-ready`. Origin push denied403 for yuanboP; no remote write.

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
completed7m10s/7m34s,all exit0; detailed GPU result collection pending.
These tests used runtime17b6d4f. The merge changes no Dockerfile or copied build input, so
reuse the image and verify new staged runtime. Do not restart the image build.

## UAV

Source8c0ae7a; both Docker images built/exported. Complete packaged reference training on
H200 and fixed-checkpoint full hidden CPU Docker inference passed. Public AP50=.3639820;
hidden AP50=.5451401442 on2475 frames across10 sequences. Normalized reward0 is expected
with the still-null official anchor. No tuning or anchor update; author training is not
an autonomous-agent trajectory. See fixed-reference-cpu-62728682/evidence.json.

## Remaining work

Collect old-source final GPU evidence; test merged chute runtime in the completed image;
complete official ALE GPU lifecycle, repeated anchors/full_at and new agent trajectories;
qualify numerical portability and observation-lock fairness. Physical solvability on the
merged task has new upstream evidence but no independent reproduction yet. Prepare the
one-line upstream GPU-model registry addition before task CI. No upstream task PR is open.
A compatible NVIDIA Docker host was already requested; no repeat question needed.

Evidence root:`/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f`.
`validation/MERGE_REPORT.md` records merge choices. `LIVE_PIPELINE.json` records job state.
Both Docker VMs are stopped after completed jobs; always recheck ownership before booting.
Old-controller diagnostics remain closed; merged-reference verification is a separate task.
