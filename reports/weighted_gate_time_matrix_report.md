# Weighted Gate/Time Matrix Report

## Summary

v83 stress-tests the v82 weighted zero-angular-command candidate on the two
remaining diagnostic questions:

- whether the focused `paper_time_scale = 0.01` pass generalizes to the full
  positive-delta matrix under the `0.11995 rad` gate
- whether weighted priority changes the tightened `0.119 rad` orientation-gate
  limit

The formal run is:

- `runs/weighted_gate_time_matrix/20260524T232637`
- command: `scripts/audit_weighted_gate_time_matrix.py`
- parent commit before v83 changes: `b72ecec06468cf527889d176fc553be764206307`

## Metrics

From `runs/weighted_gate_time_matrix/20260524T232637/metrics.yaml`:

- group count: `8`
- total case count: `64`
- total stitched pass count: `51 / 64`
- all-pass groups:
  - `time0p01_gate0p11995:weighted_kp0_normal1`
  - `time0p01_gate0p11995:weighted_kp0_normal30`

Full positive-delta matrices:

| group | scenario | time scale | gate | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `time0p01_gate0p11995` | `weighted_kp0_normal1` | `0.01` | `0.11995` | `8 / 8` | `1.0` | `0.11956645203696047` | `0.0` | `0.520987929048311` |
| `time0p01_gate0p11995` | `weighted_kp0_normal30` | `0.01` | `0.11995` | `8 / 8` | `1.0` | `0.11956645203696047` | `0.0` | `0.520987929048311` |
| `time0p0075_gate0p119` | `weighted_kp0_normal1` | `0.0075` | `0.119` | `7 / 8` | `0.75` | `0.11954627160547111` | `0.0` | `0.5177926211135458` |
| `time0p0075_gate0p119` | `weighted_kp0_normal30` | `0.0075` | `0.119` | `7 / 8` | `0.75` | `0.11954627160547111` | `0.0` | `0.5177926211135458` |
| `time0p01_gate0p119` | `weighted_kp0_normal1` | `0.01` | `0.119` | `7 / 8` | `0.75` | `0.11956645203696047` | `0.0` | `0.520987929048311` |
| `time0p01_gate0p119` | `weighted_kp0_normal30` | `0.01` | `0.119` | `7 / 8` | `0.75` | `0.11956645203696047` | `0.0` | `0.520987929048311` |

Focused `+1.0 mm` gate boundary:

| time scale | min passing gate | max failing gate | max Stage B orientation |
| ---: | ---: | ---: | ---: |
| `0.0075` | `0.11955` | `0.1195` | `0.11954627160547111` |
| `0.01` | `0.1196` | `0.11955` | `0.11956645203696047` |

## Interpretation

The v82 focused `paper_time_scale = 0.01` timing evidence generalizes across
the full positive-delta matrix under the `0.11995 rad` gate. Both tested
weighted scenarios pass all eight positive deltas through `+1.0 mm` with no
qdot saturation.

The tightened `0.119 rad` gate is still not recovered. At both
`paper_time_scale = 0.0075` and `0.01`, the weighted candidate passes through
`+0.75 mm` but fails the `+1.0 mm` row. The failure is no longer qdot or force;
it is the Stage A/Stage B orientation value relative to the tightened gate.

## Claim Boundary

This is diagnostic-label timing/gate matrix evidence only. It is not:

- a canonical controller default
- a recovery of the `+1.0 mm`, `0.119 rad` gate
- a strict paper-equivalent feasibility claim
- a robustness proof
- contact-model calibration
- hardware readiness or authorization to move/configure the real UR10e

## Validation

- `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py` passed.
- `scripts/run_tests.sh` passed with `115 passed in 2.78s`.
- `git diff --check` passed.
- Artifact audit: `460` files, `7.0M`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/weighted_gate_time_matrix/20260524T232637`.

## Next Step

The faster-timing diagnostic face can now be treated as recovered under the
`0.11995 rad` gate. The remaining simulation blocker is the `+1.0 mm`,
`0.119 rad` orientation-gate row, which should be addressed by revisiting the
terminal/contact orientation definition or model calibration rather than by more
Stage B qdot tuning.
