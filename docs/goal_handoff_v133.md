# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V133

Date: 2026-05-25

Use this after the v132 read-only evidence sequence boundary audit. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v132 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v133.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_evidence_sequence_boundary_report.md`
- `runs/read_only_evidence_sequence_boundary/20260525T115000/metrics.yaml`
- `reports/phase1_approved_evidence_acceptance_boundary_report.md`
- `runs/phase1_approved_evidence_acceptance_boundary/20260525T114000/metrics.yaml`
- `reports/read_only_phase1_preapproval_finalizer_guard_report.md`
- `runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000/metrics.yaml`
- `reports/read_only_phase1_approval_request_freeze_report.md`
- `runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml`
- `reports/read_only_next_step_selection_report.md`
- `runs/read_only_next_step_selection/20260525T111000/metrics.yaml`
- `reports/read_only_evidence_dependency_map_report.md`
- `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V132 reports `audit_passed = true`,
`sequence_boundary_complete = true`, ordered step count `5`, first step
`phase1_mounted_stack_tcp_contact_measurement`, first worksheet
`tcp_contact_measurements.csv`, remaining steps after phase1 `4`, all steps
packet-covered true, all steps preflight-ready true, all steps require
separate approval true, `phase1_alone_completes_measured_geometry_chain =
false`, `phase1_alone_completes_overall_goal = false`, current approved
read-only runs `0`, current phase1 approved runs `0`, finalization records
`0`, approved-read-only audits `0`, approved packets `0`, execution-
authorizing packets `0`, live-access-authorizing packets `0`,
`bundle_approval_authorized = false`, `completion_claim_allowed = false`, and
`do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v132 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v132 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V132 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v132-readonly-sequence-boundary
```

V132 artifacts:

```text
scripts/audit_read_only_evidence_sequence_boundary.py
tests/test_read_only_evidence_sequence_boundary.py
runs/read_only_evidence_sequence_boundary/20260525T115000
reports/read_only_evidence_sequence_boundary_report.md
```

Key result:

```text
audit_passed = true
sequence_boundary_complete = true
ordered_step_count = 5
first_step_id = phase1_mounted_stack_tcp_contact_measurement
first_worksheet = tcp_contact_measurements.csv
remaining_step_count_after_phase1 = 4
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

## Recommended V133 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use the frozen phase1 request:
`phase1_mounted_stack_tcp_contact_measurement`, worksheet
`tcp_contact_measurements.csv`, and phrase
`I approve this read-only measurement step`. Instantiate a fresh run folder,
fill only `tcp_contact_measurements.csv`, finalize with the matching
registered step ID, and audit in approved-read-only mode. Do not bundle
phase2-phase5 into that approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep packet coverage,
execution preflight, the v127 dependency map, v128 selector, v129 freeze,
v130 finalizer guard, v131 acceptance-boundary scan, and v132 sequence
boundary separate from approved evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Do not use OnRobot direct TCP DAQ as control truth until the force-source
  discrepancy is resolved.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_read_only_evidence_sequence_boundary.py`
- `scripts/run_tests.sh tests/test_read_only_evidence_sequence_boundary.py`
  reported `4 passed in 0.22s`.
- `python3 scripts/audit_read_only_evidence_sequence_boundary.py --run-id 20260525T115000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v132 run
  directory.
- Full tests passed with `231 passed in 15.64s`.
- `git diff --check` passed.
