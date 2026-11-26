# Grader and reference notes

This candidate has two explicitly different evaluation paths.

## Ordinary controller

`verify.py` owns Isaac Sim and runs `/home/user/submission/run.sh` as the agent's UID through the canonical
`robotics_grader` stdio protocol. Six hidden shifts contain 20 parts each. Scoring state comes from the simulator,
not controller-reported outcomes. A placed part earns 1, a part held for one second earns 0.5, and a lost part earns
0. Each bystander moved more than 5 cm subtracts 0.5 before division by 20. The six shift scores are averaged.

The DCC snapshot imported on 2026-11-26 uses a fixed independent feeding schedule (7–11 s release intervals),
4–7 degree chute slopes, camera latency of 3–6 control steps, physical grasping for ordinary controllers, and
secret-salted shifts. Each requested camera frame costs three additional 30 Hz steps. Timing thresholds are in
`grader_config.json`; its CPU meter and wall-time cap were inherited from that snapshot. The match lock perturbs
61 proprioceptive values. These timing and lock mechanisms still need qualification against visual controllers.
Simulator logs and generated assets go into a root-only private directory.

The raw rollout metric and lock remain unchanged by the direct-answer implementation. Normalization changes:
`anchor.json` now contains a synthetic ceiling of 1.0 with `full_at=1.0`, replacing the historical physical anchor
0.5542/full_at 0.95. Thus, subject to the existing lock, ordinary reward equals raw part_pickup_score. Historical
scores must not be compared as if their normalization and physics were the same.

## Default reference: direct answer, no physical execution

`solution/solve.sh` copies `solution/privileged/ideal_answer.json` to the canonical artifact name
`/home/user/submission/ideal_answer.json`, along with `.oracle_token`. `tests/ideal_answer.py` accepts this format
only when the token hashes to the protected `oracle_token.sha256`. Neither the answer nor token is in the image or
agent setup payload. An unauthorized attempt scores zero. The presence of a token alone does not earn points.

The file contains six lists of 20 independent terminal snapshots: world positions, velocities, four finger-contact
flags, and maximum bystander displacements. The grader regenerates each hidden tote position and applies the same
placement predicates and credit aggregation as `cell_env.py` (factored into `outcomes.py`). Incorrect positions,
non-resting parts, finger contact, moved bystanders, missing events, nonfinite values, or malformed files cannot
receive the perfect raw score. Symlinks, FIFOs and oversized files are rejected.

**These snapshots are synthetic.** They do not describe a collision-free simultaneous packing or a feasible robot
trajectory. Their supplied velocities, contacts and displacement histories are trusted fixture data, not sensor
measurements. This path does not start Isaac Sim, test grasping, test cameras, enforce real-time control, or run the
match lock. Every verdict labels `synthetic_reference=1`, `physical_rollout=0` and states those limitations. A result
of 1 confirms the terminal scoring and artifact plumbing only. It does not establish physical task solvability.
This differs materially from an answer-file calibration task: maintainers must decide whether this oracle is an
acceptable validation fixture for a closed-loop task. Passing lint/validate alone cannot settle that question.

The anchor was bootstrapped with `value=null`, the actual verifier measured raw score 1 over all 120 synthetic
snapshots, and that measured value was recorded. No grader assignment of `reward=1` is used; the normal shared
ratio function calculates the reward. The raw score must be 1 for full credit. The protected answer can be regenerated
with `python tests/review/make_ideal_answer.py`; any change to hidden seeds, salt, geometry, or scoring needs a fresh
fixture measurement. The generator supports this task's current 20-part configuration.

## Optional physical reference

`bash solution/solve_physical.sh` prepares the previous ground-truth controller and removes only the stale
`ideal_answer.json` artifact. The reference token provides privileged state and assisted grasping; motions still run
in the simulator. Its historical anchor is retained in `review/historical_physical_anchor.json` as history, not
calibration for the hardened snapshot. `privileged/reference_main.py` contains a small proprioceptive correction to
satisfy the existing match lock; this must not be presented as visual dependence. Remeasure physical feasibility on
the current snapshot before claiming the task is ready for acceptance.

## Reproduction

Host CPU tests (NumPy, Pillow and pytest; no Isaac required):

```sh
python -m pytest -q tests/review/test_ideal_answer.py tests/review/test_plumbing.py tests/review/test_build_assets.py
```

`test_ideal_answer.py` exercises actual `solve.sh` and `verify.py`: untouched submission zero, synthetic reference
one. It also checks unauthorized and malformed fixtures, partial/wrong answers, scalar boundary conditions, and
regression equivalence of the factored scene RNG and scoring. The common `tests/robotics_grader/` is unmodified.
`review/select_shifts.py` is historical physical-anchor tooling; do not run it to overwrite the current fixture anchor.

For production validation use the pinned ALE engine and the unmodified Dockerfile on a GPU-capable Docker host.
A CPU Docker VM can verify image construction, user imports, asset paths, and the synthetic oracle plumbing, but
cannot validate camera rendering or real controller execution.
