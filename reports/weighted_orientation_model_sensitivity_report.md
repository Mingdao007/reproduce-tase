# Weighted Orientation Model Sensitivity Report

## Summary

v84 is a post-hoc sensitivity audit for the remaining v83 failure:
`+1.0 mm` at the tightened `0.119 rad` orientation gate. It does not rerun
MuJoCo with a new calibrated model and does not change controller defaults.

The formal run is:

- `runs/weighted_orientation_model_sensitivity/20260524T233945`
- command: `python3 scripts/audit_weighted_orientation_model_sensitivity.py`
- parent commit before v84 changes: `79c2dd7fae6f16532fa269a2eb75235cbf4f81a1`

## Metrics

From `runs/weighted_orientation_model_sensitivity/20260524T233945/metrics.yaml`:

| group | pass count | Stage A orientation | Stage B orientation | Stage B excess over `0.119` | qdot saturation |
| --- | ---: | ---: | ---: | ---: | ---: |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `7 / 8` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `7 / 8` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `7 / 8` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `7 / 8` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` |

Focused `+1.0 mm` gate boundary:

| time scale | first passing gate | last failing gate | max Stage B orientation |
| ---: | ---: | ---: | ---: |
| `0.0075` | `0.11955` | `0.1195` | `0.11954627160547111` |
| `0.01` | `0.1196` | `0.11955` | `0.11956645203696047` |

Terminal/model sensitivity from the v69 positive terminal audit:

- current contact-point +1.0 mm terminal orientation:
  `0.11948560786548146 rad`
- legacy sphere-center +1.0 mm terminal orientation:
  `0.09525838838593075 rad`
- contact-point minus legacy-center orientation delta:
  `0.024227219479550713 rad`
- high-end contact-point terminal slope proxy:
  `0.03785584200850284 rad/mm`
- max v83 Stage B excess equivalent under that slope:
  `0.014963398168061883 mm`

## Interpretation

The remaining v83 failure is not a faster-timing qdot problem. The critical
weighted rows have `0.0` qdot saturation and small tail qdot utilization; they
miss only the tightened orientation gate.

The missing orientation margin is very small: less than `0.00057 rad`
(`0.033 deg`) at Stage B. The v69 contact-point versus legacy sphere-center
geometry convention changes the +1.0 mm terminal orientation by about
`0.024 rad` (`1.39 deg`), much larger than the residual v83 failure margin.

That does not make the legacy model acceptable. It means the next useful work
should be model/measurement driven: measured mounted-stack geometry, contact
point convention, plane/contact normal calibration, and terminal orientation
definition. More Stage B qdot tuning is unlikely to be the right first move
for the `0.119 rad` row.

## Claim Boundary

This is diagnostic sensitivity evidence only. It is not:

- a recovery of the `+1.0 mm`, `0.119 rad` gate
- a calibrated contact model
- a canonical controller default
- strict paper-equivalent feasibility
- a robustness proof
- hardware readiness or authorization to move/configure the real UR10e

## Validation

Validation after audit-trail updates:

- `python3 -m py_compile scripts/audit_weighted_orientation_model_sensitivity.py`
  passed.
- `scripts/run_tests.sh`: `115 passed in 2.72s`.
- `git diff --check` passed.
- Current-script reproducibility check: rerunning the audit to
  `/tmp/reproduce-tase-v84-verify.S4rN7N` produced identical `metrics.yaml`
  and `metrics.json`; `summary.md` differed only by the run-root path.
- Artifact audit: `4` files, `28K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads under `runs/weighted_orientation_model_sensitivity/20260524T233945`

## Next Step

Do not continue Stage B qdot tuning for the `0.119 rad` row until the
terminal/contact orientation definition and contact model calibration have
been tightened with measured geometry or an explicit accepted diagnostic gate.
