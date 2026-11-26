# Two-task submission work — admission pending

The goal covers both tasks. Mandatory model training applies only to UAV. No upstream
PR has been opened. The original friend experiments under /cwork/yr111/rax are preserved.
This checkpoint supersedes the old chronological notes, retained in
chute-validation/snapshots/before-render-ngx/SUBMISSION_PROGRESS.md under the evidence root.

## Current sources and packages

- Friend:17b6d4fd56b1754406ddde51b9ccf3d61b60a305;70 files; archive SHA256
  a3a410115254f6698debf2fcb579c07e61472b22ac949054fe35feb05dcb08ee.
- UAV:8c0ae7a3794660e08f6bc283d055149e240b1f0b;50 files; archive SHA256
  a57f2b0b37f47cb6f77055126ef4ac9b1c710d17877fea55e0b860bb1e8cd8bb.
- Pinned ALE:bfb75050aca2c54b45c5ab23bae6028a834a468a.
- Exact manifests/source and nine canonical robotics_grader files verified. Both ALE lint pass.
- No training, output clearing or data sync in setup/start. Canonical grader unchanged.

## UAV development evidence complete

All50 NPS clips present:51,951 training,1,190 public-validation,2,475 hidden frames.
Public revisionc1fca946a5936294a2cf23874040493ac148239b. YX and1-based frame indices
corrected; exact JPEG overlap0. AOT unused.

Docker build/export62725367 completed; both images and archive hashes verified.
Six real CPU contract/UID/file/network-isolation cases passed. Agent image603fa53e;
verifier7fab6230. Final-image SIF full reference62727576 completed21m10s/exit0:
24,000 from-scratch steps in1207.57s, selected12,000, all1,190 public frames in53.99s,
AP50=.36398201864109875; model972cb29f7a9e47bb9eb65067cc0838b06dd9702d9c6ca7ad063f601462270e7e.
Source/helper/logs verified. This is H200 author evidence, not autonomous-agent,
RTX4090 reproduction, hidden tuning or official ALE. Do not repeat without cause.
See uav-validation/full-image-training-62727576/evidence.json.

## Friend runtime and live pipeline

Actual GPU launch found two image defects missed by import-only tests: absent
omnigibson_6_1_0.kit and standaloneWarp1.19 mixed with IsaacWarp1.16. Source17b6d4f
includes the original pinned Kit and Warp1.16; build-time checks detect both defects.
Old SIF plus these author overlays completed job62728194 on RTX5000Ada:
20/20 events completed,1 placement, score.05, assisted=False, zero bystander/mass errors.
No successful grasp or robust physical feasibility is established. Initial RGB is
severely speckled despite simple nonzero image/depth checks passing. Host NGX library
exists but is absent from default Apptainer injection; controlled static comparison
62728432 will test causation and extra render warmup without advancing physics.

| Job | Latest state | Purpose |
|---|---|---|
|62728039|RUNNING, export|Intermediate Kit-only Docker, known Warp mismatch; CPU smoke passed|
|62728274|PENDING after62728039|Exact source17b6d4f Docker rebuild, CPU smoke/export|
|62728280|PENDING after62728274|Convert final image to SIF|
|62728290|PENDING after62728280|Final-image physical GPU smoke|
|62728300|PENDING after62728290|Final-image archived visual replay|
|62728301|RUNNING|Kit/Warp overlay archived visual replay|
|62728432|PENDING|Author static NGX/no-NGX rendering comparison|

Requery jobs; do not restart quiet builds. The180GiB VM disk at
/work/yr111/chute-direct-answer-20261126/datasets/vm-builder-62721924/ubuntu.img
has an exclusive ownership lock. Never boot concurrently. Candidatec67a7265 includes
18 pinned SDK files for author tests; it is separate from the submitted source archive.
Original SIF6e2ebf77 and Dockera35d570a are historical; overlays do not qualify the final image.

## Reference semantics and unresolved admission

The requested protected direct-answer fixture scores1 in author CPU Docker checks;
untouched/wrong/unauthorized answers score0. It reports synthetic_reference=1 and
physical_rollout=0. It is not physical success. Maintainer acceptance is unresolved.

Current ProbeLock can reject an image-driven absolute-target policy: archived
controller had0/100 action changes for constructed carry-phase joint perturbations,
while depth ablation changed detection/action. Do not remove or trivialize the lock.
Replay measures raw progress, timing and lock separately; noisy rendering is another
confound. No fresh frontier trajectory exists for either final task.

Still required: exact final friend image checks; usable cameras and physical feasibility;
fair lock/timing; real ALE GPU lifecycle, repeated anchors/full_at, and fresh agent
trajectories. DCC's Docker VM has no GPU passthrough; native/SIF development results
cannot replace Docker isolation. A compatible NVIDIA Docker host was already requested,
with no answer; do not repeat that question. Keep missing evidence explicitly missing.

Evidence root:
/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f/
Use LIVE_PIPELINE.json, ADMISSION_GATES.json, each PACKAGE.json and PR_BODY_DRAFT.md.
