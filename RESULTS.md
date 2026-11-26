# chute_realtime_bimanual_tracking: status and measured results (2026-11-25)

This file is the draft of the pull-request text for the Agentic Robotics Benchmark. The task itself is the folder
`tasks/arm/chute_realtime_bimanual_tracking/`; this file is not part of it.

## What this pull request adds

One task folder at `tasks/arm/chute_realtime_bimanual_tracking/`.

Parts of 20 different kinds (YCB household and workshop items) come down a gently inclined chute one at a time. The
agent, working through a Galaxea R1Pro mobile dual-arm robot that sees only through its head and wrist cameras, has to
take each part **while it moves** and set it down in a tote: a part that is stopped and picked up at rest counts as
lost. Each shift of 20 parts has hidden constants (slope, friction, release speed, part mass). The agent leaves a
controller (`run.sh`) in `/home/user/submission/`; training models is allowed and the lab can be used as a labelled
data source.

## Checklist

- [x] The folder sits at `tasks/arm/chute_realtime_bimanual_tracking/`; `task.toml` has
      `name = "grounded-intelligence-initiative/chute_realtime_bimanual_tracking"`; platform `arm`.
- [x] `ale lint <folder>` passes on the engine commit pinned at `vendor/ale` (bfb7505).
- [ ] `ale validate <folder>` passes. Not run: the author's cluster has no Docker; see the notes.
- [x] Difficulty measured with one frontier model (below). It scored well above the 0.5 target: see the note.
- [x] `tests/anchor.json`: `value` 0.5542 is my own measured number (the reference on the 6 hidden shifts over the real
      grading path); `source` says so; `full_at` 0.95 from two independent runs, which agreed shift by shift.
- [x] `tests/robotics_grader/` is the canonical copy from `shared/robotics_grader/`, unmodified.
- [x] Nothing under `environment/setup/payload/` reads the anchor or `tests/`; `practice.py` prints the raw metric only.
- [x] No `__pycache__`, `.ale-cache`, `assets/` or large binaries in the folder (50 files, 1.8 MB).
- [x] `tests/anchor.json` declares `metric` (`part_pickup_score`) and `direction` (`higher`); `verify.py` reports it
      under the same name.

## Frontier-model results

One run, not through `ale run` (no Docker on the author's cluster): gpt-6-astra with the codex CLI 0.166.0 (reasoning
effort high), 4 h budget, in a read-only namespace holding the instruction, `~/lab` and `~/example_controller` only, no
access to `tests/` or `solution/`. The agent stopped by itself after about 3 h 40 min with a camera-only controller
(depth segmentation, a fitted motion model, grasp points chosen from visible geometry). Graded with `tests/verify.py`:

| shift | 2524 | 3390 | 4191 | 4836 | 7168 | 8803 |
|---|---|---|---|---|---|---|
| part_pickup_score | 0.90 | 0.90 | 0.95 | 0.95 | 0.95 | 0.925 |

Mean 0.929, ratio to the anchor 1.68, reward 1.0. **This is far above the difficulty target.** It was also measured on
the task version before the camera-frame fix of this commit (frames then showed the scene of the previous request);
it has not been repeated on this version. The reference (0.5542) is clearly not a ceiling. Raising the difficulty
(faster parts: the release speed and slope were lowered during development so that the reference could keep up) is the
open item of this task.

## Notes for the maintainers

- **Simulator.** Isaac Sim 6.1 with OmniGibson (BEHAVIOR-1K repository at commit bd049de plus
  `environment/omnigibson-isaac61.patch`). Physics is PhysX on the CPU; the GPU renders the cameras. `gpus = 1`.
- **Time.** One 30 Hz step per action; each camera frame asked for costs three more steps. The controller's own time
  must stay within the simulated time elapsed plus 60 s, or the shift ends with what it had earned: a pass/fail
  real-time threshold in the manner of `dual_arm_parcel_sorting_on_conveyor`, never a scored time.
- **Relation to `dual_arm_parcel_sorting_on_conveyor`.** That task turns parcels so that a label faces up; its
  difficulty is finding the label and re-orienting. This task reads nothing on the items: its difficulty is tracking a
  moving part from the cameras and taking it in motion.
- **Reference.** Privileged: `verify.py` attaches ground truth to the observation only when the submission holds
  `.oracle_token` (hash in `tests/oracle_token.sha256`). It never looks at a camera. It is a ground-truth controller, not
  a ceiling: `part_pickup_score` 0.5542 on the hidden set (10 to 12 of 20 parts in the tote per shift). It leaves alone the
  parts wider than the gripper opens and still loses parts in motion. Two independent grading runs gave the same score
  on every one of the 6 shifts (physics on the CPU is repeatable on one host); a shift takes about 4 minutes of
  simulated time and the reference 20 to 30 s of its own time, far inside the real-time rule.
- **Hidden set.** `tests/hidden/shift_selection.json`: 12 candidate seeds drawn once by a fixed rule, each graded once
  with the reference; the 6 with the highest score are kept (`tests/review/select_shifts.py` states the rule and
  reproduces the files). The 12 scores ranged from 0.0 to 0.60.
- **What was verified where.** The grading path (`solve.sh` + `verify.py` + the kit's wire) was run against the real
  simulator on the author's cluster (H200, rootless, so the kit's `runuser` step was bypassed in a temporary copy).
  The image was built once from this Dockerfile with rootless podman (28 steps, 43.4 GB); on that cluster a single user
  id is mapped, so apt's `_apt` account, `chown user:user` and the final `runuser -u user` check were changed in a copy.
  Running the simulator on a GPU inside the container, and `ale validate`, have not been done.
- **Licences of fetched assets.** `environment/NOTICE.md`: OmniGibson and the R1Pro model MIT; YCB items and
  Simple_Room from NVIDIA's public Isaac asset bucket (the source `object_finding_and_organizing_on_messy_desk` uses).
  No BEHAVIOR-1K scene or object data.

## Suggested card (`tasks/cards.toml`)

```toml
[chute_realtime_bimanual_tracking]
title = "Take moving parts off a chute with an R1Pro"
summary = "Program a mobile dual-arm robot to take 20 different parts off an inclined chute while they move, seeing them only through its cameras, and put them in a tote."
platforms = ["arm"]
stages = ["behavior"]
```
