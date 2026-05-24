# Diagnostic Robustness Matrix Candidate Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v98-diagnostic-robustness-matrix`

## Objective

Define one candidate diagnostic robustness matrix from the currently recovered
and failing robustness faces. This is bookkeeping over existing offline
evidence only; it is not an accepted robustness proof.

## Artifacts

- New audit script:
  `scripts/audit_diagnostic_robustness_matrix_candidate.py`
- New audit run:
  `runs/diagnostic_robustness_matrix_candidate/20260525T053101`
- New tests:
  `tests/test_diagnostic_robustness_matrix_candidate.py`

## Result

The candidate matrix reads v95-v97 blocker metrics and reports:

```text
overall_goal_complete = false
candidate_matrix_complete = false
accepted_as_robustness_proof = false
cell_count = 12
passed_diagnostic = 7
passed_diagnostic_nonfinal = 1
failed = 4
do_not_mark_goal_complete = true
```

Failed cells:

```text
base_z_plus1mm
positive_fast_timing_0p0075
positive_orientation_gate_0p119
weighted_plus1mm_0p119_gate
```

The v75 qdot012 positive matrix is tracked as
`passed_diagnostic_nonfinal`: it passes `8 / 8`, but it remains diagnostic
evidence and cannot be upgraded into a robustness proof while the failed cells
and claim dependencies remain unresolved.

Blocking dependencies:

```text
strict_feasibility_complete
robustness_complete_from_v97
approved_read_only_calibration_evidence
orientation_gate_acceptance
contact_calibration_claim
```

## Claim Boundary

V98 is offline diagnostic bookkeeping only. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a replacement orientation gate, calibrate the contact model,
prove robustness, prove strict paper-equivalent feasibility, or make a
hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_diagnostic_robustness_matrix_candidate.py`
  passed.
- `scripts/run_tests.sh tests/test_diagnostic_robustness_matrix_candidate.py`
  passed with `2 passed in 0.18s`.
- `python3 scripts/audit_diagnostic_robustness_matrix_candidate.py --run-id 20260525T053101`
  created the v98 candidate matrix audit.
- `scripts/run_tests.sh` passed with `134 passed in 5.59s`.
- `git diff --check` passed after full-test validation.
- Branch push verification is pending.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The clearest next offline task is to convert the four failed candidate cells
into an executable experiment matrix, while keeping contact/gate calibration
blocked until approved read-only evidence exists.
