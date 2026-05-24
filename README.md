# reproduce-tase

GitHub home for the TASE finite-time force-motion control reproduction and
UR10e adapted reproduction.

Target repository: `Mingdao007/reproduce-tase`

Current branch: `exp/tase-ur10e-v68-positive-start-contact`

## Scope

This repository is the authoritative location for reproduction code, configs,
plans, reports, and lightweight run metadata. The legacy working source is:

`/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/`

Large raw artifacts stay out of normal Git history unless Git LFS is explicitly
configured. They are represented by manifests and local paths.

## Safety

No real UR10e motion is authorized by this repository state. No TCP, payload,
URCap, zero, bias, filter, or OnRobot configuration writes are authorized.
Hardware work is read-only until a separate hardware gate SOP is approved.

## First Checkpoints

- `plans/MASTER_PLAN.md`
- `plans/PAPER_TRUTH_EXTRACTION.md`
- `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
- `plans/MUJOCO_ENVIRONMENT_PLAN.md`
- `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
- `plans/EXPERIMENT_MATRIX.md`
- `plans/HARDWARE_GATE_SOP.md`
- `plans/ROLLBACK_AND_CHECKPOINTS.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `reports/REPO_MIGRATION_AUDIT.md`
- `reports/math_derivation_ur10e_transfer.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`

## Reproduction Claim

Current accepted claims are tracked in `reports/completion_audit.md`.
UR10e results remain adapted simulation evidence, not hardware evidence. v58
selects the v57 diagnostic terminal setup target for the next Stage A
simulation prototype. v59 shows direct handoff from that target to Stage B
keeps target contact but still fails all E1-E4 rows on qdot saturation. v60
adds a slowed, low-gain diagnostic handoff that passes `4 / 4` from the
selected target. v61 adds an offline 128-knot quasi-static contact path from
the ordinary initial q to that target, but it is not an online controller,
strict trajectory-feasibility claim, paper-equivalent claim, or hardware claim.
v62 tracks that path with a qdot-limited joint-path replay prototype over
`15.0 s`, but it still does not connect Stage A tracking to Stage B handoff in
one staged trajectory run. v63 stitches the v62 tracker to the v60 slowed
handoff and passes `4 / 4` E1-E4 under the diagnostic label. v64 stress-tests
that stitched policy and passes only `4 / 9` sensitivity cases, failing 1 mm
base-z/contact perturbations, shorter Stage A timing, a tighter qdot limit, and
faster Stage B timing. v65 recovers the timing/qdot side with explicit margins:
`14.5 s` Stage A passes at the nominal `0.15 rad/s` limit, `18.0 s` passes at a
`0.12 rad/s` limit, and Stage B passes up to `paper_time_scale = 0.012` but not
`0.0125`. v66 adds perturbation-aware endpoint and path reoptimization for the
base-z cases: `base_z_minus_1mm_stage_a_16s_recovery` passes, but the exact
`15.0 s` `base_z_minus_1mm` reference and `base_z_plus_1mm` remain unresolved.
v67 brackets the base-z model perturbation and finds no positive-delta recovery
from `+0.05 mm` through `+1.0 mm`; the positive side loses start contact and
exceeds the terminal orientation gate before any path can be tested.
v68 widens the start-contact search and shows positive-delta start contact is
recoverable through `+1.0 mm`; the remaining positive-side blocker is terminal
orientation, not the Stage A start contact.
This is still not strict paper-equivalent, robust, or hardware evidence.

## Test Command

Use the repo wrapper so user-site pytest plugins do not affect results:

```bash
scripts/run_tests.sh
```
