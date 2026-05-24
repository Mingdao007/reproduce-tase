# reproduce-tase

GitHub home for the TASE finite-time force-motion control reproduction and
UR10e adapted reproduction.

Target repository: `Mingdao007/reproduce-tase`

Current branch: `exp/tase-ur10e-v56-contact-manifold-gate-audit`

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
UR10e results remain adapted simulation evidence, not hardware evidence. The
v56 shows the strict setup gate is a gate-definition conflict in the current
UR10e adapted simulation: x/y, target force, and force-normal orientation are
not jointly satisfied by the audited contact-neighborhood solves.

## Test Command

Use the repo wrapper so user-site pytest plugins do not affect results:

```bash
scripts/run_tests.sh
```
