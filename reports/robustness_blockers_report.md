# Robustness Blockers Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v97-robustness-blockers`

## Objective

Quantify the remaining robustness blocker using existing offline diagnostic
sensitivity and recovery runs. This is the v95 offline-actionable robustness
item only; it is not a robustness proof or completion claim.

## Artifacts

- New audit script:
  `scripts/audit_robustness_blockers.py`
- New audit run:
  `runs/robustness_blockers/20260525T052457`
- New tests:
  `tests/test_robustness_blockers.py`

## Result

The audit reads the v64 baseline stitched sensitivity, v65 timing-margin
recovery, v66/v67 base-z recovery/bracket runs, v73 positive stitched
sensitivity, v75 qdot012 positive recovery, v84 orientation model sensitivity,
v85 calibration-margin audit, and the v95/v96 blocker metrics.

It reports:

```text
overall_goal_complete = false
robustness_complete = false
baseline_stitched_pass_count = 4 / 9
positive_matrix_pass_count = 37 / 40
primary_blocker = accepted_model_robustness_not_closed
do_not_mark_goal_complete = true
```

The baseline diagnostic stitched sensitivity still fails `5 / 9` cases:
`base_z_minus_1mm`, `base_z_plus_1mm`, `stage_a_14s`,
`qdot_limit_0p12`, and `paper_time_scale_0p02`. Later diagnostic runs recover
some faces, including `stage_a_14p5`, `qdot012_stage_a_18p0`, and the v75
positive qdot012 matrix at `18.035 s`, but those recoveries are still scoped
diagnostic simulation evidence. The positive stitched sensitivity matrix still
fails `3 / 40` cells across `qdot012_stage_a18s`,
`paper_time_scale_0p0075`, and `orientation_gate_0p119`; the `0.119 rad`
orientation gate remains blocked at the `+1.0 mm` row without accepted
contact/gate calibration evidence.

## Claim Boundary

V97 is offline simulation bookkeeping only. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a replacement orientation gate, calibrate the contact model,
prove robustness, prove strict paper-equivalent feasibility, or make a
hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_robustness_blockers.py`
  passed.
- `scripts/run_tests.sh tests/test_robustness_blockers.py`
  passed with `2 passed in 0.38s`.
- `python3 scripts/audit_robustness_blockers.py --run-id 20260525T052457`
  created the v97 blocker audit.
- `scripts/run_tests.sh` passed with `132 passed in 5.44s`.
- `git diff --check` passed after full-test validation.
- Branch push was verified at
  `f74c3719d4770e21604ae0087d8b27cc22e4b7d9`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline target can define and stress a single accepted diagnostic
robustness matrix, or continue strict setup policy search from the v96 audit.
Any calibrated contact/gate update remains blocked until approved read-only
measurement evidence exists.
