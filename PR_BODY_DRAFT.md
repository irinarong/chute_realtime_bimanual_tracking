## What this pull request adds

`tasks/arm/chute_realtime_bimanual_tracking/` asks an autonomous agent to build a visual controller for a two-arm robot catching moving parts from a chute and placing them in a tote. The submitted `run.sh` and supporting code receive RGB-D camera observations and proprioception; a separate privileged simulator computes outcomes over six hidden shifts.

**Admission pending. This is a local PR draft. No upstream PR has been opened.**

## Checklist

- [x] Folder, task name and `arm` platform agree.
- [x] `ale lint` passes on pinned engine `bfb75050aca2c54b45c5ab23bae6028a834a468a`.
- [ ] Official `ale validate` records untouched reward 0 and oracle reward 1 under the declared GPU resources.
- [ ] Frontier-model difficulty is measured on this version and complete trajectories are archived.
- [ ] Official ALE oracle records support the anchor and `full_at`. Current measurements cover a synthetic fixture only.
- [x] All nine vendored `robotics_grader` files match the canonical package.
- [x] Practice grading reports raw physical metrics and does not read the private anchor or hidden tests.
- [x] The task directory contains source and small fixtures, without model binaries or downloaded simulator assets.
- [x] Platform, positive metric direction and reported metric name agree.

## Reference design requiring maintainer review

At the contributor's request, the default reference is a protected direct-answer fixture. It writes terminal snapshots and a reference-only authorization token. The verifier reconstructs hidden tote layouts and applies the same placement predicates and credit aggregation used by the physical simulator. Wrong or unauthorized answers score zero; the shared normalization computes the result.

Actual host runs measured synthetic reference reward 1 twice and untouched reward 0. These are **not official ALE validation records and not physical success rates**. Every fixture verdict carries `synthetic_reference=1` and `physical_rollout=0`. The supplied terminal positions, velocities and contact states do not prove a feasible trajectory or successful grasp. This differs from recovering fixed calibration parameters: acceptance of this reference design requires a maintainer decision and separate physical feasibility evidence.

The previous privileged physical controller remains available as `solution/solve_physical.sh`. It uses ground-truth state and assisted grasping. Its small proprioception-dependent correction satisfies the current match lock; that is not evidence of visual control. The default normalization is now the measured synthetic ceiling, so historical normalized scores are not directly comparable.

## Validation and difficulty

Nineteen portable tests and three Linux subprocess integration tests pass, covering protected artifact handling, scoring predicates, scene RNG equivalence, actual reference/verify entry points, simulator protocol and cumulative timing. A timing regression ensures that a reply exceeding the documented wall cap also consumes the full shift budget. Private and practice grading now use identical CPU accounting that retains waited child/grandchild time and discovers new live workers every sample. The old meter failed all three real Linux subprocess cases; the corrected meter passed without double charging a reaped worker.

The original Dockerfile built successfully on an isolated DCC KVM guest, including its `chown`, asset and agent-UID import checks. Its archive was saved successfully (job 62721924, exit zero); the final content-pinned Dockerfile rebuild is running as job 62723900. Subsequent exact-image CPU and GPU smoke checks are queued. Native GPU or Apptainer results will be identified as development evidence; they do not establish ALE's Docker privilege boundary.

No frontier result is claimed for this candidate. The earlier four-hour controller used an older environment and its saved verdicts failed the proprioception-only match lock. That observation lock and full ALE process-isolation/timing behavior still need qualification before low rewards can be interpreted as task difficulty.

## Notes for the maintainers

The image uses Isaac Sim 6.1, patched OmniGibson at a fixed source commit, the R1Pro model and NVIDIA public YCB/Simple_Room assets. Source and asset licence details are in `environment/NOTICE.md`. Robot assets use an immutable Hugging Face revision and SHA256. All 277 NVIDIA files have measured size/hash pins, and `usd-core` is fixed at the observed 26.11. The final pinned image rebuild is pending. The fixture reference is immediate; ordinary verification needs a rendering-capable NVIDIA GPU and can take up to three hours.

Remaining gates: exact build and image checks; physical feasibility; fair lock/timing validation; verification of the final pinned image; official ALE lifecycle validation; current frontier difficulty and archived trajectories. No fabricated `ok` line is provided.
