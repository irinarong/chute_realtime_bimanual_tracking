## Task

The agent writes a visual controller for a two-arm robot to catch moving parts and place
them in a tote. It receives RGB-D images and proprioception; the privileged verifier runs
six hidden20-part shifts. Source follows the task author's main atc657bc8, with corrected
review notes. The task folder alone belongs in the benchmark PR.

**Admission pending. No benchmark task PR is open.** Integration PR1 in the author's
repository was merged and is separate from benchmark admission.

## Reference and scoring

`solution/solve.sh` stages the real ground-truth controller. Its token authorizes privileged
state and assisted grasping. It does not emit terminal-answer snapshots. The upstream
anchor is0.8583/full_at0.95, attributed to two author six-shift measurements. Independent
official ALE calibration remains outstanding. Ordinary agents receive neither truth nor
assisted grasping. The upstream reported camera-agent raw mean0.3375/reward0.41 is attributed
evidence with account separation bypassed, not our qualifying `ale run` trajectory.

## Build and checks

The Docker image includes the pinned Isaac6.1 Kit and matching Warp1.16, immutable robot
and NVIDIA assets, agent-UID import checks, and preserved licences. Image ID:
`sha256:f2155903863e515cb0cda8c7fa764e4e13a3700636bf2ab8f363d99baab901dd`.
Current source changes no build input, so that image is reused. Runtime setup stays light.

- 7 portable checks pass;3 Linux-only checks skipped locally. ALE/domain/GPU-name lint pass.
- All9 shared grader files match the canonical source.
- Current CPU Docker job62742402 passes missing/malformed submission zero cases, normal
 and reference startup under the agent UID, and all3 Linux process CPU-accounting checks.
- First-shift author GPU check62738655 onRTX5000Ada placed16/20(raw0.80), with60/60 probes
 and no late replies. It uses the same controller/scoring but does not qualify H200/ALE.
- Current H200 source check62742430 and ordinary public-seed camera capture are pending.

The declaration is H200,8CPUs,32GiB in both stages, a4h agent budget and3h verifier cap.
H200 is in the benchmark registry; the previous RTX5000Ada registry patch is superseded.
The cluster's exact-image SIF runs use a single-UID author adapter. Docker CPU checks test
UID separation; neither is an official GPU ALE run.

## Before submission

- [ ] Official untouched0/reference1 ALE validation under the declared resources.
- [ ] Repeated reference calibration and numerical portability.
- [ ] Fresh frontier-agent runs with full trajectories.
- [ ] Observation-lock fairness and ordinary camera-controller feasibility qualified.

Source398d93c,73files; archive SHA256
`2ff077150eae4b2c8f8151145b0fdd9668849db71797713b345ab763cdfd8b26`.
Historical synthetic1 results belong to the retired variant and are not current validation.
