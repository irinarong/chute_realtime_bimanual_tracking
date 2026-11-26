# Two-task submission preparation — admission pending

Both task packages remain in scope. Mandatory model training applies only to UAV.
No upstream task PR is open. Original friend experiments under `/cwork/yr111/rax/`
are preserved. The old-controller investigation is closed; do not extend it.

## Current source packages

| Task | Source commit | Source archive SHA256 |
|---|---|---|
| Chute | `489b139b0dba3d84016bccea07777b01153bea16` | `030d3a1fac6f4196b72006d381fad8c8011cc53b9ca08adebf776149c20e3db1` |
| UAV | `8c0ae7a3794660e08f6bc283d055149e240b1f0b` | `a57f2b0b37f47cb6f77055126ef4ac9b1c710d17877fea55e0b860bb1e8cd8bb` |

Both packages pass pinned ALE lint; each has nine unchanged canonical grader files.
Chute domain lint passes. UAV domain lint still requires the measured anchor and `full_at`.
Chute's new manifest restricts both stages to RTX 5000 Ada, the measured rendering model.
Only `task.toml` differs from runtime/build source17b6d4f; no Docker rebuild is needed.
Upstream model-name CI requires the separate one-line GPU registry patch in `validation/`.
It applies cleanly; the engine recognizes the model. No registry pass is claimed before it lands.

## Confirmed development results

- Chute direct-answer reference scored1 twice in CPU Docker; untouched/wrong/unauthorized
  artifacts scored0. These synthetic verdicts explicitly have `physical_rollout=0`.
- Chute Kit/Warp build defects are fixed. Controlled host-NGX injection restored clean
  rendering without physics changes. Clean archived-controller replay had0/20 placement
  and no contacts/time violations; this is not frontier difficulty evidence.
- UAV has all50 NPS clips:51,951 train,1,190 public,2,475 hidden frames. Coordinate/frame
  conventions corrected; exact JPEG overlap0. Both Docker images are built/exported;
  six real CPU isolation/contract cases passed.
- UAV packaged reference completed24,000 training steps from generic ImageNet initialization
  in1,207.57s onH200, selected12,000; all1,190 public frames AP50=.3639820186.
  Model SHA256:972cb29f7a9e47bb9eb65067cc0838b06dd9702d9c6ca7ad063f601462270e7e.
  It is author reference training, not an autonomous-agent run or official ALE GPU gate.

## Live jobs (requery before acting)

| Job | Last observed state | Purpose |
|---|---|---|
|62728274|RUNNING|Corrected chute Docker build, CPU smoke, export|
|62728280|PENDING after62728274|Convert exact image to SIF|
|62728568|PENDING after62728280|Exact-image GPU runtime/physical smoke with host NGX|
|62728569|PENDING after62728568|Exact-image archived replay/grading-path smoke|
|62728682|RUNNING|Fixed trained UAV artifact, full hidden verifier in CPU Docker|

Both running jobs were confirmed through Slurm and live guest process activity. Quiet
layer commits/inference logs do not imply a hang. Never boot either owned VM disk concurrently.
The UAV verifier changes only inference device toCPU; it does not train/tune or fill the anchor.

## Remaining submission gates

Final chute image evidence; physical feasibility and observation-lock fairness; numeric
portability; official ALE GPU lifecycle and repeated anchors/full_at; fresh frontier-agent
trajectories; upstream GPU model addition; maintainer acceptance of the synthetic reference.
The compatible NVIDIA Docker host request remains unanswered; do not repeat the question.
Native/SIF/CPU Docker results do not replace official ALE GPU qualification.

Evidence root: `/Users/aaronpang/.codex/visualizations/2026/11/26/01a2166c-f6f9-75e1-99e9-3a49ad48642f`.
Start with `DELIVERY_INDEX.md`, `ADMISSION_GATES.json` and the two refreshed PR drafts.
The live candidate bundlec67a7265 remains tied to runtime source17b6d4f. Preserve its identity;
the submission package's GPU-only delta does not change ongoing build/runtime tests.
