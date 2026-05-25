# Read-Only Evidence Sequence Boundary Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v132-readonly-sequence-boundary`

Run: `runs/read_only_evidence_sequence_boundary/20260525T115000`

## Scope

This v132 audit freezes the non-authorizing sequence boundary for the
registered read-only evidence chain. It cross-checks the v127 dependency map,
v128 next-step selector, and v131 current evidence scan. It does not approve
phase1, bundle later steps into phase1, create evidence, collect live
measurements, or authorize execution.

## Result

Key metrics:

```text
audit_passed = true
sequence_boundary_complete = true
ordered_step_count = 5
first_step_id = phase1_mounted_stack_tcp_contact_measurement
first_worksheet = tcp_contact_measurements.csv
remaining_step_count_after_phase1 = 4
remaining_step_ids_after_phase1 =
  - phase2_ksm_contact_patch_convention
  - phase3_plane_normal_external_measurement
  - phase4_force_source_read_only_comparison
  - phase5_orientation_gate_semantics_evidence
all_steps_packet_covered = true
all_steps_preflight_ready = true
all_steps_separate_approval_required = true
phase1_alone_completes_measured_geometry_chain = false
phase1_alone_completes_overall_goal = false
current_approved_read_only_run_count = 0
current_phase1_approved_read_only_run_count = 0
current_finalization_record_count = 0
current_approved_read_only_audit_passed_count = 0
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
bundle_approval_authorized = false
approved_read_only_evidence_created = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Sequence:

| Index | Step ID | Worksheet | Role |
| ---: | --- | --- | --- |
| 1 | `phase1_mounted_stack_tcp_contact_measurement` | `tcp_contact_measurements.csv` | first selected step |
| 2 | `phase2_ksm_contact_patch_convention` | `ksm_contact_patch_convention.csv` | remaining required step |
| 3 | `phase3_plane_normal_external_measurement` | `plane_normal_measurements.csv` | remaining required step |
| 4 | `phase4_force_source_read_only_comparison` | `force_source_comparison.csv` | remaining required step |
| 5 | `phase5_orientation_gate_semantics_evidence` | `orientation_gate_semantics.csv` | remaining required step |

## Interpretation

The selected phase1 step is only the first exact read-only evidence step. Four
downstream registered evidence steps remain after phase1, and each still needs
its own explicit approval. A future approved phase1 run could create one
approved read-only evidence artifact, but it would not by itself close the
measured-geometry chain, contact/setup acceptance, orientation-gate
acceptance, robustness, hardware readiness, or the overall goal.

## Validation

- `python3 -m py_compile scripts/audit_read_only_evidence_sequence_boundary.py`
- `scripts/run_tests.sh tests/test_read_only_evidence_sequence_boundary.py`
  reported `4 passed in 0.22s`.
- `python3 scripts/audit_read_only_evidence_sequence_boundary.py --run-id 20260525T115000`
- YAML anchor check found no anchors in
  `runs/read_only_evidence_sequence_boundary/20260525T115000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v132 run
  directory.
- Full tests passed with `231 passed in 15.64s`.
- `git diff --check` passed.

## Limit

This audit does not collect live measurements, approve a read-only SOP step,
create approved calibration evidence, accept a contact model, accept a setup
target, relax a gate, prove strict paper-equivalent feasibility, prove
robustness, establish hardware readiness, or authorize hardware work.
