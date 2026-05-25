# Read-Only Evidence Dependency Map Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v127-readonly-evidence-dependency-map`

Run: `runs/read_only_evidence_dependency_map/20260525T110000`

## Scope

This v127 audit is offline dependency bookkeeping only. It maps the five
unresolved measured-geometry readiness checks to exact registered read-only SOP
steps, audited not-approved approval packets, and preflight-ready worksheets.
It does not instantiate an evidence run, collect live measurements, or approve
execution.

## Result

Key metrics:

```text
audit_passed = true
dependency_map_complete = true
mapped_readiness_check_count = 5
finalizer_step_count = 5
mapped_step_count = 5
packet_covered_step_count = 5
preflight_ready_step_count = 5
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
explicit_user_approval_required = true
live_access_authorized = false
execution_authorized = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

Mapped readiness path:

| Readiness check | Registered step | Worksheet |
| --- | --- | --- |
| `mounted_stack_tcp_contact_point` | `phase1_mounted_stack_tcp_contact_measurement` | `tcp_contact_measurements.csv` |
| `contact_patch_convention` | `phase2_ksm_contact_patch_convention` | `ksm_contact_patch_convention.csv` |
| `plane_contact_normal` | `phase3_plane_normal_external_measurement` | `plane_normal_measurements.csv` |
| `force_source_frame` | `phase4_force_source_read_only_comparison` | `force_source_comparison.csv` |
| `orientation_gate_semantics` | `phase5_orientation_gate_semantics_evidence` | `orientation_gate_semantics.csv` |

Every mapped step has one audited not-approved packet and a preflight-ready
worksheet/command path. The blocker rows remain in
`packet_preflight_ready_but_approval_missing` state because no packet is
approved and no approved-read-only evidence exists.

## Interpretation

V127 clarifies the evidence dependency chain before any live bench work. The
top blocker is still approved read-only calibration evidence. Packet coverage
and execution preflight are useful readiness artifacts, but they remain
non-evidence until the user explicitly approves one exact registered step and a
future run is finalized and audited in approved-read-only mode.

## Validation

- `python3 -m py_compile scripts/audit_read_only_evidence_dependency_map.py`
- `scripts/run_tests.sh tests/test_read_only_evidence_dependency_map.py`
  reported `3 passed in 0.21s`.
- `python3 scripts/audit_read_only_evidence_dependency_map.py --run-id 20260525T110000`
- YAML anchor check found no anchors in
  `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v127 run
  directory.
- Full tests passed with `214 passed in 11.67s`.
- `git diff --check` passed.

## Limit

This is offline dependency mapping only. It does not collect live measurements,
approve a read-only SOP step, create approved calibration evidence, accept a
contact model, accept a setup target, relax a gate, prove strict
paper-equivalent feasibility, prove robustness, establish hardware readiness,
or authorize hardware work.
