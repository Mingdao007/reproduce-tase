# Robustness Dependency Frontier After V141 Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v142-robustness-dependency-frontier`

Run: `runs/robustness_dependency_frontier_after_v141/20260525T160000`

## Scope

This v142 audit classifies the remaining robustness blocker after the v141
post-v140 completion gate. It reads the v141 completion gate and the v111
weighted-profile matrix restatement, then separates the remaining failed
robustness cells by dependency frontier.

It performs no new simulation, no hardware access, and no claim upgrade.

## Result

Key metrics:

```text
audit_passed = true
robustness_complete = false
accepted_as_robustness_proof = false
candidate_matrix_complete = false
all_failed_cells_closed = false
closed_cell_count = 0
source_failed_cell_count = 4
frontier_row_count = 4
profile_overlay_supported_noncanonical_count = 2
profile_overlay_supported_noncanonical_cell_ids = base_z_plus1mm, positive_fast_timing_0p0075
gate_or_contact_acceptance_blocked_count = 2
gate_or_contact_acceptance_blocked_cell_ids = positive_orientation_gate_0p119, weighted_plus1mm_0p119_gate
new_simulation_selected = false
additional_failed_cell_execution_recommended = false
requires_approved_read_only_evidence_for_closure = true
requires_contact_setup_target_acceptance_for_closure = true
requires_orientation_gate_acceptance_for_gate_rows = true
source_approved_read_only_run_count = 0
source_approved_read_only_audit_passed_count = 0
source_accepted_orientation_review_count = 0
source_accepted_contact_setup_target_review_count = 0
do_not_mark_goal_complete = true
```

Frontier classification:

| Cell | Frontier class | Blocking dependency |
| --- | --- | --- |
| `base_z_plus1mm` | `profile_overlay_supported_noncanonical` | canonical controller/profile acceptance, contact/setup-target acceptance, approved read-only evidence |
| `positive_fast_timing_0p0075` | `profile_overlay_supported_noncanonical` | canonical controller/profile acceptance, contact/setup-target acceptance, approved read-only evidence |
| `positive_orientation_gate_0p119` | `gate_or_contact_acceptance_blocked` | orientation-gate acceptance, contact/setup-target acceptance, approved read-only evidence |
| `weighted_plus1mm_0p119_gate` | `gate_or_contact_acceptance_blocked` | orientation-gate acceptance, contact/setup-target acceptance, approved read-only evidence |

## Interpretation

The robustness frontier is now split cleanly:

- Two failed cells have noncanonical profile overlays, but the original failed
  cells remain open and cannot be treated as closed robustness evidence.
- Two failed cells remain gate/contact acceptance blocked.
- No new simulation is selected as closure evidence because the remaining
  closure conditions require accepted contact/gate/profile evidence, starting
  from approved read-only calibration evidence.

## Validation

- `python3 -m py_compile scripts/audit_robustness_dependency_frontier_after_v141.py`
- `scripts/run_tests.sh tests/test_robustness_dependency_frontier_after_v141.py`
  reported `4 passed in 0.16s`.
- `python3 scripts/audit_robustness_dependency_frontier_after_v141.py --run-id 20260525T160000`
- Full tests passed with `275 passed in 31.32s`.
- YAML anchor scan found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads in the v142 run artifact.
- `git diff --check` passed.

## Limit

This is offline robustness-dependency bookkeeping only. It does not run
simulations, close failed robustness cells, approve a read-only SOP step,
create repository approved calibration evidence, accept a contact model,
accept a setup target, accept a controller/profile change, relax a gate, prove
strict paper-equivalent feasibility, prove robustness, establish hardware
readiness, authorize live access, authorize execution, or authorize hardware
work.
