# Overlay Target Force Coverage V151 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v151-overlay-target-force-coverage`

## Scope

V151 checks whether the v150 diagnostic force-response ladder can cover the
common `5.0 N` target force before any controller or setup-target experiment
uses that target. It scans near-zero through 2 mm diagnostic penetration using
the v149 collision-clean target pair.

This is an offline diagnostic audit only. It does not tune or accept contact
parameters.

## Result

The v151 audit is:

```text
runs/overlay_target_force_coverage_after_v150/20260525T231000
```

Key metrics:

```text
audit_passed = true
target_force_N = 5.0
force_tolerance_N = 0.25
scan_row_count = 18
clean_target_contact_all_rows = true
zero_penetration_force_N = 0.0
minimum_positive_force_N = 7.136494172695263
best_penetration_m = 1e-12
best_force_N = 7.136494172695263
best_abs_error_N = 2.1364941726952633
target_within_tolerance = false
target_force_reachable_in_scan = false
coverage_gap_identified = true
diagnostic_overlay_acceptance_status = not_accepted
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Interpretation:

```text
0 m penetration -> 0.0 N
any positive penetration in the scan -> at least 7.136494172695263 N
```

So the current unaccepted diagnostic overlay cannot represent a clean `5.0 N`
static target by penetration alone. The next simulation step should be a
non-final contact-parameter or target-definition diagnostic, not a
claim-closing 5 N controller run.

## Validation

- `python3 -m py_compile scripts/audit_overlay_target_force_coverage_after_v150.py`
- `scripts/run_tests.sh tests/test_overlay_target_force_coverage_after_v150.py`
  reported `4 passed in 0.29s`.
- `python3 scripts/audit_overlay_target_force_coverage_after_v150.py --run-id 20260525T231000`
- Full `scripts/run_tests.sh` reported `316 passed in 33.67s`.
- YAML anchor scan found no anchors in the v151 coverage metrics.
- Raw/heavy artifact scan found no payloads in the v151 run artifact.
- `git diff --check` passed.

## Limit

V151 is offline diagnostic target-force coverage evidence only. It does not
collect live measurements, approve a read-only SOP step, authorize live access,
authorize execution, create approved calibration evidence, accept a contact
model, accept a setup target, relax an orientation gate, prove strict
paper-equivalent feasibility, prove robustness, establish hardware readiness,
or close the completion gate.
