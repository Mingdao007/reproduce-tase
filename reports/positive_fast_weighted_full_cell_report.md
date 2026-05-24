# Positive Fast Weighted Full-Cell Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v107-positive-fast-weighted-full-cell`

## Objective

Run the exact `+1.0 mm` positive fast-timing full E1-E4 cell with
`paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the run-local
`0.12 rad` orientation gate fixed. Compare the original linear-primary
baseline against the two weighted priority candidates that v106 showed could
clear isolated E2.

## Artifacts

- New audit script:
  `scripts/audit_positive_fast_weighted_full_cell.py`
- New run:
  `runs/positive_fast_weighted_full_cell/20260525T064719`
- New test:
  `tests/test_positive_fast_weighted_full_cell.py`

## Result

The v107 full-cell matrix reports:

```text
scenario_count = 3
passing_scenario_count = 2
passing_scenarios = weighted_kp0_normal1, weighted_kp0_normal30
weighted_candidate_recovered = true
all_weighted_candidates_recovered = true
original_failed_cell_closed = false
orientation_gate_rad = 0.12
```

Key rows:

| scenario | stitched | Stage B pass | failed rows | max orientation | qdot saturation | tail qdot | force error |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `false` | `3 / 4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `weighted_kp0_normal1` | `true` | `4 / 4` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |
| `weighted_kp0_normal30` | `true` | `4 / 4` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |

The exact baseline still reproduces the unresolved E2 failure. Both weighted
rows recover the full E1-E4 cell at the fixed `0.12 rad` gate.

## Claim Boundary

V107 is full E1-E4 diagnostic simulation for one `+1.0 mm` fast-timing face.
It shows a weighted-priority recovery candidate, but it does not close the
original v99 `positive_fast_timing_0p0075` failed cell because this branch
does not accept `weighted` as a canonical controller default. It also does not
accept a relaxed orientation gate, calibrate contact geometry, prove
robustness, prove strict paper-equivalent feasibility, or authorize hardware
motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_positive_fast_weighted_full_cell.py`
  passed.
- `scripts/run_tests.sh tests/test_positive_fast_weighted_full_cell.py`
  passed with `2 passed in 0.12s`.
- `python3 scripts/audit_positive_fast_weighted_full_cell.py --output-dir runs/positive_fast_weighted_full_cell/20260525T064719`
  created the v107 run.
- `rg -n "&id|\*id" runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/positive_fast_weighted_full_cell/20260525T064719 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `150 passed in 6.79s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `2e94f4bbd9ac25228c819bdc789eb6bc1f75f719`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The next positive-fast step should be a weighted-priority acceptance-boundary
audit before treating weighted priority as canonical. The separate
`base_z_plus1mm` start-contact versus terminal-orientation split remains the
other clean offline target.
