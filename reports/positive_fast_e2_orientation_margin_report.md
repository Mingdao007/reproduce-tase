# Positive Fast E2 Orientation-Margin Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v106-positive-fast-e2-orientation-margin`

## Objective

Probe the v105 fast E2 orientation-margin blocker at `+1.0 mm` without
relaxing the run-local `0.12 rad` orientation gate. The probe keeps
`paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the v70
run-local relaxed Stage A/path setup fixed, then compares a compact Stage B
priority scenario matrix.

## Artifacts

- New audit script:
  `scripts/audit_positive_fast_e2_orientation_margin.py`
- New run:
  `runs/positive_fast_e2_orientation_margin/20260525T063817`
- New test:
  `tests/test_positive_fast_e2_orientation_margin.py`

## Result

The v106 E2-only matrix reports:

```text
scenario_count = 6
e2_pass_count = 2
passing_scenarios = weighted_kp0_normal1, weighted_kp0_normal30
best_orientation_scenario = weighted_kp0_normal1
min_orientation_error_rad = 0.11954627160547111
orientation_gate_rad = 0.12
```

Key rows:

| scenario | E2 pass | failed criteria | orientation | qdot saturation | tail qdot | force error |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `false` | `qdot_saturation_fraction; tail_max_qdot_utilization; max_orientation_error_rad` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `planar_normal30_kp0p001` | `false` | `qdot_saturation_fraction; tail_max_qdot_utilization` | `0.11983992753823672` | `0.072` | `1.0` | `0.20098660314203312` |
| `planar_normal30_kp0p002` | `false` | `tail_mean_abs_force_error_N` | `0.11972166555008389` | `0.001` | `0.0012133347645829611` | `0.275874931458737` |
| `weighted_kp0_normal1` | `true` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008094383419582085` |
| `weighted_kp0_normal30` | `true` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008094383419582085` |

The passing weighted rows reduce the baseline E2 orientation error by:

```text
0.12020305872871904 - 0.11954627160547111 = 0.0006567871232479308 rad
```

This clears the run-local `0.12 rad` gate while also clearing qdot saturation,
tail qdot utilization, force, and x/y gates for E2.

## Claim Boundary

V106 is E2-only diagnostic simulation. It does not rerun the full E1-E4 failed
cell audit, does not make `weighted` a canonical controller default, does not
accept a relaxed orientation gate, does not calibrate contact geometry, does
not prove robustness, does not prove strict paper-equivalent feasibility, and
does not authorize hardware motion or configuration.

## Validation

- `python3 -m py_compile scripts/audit_positive_fast_e2_orientation_margin.py`
  passed.
- `scripts/run_tests.sh tests/test_positive_fast_e2_orientation_margin.py`
  passed with `1 passed in 0.12s`.
- `python3 scripts/audit_positive_fast_e2_orientation_margin.py --output-dir runs/positive_fast_e2_orientation_margin/20260525T063817`
  created the v106 run.
- `rg -n "&id|\*id" runs/positive_fast_e2_orientation_margin/20260525T063817/metrics.yaml`
  found no YAML anchors.
- `find runs/positive_fast_e2_orientation_margin/20260525T063817 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `148 passed in 6.81s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `716ecde74a428c15ce17445018ca7028b1db9527`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next offline probe can either rerun the `positive_fast_timing_0p0075`
failed-cell audit with the weighted E1-E4 priority formulation while keeping
the `0.12 rad` gate fixed, or switch to the separate `base_z_plus1mm`
start-contact versus terminal-orientation split.
