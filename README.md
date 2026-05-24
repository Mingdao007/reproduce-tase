# reproduce-tase

GitHub home for the TASE finite-time force-motion control reproduction and
UR10e adapted reproduction.

Target repository: `Mingdao007/reproduce-tase`

Current branch: `exp/tase-ur10e-v76-positive-timing-boundary`

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
v69 isolates that blocker: in the current contact-point model, force/x-y/contact
passes `8 / 8` positive terminal cases, but orientation still passes `0 / 8`;
full-rotation and force-normal-only errors are numerically identical, so yaw is
not the limiting convention.
v70 uses a run-local `0.12 rad` diagnostic orientation envelope and recovers
positive start, terminal, and path feasibility through `+1.0 mm`, but stitched
recovery remains `0`: Stage B handoff is `3 / 4`, consistently failing E2 on
qdot saturation.
v71 isolates that E2 handoff margin: at original `paper_time_scale = 0.01`, E2
passes `0 / 8` positive deltas; at `0.005`, E2 passes `8 / 8`. A qdot-limit-only
probe at `+1.0 mm` still fails because orientation remains just above
`0.12 rad`.
v72 combines the v70 relaxed terminal/path setup with the v71 E2-safe timing
and recovers the full positive E1-E4 stitched diagnostic matrix `8 / 8` through
`+1.0 mm`. v73 stress-tests that recovered policy under a compact five-scenario
matrix and passes `37 / 40` stitched cells: nominal v72 and `stage_a_14p5s`
pass all positive deltas, while `qdot012_stage_a18s` fails `+0.2 mm` on Stage A
final tracking, `paper_time_scale_0p0075` fails `+1.0 mm` on E2, and
`orientation_gate_0p119` fails `+1.0 mm` on orientation gates. v74 isolates
the `qdot012_stage_a18s` `+0.2 mm` miss and shows it is recovered by extending
Stage A from `18.03 s` to `18.035 s`; Stage B remains `4 / 4` throughout that
duration sweep. v75 folds that `18.035 s` margin back into the full positive
qdot012 matrix and recovers all positive deltas `8 / 8` through `+1.0 mm`.
v76 isolates the harder `paper_time_scale_0p0075` `+1.0 mm` timing boundary:
the row still passes at `paper_time_scale = 0.0052` and first fails at
`0.0054` on E2 orientation just above the `0.12 rad` diagnostic gate; Stage A
passes every timing case, and qdot saturation becomes severe only at `0.007`
and above.
This is still not strict paper-equivalent, robust, or hardware evidence.

## Test Command

Use the repo wrapper so user-site pytest plugins do not affect results:

```bash
scripts/run_tests.sh
```
