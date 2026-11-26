# Upstream merge: bc8ba0c

Merged the friend's latest main into the existing submission branch. Adopted the stronger
physical reference (all modules, robot URDF and shape samples), updated hidden shifts,
9–13s release timing, corrected tote/end-stop scoring and bounded commands. Retained the
Docker Kit/Warp fixes, immutable asset pins, shared CPU meter and requested synthetic reference.

`solve.sh` remains the protected direct-answer reference. `solve_physical.sh` now stages
the complete new controller, excludes the synthetic answer, and preserves unrelated outputs.
The fixture was regenerated for the new hidden set and measured at1 twice. Wrong/unauthorized
and untouched submissions remain0. Upstream physical anchor0.8583 is kept separately under
`tests/review/upstream_physical_anchor.json`; it is not the default normalization denominator.

Portable tests:21 passed;3 Linux-only tests skipped locally. Added checks that the physical
entrypoint starts with all its dependencies and cannot accidentally use a stale fixture,
and that extreme commands do not reach physics. Pinned ALE lint passes; canonical grader
files remain identical. Domain lint also passed. Exact-image merged runtime checks subsequently passed:
CPU62738654 validates both entrypoint startup and protected fixture cases; SIF GPU62738655
completed the first privileged assisted physical shift at16/20 (0.80), with60/60 probes
and no late replies. Neither check is official ALE GPU lifecycle validation.

The Dockerfile and every copied build input match build source17b6d4f. Only staged runtime
files and a licence notice changed, so the completed image can be reused without rebuilding.
The old-source Docker/CPU/GPU jobs completed; their scores do not qualify the merged runtime.
Upstream reported controller scores are attributed evidence, not independently reproduced here.

The initial push was denied403 for account yuanboP. After the user granted access,
`codex/chute-submission-ready` was pushed successfully to origin at7d9d241 on2026-11-26.
Remote main remainsbc8ba0c. The merged-source CPU Docker checks passed in62738654;
reviewable result JSON is in `validation/results/merged-cpu-62738654/`.
