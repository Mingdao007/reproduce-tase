# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V130

Date: 2026-05-25

Use this after the v129 phase1 approval-request freeze audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v129 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v130.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_phase1_approval_request_freeze_report.md`
- `runs/read_only_phase1_approval_request_freeze/20260525T112000/metrics.yaml`
- `reports/read_only_next_step_selection_report.md`
- `runs/read_only_next_step_selection/20260525T111000/metrics.yaml`
- `reports/read_only_evidence_dependency_map_report.md`
- `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`
- `reports/read_only_step_execution_preflight_report.md`
- `runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V129 reports `audit_passed = true`,
`approval_request_freeze_complete = true`, frozen step
`phase1_mounted_stack_tcp_contact_measurement`, frozen worksheet
`tcp_contact_measurements.csv`, required phrase
`I approve this read-only measurement step`, packet Markdown SHA256
`91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d`,
packet status `approval_packet_created_not_approved`, packet approval status
`not_approved`, `freeze_authorizes_live_access = false`,
`freeze_authorizes_execution = false`,
`approved_read_only_evidence_created = false`, `overall_goal_complete = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v129 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v129 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V129 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v129-readonly-phase1-approval-request-freeze
```

Verified implementation commit:

```text
4bf07b2373af781eb35b20d13862afd9c5330907
```

V129 artifacts:

```text
scripts/audit_read_only_phase1_approval_request_freeze.py
tests/test_read_only_phase1_approval_request_freeze.py
runs/read_only_phase1_approval_request_freeze/20260525T112000
reports/read_only_phase1_approval_request_freeze_report.md
```

Key result:

```text
audit_passed = true
approval_request_freeze_complete = true
frozen_step_id = phase1_mounted_stack_tcp_contact_measurement
frozen_worksheet = tcp_contact_measurements.csv
approval_phrase_required = I approve this read-only measurement step
exact_step_id_required = true
packet_markdown_sha256 = 91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d
packet_status = approval_packet_created_not_approved
packet_audit_passed = true
packet_approval_status = not_approved
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
freeze_authorizes_live_access = false
freeze_authorizes_execution = false
freeze_creates_approved_evidence = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V130 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use the frozen phase1 request:
`phase1_mounted_stack_tcp_contact_measurement`, worksheet
`tcp_contact_measurements.csv`, and phrase
`I approve this read-only measurement step`. Instantiate a fresh run folder,
fill only `tcp_contact_measurements.csv`, finalize with the matching registered
step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage, execution preflight, the v127 dependency map, the v128
  selector, and the v129 freeze separate from approved evidence.
- Keep formula-convergence and tuned Fig.6 paper-platform evidence separate
  from full paper-equivalent parity.
- Do not accept any strict-terminal relaxation from v126; it is a budget audit
  only and accepts no gate change.
- Keep contact/setup-target acceptance, orientation gate acceptance, contact
  calibration, robustness proof, strict feasibility, and hardware readiness
  false unless a later audit supplies stronger evidence.

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

- `python3 -m py_compile scripts/audit_read_only_phase1_approval_request_freeze.py`
- `scripts/run_tests.sh tests/test_read_only_phase1_approval_request_freeze.py`
  reported `3 passed in 0.11s`.
- `python3 scripts/audit_read_only_phase1_approval_request_freeze.py --run-id 20260525T112000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v129 run
  directory.
- Full tests passed with `220 passed in 11.97s`.
- `git diff --check` passed.
