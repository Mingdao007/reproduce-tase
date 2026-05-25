# Calibrated Overlay Force Response V150 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v150-overlay-force-response`

## Scope

V150 runs the next offline diagnostic force/contact simulation against the
v149 collision-masked diagnostic contact overlay:

```text
configs/mujoco_ur10e_calibrated_20260525T1641_diagnostic_contact_overlay.yaml
```

It applies a static penetration ladder by translating the diagnostic plane
along its configured normal while keeping the backed-up v147 joint pose fixed.
This tests whether the collision-clean plane/tip pair has a usable MuJoCo
force response without non-target contacts.

## Result

The v150 audit is:

```text
runs/calibrated_overlay_force_response_after_v149/20260525T230000
```

Key metrics:

```text
audit_passed = true
force_response_ladder_passed = true
row_count = 7
clean_target_contact_all_rows = true
zero_penetration_force_ok = true
positive_penetration_force_positive = true
target_force_monotonic_nondecreasing = true
positive_target_force_strictly_increasing = true
contact_distance_matches_penetration = true
min_positive_force_N = 7.432339543010282
force_at_1mm_N = 11.078794158483424
max_force_N = 14.36943859842967
diagnostic_overlay_acceptance_status = not_accepted
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Ladder summary:

| penetration m | target force N | target contacts | non-target contacts |
| ---: | ---: | ---: | ---: |
| `0.0` | `0.0` | `1` | `0` |
| `0.0001` | `7.432339543010282` | `1` | `0` |
| `0.00025` | `7.93408449665741` | `1` | `0` |
| `0.0005` | `8.977491430922026` | `1` | `0` |
| `0.001` | `11.078794158483424` | `1` | `0` |
| `0.0015` | `12.724636394431727` | `1` | `0` |
| `0.002` | `14.36943859842967` | `1` | `0` |

## Interpretation

The v149 overlay now has a clean target-only force response over the diagnostic
penetration ladder and can be used for the next offline force/contact
simulation debugging step.

This is still not accepted contact calibration. The ladder is a simulation
debugging artifact over an unaccepted diagnostic overlay.

## Validation

- `python3 -m py_compile scripts/audit_calibrated_overlay_force_response_after_v149.py`
- `scripts/run_tests.sh tests/test_calibrated_overlay_force_response_after_v149.py`
  reported `4 passed in 0.27s`.
- `python3 scripts/audit_calibrated_overlay_force_response_after_v149.py --run-id 20260525T230000`
- Full `scripts/run_tests.sh` reported `312 passed in 33.58s`.
- YAML anchor scan found no anchors in the v150 force-response metrics.
- Raw/heavy artifact scan found no payloads in the v150 run artifact.
- `git diff --check` passed.

## Limit

V150 is offline diagnostic force-response evidence only. It does not collect
live measurements, approve a read-only SOP step, authorize live access,
authorize execution, create approved calibration evidence, accept a contact
model, accept a setup target, relax an orientation gate, prove strict
paper-equivalent feasibility, prove robustness, establish hardware readiness,
or close the completion gate.
