# Failed Diagnostic Robustness Experiment Matrix Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v99-failed-robustness-experiment-matrix`

## Objective

Convert the four failed v98 diagnostic robustness matrix cells into concrete,
offline executable experiment commands. This is a planning artifact only: it
does not execute the experiments and does not upgrade any claim scope.

## Artifacts

- New matrix generator:
  `scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
- New planned run:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909`
- New tests:
  `tests/test_failed_diagnostic_robustness_experiment_matrix.py`

## Result

The v99 generator reads the v98 candidate matrix metrics and verifies the
expected failed cells:

```text
base_z_plus1mm
positive_fast_timing_0p0075
positive_orientation_gate_0p119
weighted_plus1mm_0p119_gate
```

It writes a planned-not-executed run with:

```text
status = planned_not_executed
experiment_count = 4
planned_not_executed_count = 4
all_expected_scripts_exist = true
all_commands_have_output_dirs = true
do_not_mark_goal_complete = true
```

The generated `commands.sh` contains one focused offline command for each
failed v98 cell:

- `base_z_plus1mm`: run `audit_stage_a_base_z_bracket.py` at `+1.0 mm` with
  Stage A durations `15.0,16.0,18.0`.
- `positive_fast_timing_0p0075`: run
  `audit_positive_stitched_sensitivity.py` at `+1.0 mm` for
  `paper_time_scale_0p0075`.
- `positive_orientation_gate_0p119`: run
  `audit_positive_orientation_gate_boundary.py` at `+1.0 mm` over gates from
  `0.119` through `0.12 rad`.
- `weighted_plus1mm_0p119_gate`: run
  `audit_weighted_gate_time_matrix.py` at `+1.0 mm` over focused weighted
  gate candidates.

No experiment output directories were created by v99; only the plan, metrics,
summary, command script, and git state were written.

## Claim Boundary

V99 is offline experiment planning only. It does not execute simulations,
collect live measurements, execute the read-only SOP, move the UR10e, write
configuration, zero/bias/filter the force sensor, run force control, reconcile
force-source frames, accept a replacement orientation gate, calibrate the
contact model, prove robustness, prove strict paper-equivalent feasibility, or
make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
  passed.
- `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_matrix.py`
  passed with `2 passed in 0.13s`.
- `python3 scripts/create_failed_diagnostic_robustness_experiment_matrix.py --run-id 20260525T053909`
  created the v99 planned experiment matrix.
- `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `136 passed in 5.75s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `f81df802cede561528849dc886b303ad3d5e63dc`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline step is to run at most one planned v99 experiment command at
a time, then add a separate comparison audit that evaluates the produced
metrics against the failed-cell closure criteria. Gate relaxation and contact
model interpretation remain blocked until approved read-only evidence exists.
