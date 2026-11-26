# Grader notes (for reviewers)

- `verify.py` owns the simulator (`cell_server.py`, run by `/opt/sim/bin/python`) and drives the submission's `run.sh`
  over the kit's stdio wire (`robotics_grader`), one simulator process per hidden shift (`hidden/shifts.json`).
- Metric: `part_pickup_score`, computed by `cell_env.py` from the simulator's own state (part in the tote 1.0, held for
  1 s 0.5, anything else 0, -0.5 per bystander moved more than 5 cm), mean over the shift's 20 parts and over the
  shifts. Nothing the controller prints is a scoring input. The reward is the ratio to `anchor.json`.
- Time: each camera frame asked for advances the cell three more 30 Hz steps (a fixed price). The controller's own
  time must stay within the simulated time elapsed plus 60 s, or the shift ends with what it had earned: a pass/fail
  real-time threshold in the manner of `dual_arm_parcel_sorting_on_conveyor`, never a scored time.
- A part that stands still on the track for 1 s unheld is lost (jam), so a controller cannot stop a part and pick it
  up at rest: it has to be taken while it moves.
- Action: 26 numbers (23 robot command values, 3 camera flags). The match lock perturbs the 61 proprioceptive values.
- The reference (`solution/`) is privileged: `verify.py` attaches ground truth to the observation only when the
  submission holds `.oracle_token`, whose SHA-256 is `oracle_token.sha256`. The token is not in the agent's image.
- `review/test_plumbing.py`: CPU tests of the wire, the packing of frames, the truth gate and the reply parser.
- Physics is PhysX on the CPU (`gm.USE_GPU_DYNAMICS = False`); the GPU renders the cameras. `anchor.json` records the
  measured spread of the reference.
