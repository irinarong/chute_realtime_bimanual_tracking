
## What this pull request adds

One task folder at `tasks/arm/chute_realtime_bimanual_tracking/`.

Parts of 20 different kinds (YCB household and workshop items) come down an inclined chute one at a time, picking up
speed under gravity (about 0.1 m/s at release, 0.5 to 0.65 m/s where the hand can take them, up to 0.9 m/s at the end;
about 2 s on the chute). The agent, working through a Galaxea R1Pro mobile dual-arm robot that sees only through its
head and wrist cameras, has to take each part **while it moves** and set it down in a tote. The line feeds on a random
schedule of its own (a part every 9 to 13 s) that nothing the controller does can change. What the controller sees is
late (each frame costs 0.1 s and arrives 0.1 to 0.2 s after it was taken), grasping is by finger friction alone, and
every reply has a deadline of 0.1 s of CPU time. Each shift of 20 parts has hidden constants (slope, friction, release
speed, lane, part mass, camera latency, the schedule). The agent leaves a controller (`run.sh`) in
`/home/user/submission/`; training models is allowed, both arms may be used.

## Checklist

- [x] The folder sits at `tasks/arm/chute_realtime_bimanual_tracking/`; `task.toml` has
      `name = "grounded-intelligence-initiative/chute_realtime_bimanual_tracking"`; platform `arm`.
- [x] `ale lint <folder>` passes on the engine commit pinned at `vendor/ale` (bfb7505).
- [ ] `ale validate <folder>` passes. **Not run**: the author's cluster has no Docker. The grading path was run outside
      the engine (see the notes); the validator is asked to run it.
- [x] Difficulty measured with one frontier model (below). It scored well above the 0.5 target: see the note.
- [x] `tests/anchor.json`: `value` 0.8583 is my own measured number (the reference on the 6 hidden shifts over the real
      grading path); `source` says so; `full_at` 0.95 from two independent runs, which agreed shift by shift.
- [x] `tests/robotics_grader/` is the canonical copy from `shared/robotics_grader/`, unmodified.
- [x] Nothing under `environment/setup/payload/` reads the anchor or `tests/`; `practice.py` prints the raw metric only.
- [x] No `__pycache__`, `.ale-cache`, `assets/` or large binaries in the folder (59 files, 2.7 MB).
- [x] `tests/anchor.json` declares `metric` (`part_pickup_score`) and `direction` (`higher`); `verify.py` reports it
      under the same name.

## Frontier-model results

One run, not through `ale run` (no Docker on the author's cluster): gpt-6-astra with the codex CLI 0.166.0 (reasoning
effort high), the full 4 h budget, in a read-only namespace holding the instruction, `~/lab` and
`~/example_controller` only, no access to `tests/` or `solution/`, grading-related environment variables removed. Its
final controller (camera only, physical grasping, 488 lines) graded with `tests/verify.py` on the six hidden shifts:

| shift | 1105 | 1334 | 2162 | 3070 | 3390 | 4191 | mean |
|---|---|---|---|---|---|---|---|
| reference (anchor) | 0.80 | 0.90 | 0.80 | 0.85 | 0.90 | 0.90 | 0.858 |
| gpt-6-astra | 0.10 | 0.35 | 0.15 | 0.375 | 0.55 | 0.50 | 0.338 |

Ratio 0.39, reward 0.338 / 0.858 / 0.95 = 0.41. No late reply, no shift cut short, no bystander moved, 485 to 549
frames asked for per shift. Its code was read: observations and its own files only. Two differences between the lab it
practised in and the graded version, both in its favour at grading: an error in the judge that lost parts set down in
the near half of the tote was fixed after its run had started, and the feed interval was lengthened from 7 to 11 s to
9 to 13 s. It reported 0.475 on two practice shifts of its own.

An earlier version of this task (parts at about 0.2 m/s, no latency, assisted grasping for everyone, feed paced by the
robot) was far too easy: the same model scored 0.93 there. 

## Notes for the maintainers

- **Simulator.** Isaac Sim 6.1 with OmniGibson (BEHAVIOR-1K repository at commit bd049de plus
  `environment/omnigibson-isaac61.patch`). Physics is PhysX on the CPU; the GPU renders the cameras. `gpus = 1`.
- **Relation to `dual_arm_parcel_sorting_on_conveyor`.** That task turns parcels so that a label faces up; its
  difficulty is finding the label and re-orienting. This task reads nothing on the items: its difficulty is tracking a
  moving part from the cameras and taking it in motion.
- **Time.** One 30 Hz step per action; a requested frame costs three more steps and is delivered 3 to 6 steps after
  it was taken (a hidden constant of the shift), stamped with `t_capture`, as in `fault_adaptive_spacecraft_docking` and
  `dual_arm_parcel_sorting_on_conveyor`. Each reply may use 0.1 s of CPU time (three late replies forgiven, the fourth
  ends the shift); total CPU time below simulated time plus 10 s. CPU time, not wall time: on a loaded machine wall time
  made every controller late. Thresholds, never scored times.
- **Reference.** Privileged through a token (`.oracle_token`, hash in `tests/oracle_token.sha256`), which gives it
  three things an agent never has: ground truth, what is coming (schedule, items, accelerations), and the simulator's
  assisted grasp (a part held by both fingers for 0.3 s is attached to the hand). It never looks at a camera.
  `part_pickup_score` 0.858 on the hidden set, identical in two runs shift by shift. It is not a ceiling: it places 15
  to 18 of a shift's 20 parts. It takes the two clamps and the drill by their handles with one hand, never takes the
  cracker box (the one part that needs two hands), and loses the bowl and the scissors in some shifts.
  Most of it was written by gpt-6-astra given ground truth and the brief to build a reference; the rest by hand.
- **Hidden set.** `tests/hidden/shift_selection.json`: 12 candidate seeds drawn once by a fixed rule, each graded once
  with the reference (0.70 to 0.90); the 6 with the highest score are kept and graded a second time.
  `tests/review/select_shifts.py` states the rule and reproduces the files. Graded shifts are drawn with a secret salt,
  so no seed reproduces one in the lab.
- **Against shortcuts.** The simulator's files live in a folder only the grader's account can enter; a shift with parts
  taken and no frame requested is void; the instruction lists what a controller may use. Account separation could not
  be exercised on the author's cluster.
- **What was verified where.** The grading path (`solve.sh` + `verify.py` + the kit's wire) was run against the real
  simulator on the author's cluster (H200, rootless, so the kit's `runuser` step was bypassed in a temporary copy).
  The image was built once from this Dockerfile with rootless podman (28 steps, 43.4 GB); on that cluster a single user
  id is mapped, so apt's `_apt` account, `chown user:user` and the final `runuser -u user` check were changed in a copy.
  Running the simulator on a GPU inside the container, and `ale validate`, have not been done.
- **Licences of fetched assets.** `environment/NOTICE.md`: OmniGibson and the R1Pro model MIT; YCB items and
  Simple_Room from NVIDIA's public Isaac asset bucket (the source `object_finding_and_organizing_on_messy_desk` uses).
  No BEHAVIOR-1K scene or object data.

## What CI will show

`tests/test_task_cards.py` fails until the task has a card in `tasks/cards.toml` (a maintainer's file; a suggestion is
below). `ale lint`, the domain lint over the whole repository and the vendored-kit comparison pass on this branch.

## Suggested card (`tasks/cards.toml`)

```toml
[chute_realtime_bimanual_tracking]
title = "Take moving parts off a chute with an R1Pro"
summary = "Program a mobile dual-arm robot to take 20 different parts off a chute while they accelerate past, seeing them only through late camera frames, and put them in a tote."
platforms = ["arm"]
stages = ["behavior"]
```
