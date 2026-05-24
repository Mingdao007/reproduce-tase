# Positive Fast-Timing E2 Qdot Isolation Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v105-positive-fast-e2-qdot-isolation`

## Objective

Isolate the v104-identified `positive_fast_timing_0p0075` blocker on the
`+1.0 mm` E2 handoff row. The probe keeps the same v70 run-local `0.12 rad`
orientation gate and tests only offline simulation settings. It does not
change canonical defaults or close the failed cell.

## Artifacts

- Updated audit script:
  `scripts/audit_positive_stage_b_e2_margin.py`
- New run:
  `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019`
- New test:
  `tests/test_positive_stage_b_e2_margin.py`

## Result

The focused E2 timing sweep used:

```text
base_z_deltas_mm = 1.0
paper_time_scales = 0.0075, 0.007, 0.0065, 0.006, 0.0055, 0.0052, 0.005
qdot_probe_limits_rad_s = 0.15, 0.18, 0.2, 0.25, 0.3
qdot_probe_paper_time_scale = 0.0075
max_orientation_error_rad = 0.12
```

Timing boundary:

```text
timing_row_count = 7
fastest_all_pass_paper_time_scale = 0.0052
```

Qdot-only probe at `paper_time_scale = 0.0075`:

```text
qdot_probe_row_count = 5
qdot_probe_pass_count = 0
max_failing_qdot_limit_rad_s = 0.3
min_qdot_saturation_fraction = 0.0
max_orientation_error_rad = 0.1202243264055315
```

At the original qdot limit `0.15 rad/s`, E2 fails on qdot saturation, tail
qdot utilization, and orientation:

```text
qdot_saturation_fraction = 0.999
tail_max_qdot_utilization = 1.0
max_orientation_error_rad = 0.12020305872871904
```

Increasing the qdot limit clears the qdot/tail-utilization failed criteria,
but every qdot-limit row through `0.3 rad/s` still fails orientation. At
`qdot_limit = 0.3 rad/s`, qdot saturation is `0.0` and max orientation is
still `0.12022428616393772 rad`.

## Claim Boundary

V105 is a narrow offline diagnostic probe. It does not recover the v99
`positive_fast_timing_0p0075` failed cell at `paper_time_scale = 0.0075`, does
not accept a relaxed orientation gate, does not calibrate contact geometry,
does not prove robustness, does not prove strict paper-equivalent feasibility,
and does not authorize hardware motion or configuration.

## Validation

- `python3 -m py_compile scripts/audit_positive_stage_b_e2_margin.py` passed.
- `scripts/run_tests.sh tests/test_positive_stage_b_e2_margin.py` passed with
  `1 passed in 0.12s`.
- `python3 scripts/audit_positive_stage_b_e2_margin.py --output-dir runs/positive_fast_timing_e2_qdot_isolation/20260525T063019 --base-z-deltas-mm 1.0 --paper-time-scales 0.0075,0.007,0.0065,0.006,0.0055,0.0052,0.005 --qdot-probe-limits-rad-s 0.15,0.18,0.2,0.25,0.3`
  created the v105 run.
- `rg -n "&id|\*id" runs/positive_fast_timing_e2_qdot_isolation/20260525T063019/metrics.yaml`
  found no YAML anchors.
- `scripts/run_tests.sh` passed with `147 passed in 6.86s`.
- `git diff --check` passed after validation.
- Branch push was verified at
  `6cc6733a3ac78b93090d4079b62480ade57e82a7`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The remaining `positive_fast_timing_0p0075` question is no longer pure qdot
saturation: at faster timing, orientation remains above the `0.12 rad` gate
even after qdot saturation is removed. The next offline step should either
probe orientation-margin reduction at `paper_time_scale = 0.0075` without gate
relaxation, or switch to the separate `base_z_plus1mm` start-contact versus
terminal-orientation split.
