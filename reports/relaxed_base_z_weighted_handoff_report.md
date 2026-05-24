# Relaxed Base-Z Weighted Handoff Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v109-relaxed-base-z-weighted-handoff`

Implementation commit: `3a766ae641d7d4cda70864da4cfad366786e6515`

## Objective

Test the remaining v108 relaxed `base_z_plus1mm` Stage B handoff blocker
without changing the claim boundary. The audit reruns the v70 relaxed
`+1.0 mm` path with `paper_time_scale = 0.01`, `qdot_limit = 0.15 rad/s`, the
run-local `0.12 rad` orientation gate, Stage A durations `15.0 s` and
`16.0 s`, and three Stage B priority scenarios.

## Artifacts

- New audit script:
  `scripts/audit_relaxed_base_z_weighted_handoff.py`
- New run:
  `runs/relaxed_base_z_weighted_handoff/20260525T073012`
- New test:
  `tests/test_relaxed_base_z_weighted_handoff.py`

## Result

The v109 matrix reports:

```text
case_count = 6
tested_stage_a_durations_s = 15.0, 16.0
passing_case_count = 4
baseline_failing_count = 2
weighted_passing_count = 4
weighted_candidate_recovered_any_duration = true
weighted_candidate_recovered_all_durations = true
all_weighted_cases_recovered = true
original_failed_cell_closed = false
canonical_orientation_gate_change_accepted = false
canonical_controller_change_accepted = false
```

Key rows:

| duration | scenario | stitched | Stage B pass | failed rows | max orientation | qdot saturation | tail qdot | force error |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `15.0` | `linear_kp0_normal1` | `false` | `3 / 4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12043140848858806` | `0.997` | `1.0` | `0.014411641468066758` |
| `15.0` | `weighted_kp0_normal1` | `true` | `4 / 4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `15.0` | `weighted_kp0_normal30` | `true` | `4 / 4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `16.0` | `linear_kp0_normal1` | `false` | `3 / 4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12043140848858806` | `0.997` | `1.0` | `0.014411641468066758` |
| `16.0` | `weighted_kp0_normal1` | `true` | `4 / 4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `16.0` | `weighted_kp0_normal30` | `true` | `4 / 4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |

The linear-primary baseline reproduces the v70 E2 blocker at both tested Stage
A durations. Both weighted rows pass E1-E4 at both durations. This makes
weighted priority a diagnostic candidate for the relaxed `base_z_plus1mm`
handoff, but it does not close the original v99 failed cell.

## Claim Boundary

V109 is diagnostic simulation only. It uses the v70 run-local `0.12 rad`
orientation gate and weighted Stage B priority as non-canonical candidates. It
does not close the original v99 `base_z_plus1mm` failed cell, accept a
replacement orientation gate, accept weighted priority as a canonical
controller default, change canonical configs, calibrate contact geometry, prove
robustness, prove strict paper-equivalent feasibility, establish hardware
readiness, or authorize hardware motion/configuration.

## Validation

- `python3 -m py_compile scripts/audit_relaxed_base_z_weighted_handoff.py`
  passed.
- `scripts/run_tests.sh tests/test_relaxed_base_z_weighted_handoff.py`
  passed with `3 passed in 0.12s`.
- `python3 scripts/audit_relaxed_base_z_weighted_handoff.py --output-dir runs/relaxed_base_z_weighted_handoff/20260525T073012`
  created the v109 run.
- `rg -n "&id|\*id" runs/relaxed_base_z_weighted_handoff/20260525T073012/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/relaxed_base_z_weighted_handoff/20260525T073012 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `156 passed in 6.93s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `3a766ae641d7d4cda70864da4cfad366786e6515`.

## Next Step

Without explicit live bench approval, continue only non-final offline work. The
next clean offline step is a weighted-priority acceptance-boundary audit that
uses v107 and v109 together to decide whether `weighted` can be named as a
diagnostic controller profile without becoming canonical or closing any
original v99 failed cell.
