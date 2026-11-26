## What this pull request adds

`tasks/arm/chute_realtime_bimanual_tracking/` asks an autonomous agent to implement a visual controller that catches moving parts with a two-arm robot and places them in a tote. The submitted `run.sh` and supporting code receive RGB-D images and proprioception; a separate privileged simulator evaluates six hidden shifts.

**Admission pending. Local draft only; no upstream task PR has been opened.**

## Checklist

- [x] Folder, manifest name and `arm` platform agree.
- [x] Pinned ALE lint passes (`bfb75050aca2c54b45c5ab23bae6028a834a468a`).
- [ ] Official ALE validation records untouched reward 0 and reference reward 1 under the declared GPU resources.
- [ ] Current frontier-agent results and complete trajectories are archived.
- [ ] Repeated official reference runs support the anchor and `full_at`.
- [x] All nine `robotics_grader` files match the canonical package.
- [x] Practice scoring reports raw metrics without importing hidden tests or the anchor.
- [x] The task folder contains source and small fixtures, without checkpoints or downloaded simulator assets.
- [x] Platform, positive metric direction and reported metric name agree.
- [ ] The upstream known-GPU list includes `NVIDIA RTX 5000 Ada Generation`.

## Reference design

The requested default reference writes protected terminal snapshots and a reference-only authorization token. The verifier reconstructs the hidden tote layouts and applies the simulator's placement predicates and credit aggregation. Author CPU Docker checks measured reference reward 1 twice and untouched, wrong and unauthorized answers at 0.

These verdicts explicitly report `synthetic_reference=1` and `physical_rollout=0`. They validate the direct-answer scoring path; they do not establish that a feasible physical trajectory exists. Acceptance of this reference design for a closed-loop task remains a maintainer-review item. The stronger upstream privileged controller is available separately as `solution/solve_physical.sh`; all motion/geometry dependencies are staged and any stale synthetic fixture is removed.

## Build and validation evidence

GPU startup exposed two defects that import-only checks missed: a missing `omnigibson_6_1_0.kit` and mismatched standalone/bundled Warp versions. The Dockerfile now copies the pinned Kit, pins standalone Warp to Isaac's 1.16.0, and checks both at build time. The corrected image build/CPU checks/export (62728274), conversion (62728280), and two old-source GPU checks (62728568/62728569) all completed with exit0. Collected image identity is `sha256:f2155903863e515cb0cda8c7fa764e4e13a3700636bf2ab8f363d99baab901dd`; its CPU cases pass. GPU result details still need collection. The upstream merge leaves all Docker build inputs unchanged, but its updated runtime needs separate checks.

Earlier CPU Docker checks passed the protected-reference cases, root-to-user solver execution and three real Linux child-process CPU-accounting cases. The intermediate Kit-only image also passed those checks but retained the Warp mismatch, so it is historical evidence only.

Controlled development rendering on RTX 5000 Ada identified an Apptainer host-library omission: adding the host-matched NGX library restored clean RGB without changing physics, joint state or part poses. Author launch helpers now handle this; no driver library is baked into the task image. The pinned ALE Docker provider already requests all NVIDIA driver capabilities, but its GPU lifecycle has not been run here.

## Frontier-model results

The upstream update at `bc8ba0c` reports a fresh camera-only controller raw mean0.3375 and
physical-reference mean0.8583. Its reported reward0.41 uses physical normalization0.8583/full_at0.95;
our requested direct-answer variant uses a synthetic ceiling1.0. Those rewards are not interchangeable.
The upstream run bypassed account separation and was not `ale run`; its source reports are retained
as attributed snapshots in RESULTS.md and PR_BODY.md. They have not been independently reproduced
on this merged configuration. The older zero-contact replay concerned the previous task version.
The joint-only observation-lock fairness concern remains; no lock was silently removed during merging.

## Notes for maintainers

Both stages request 8 CPUs, 32 GiB RAM and one `RTX-5000-Ada`; the agent budget is four hours and verification up to three hours. The precise model restriction matches the development rendering hardware. The upstream GPU registry does not currently contain that model: the accompanying author-only `benchmark-gpu-model.patch` adds it, and must land before the task's GPU-name CI can pass. The task PR itself should contain only the task folder.

The image uses Isaac Sim 6.1, patched OmniGibson at a fixed commit, the R1Pro model and pinned NVIDIA YCB/Simple_Room assets. Licence details are in `environment/NOTICE.md`. Robot assets have an immutable Hugging Face revision and SHA256; all 277 NVIDIA files have size/hash pins.

Remaining qualifications: merged-runtime image checks, ordinary physical feasibility, fair observation lock, numerical portability, official ALE lifecycle and repeated anchors, and current frontier-agent trajectories. Native/SIF/CPU-container evidence does not replace the official GPU lifecycle.

Current merge provenance and checks: `validation/MERGE_REPORT.md`. Source-package identity will be refreshed after the merge commit.
