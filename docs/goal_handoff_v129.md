# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V129

Date: 2026-05-25

Use this after the v128 read-only next-step selection audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v128 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v129.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_next_step_selection_report.md`
- `runs/read_only_next_step_selection/20260525T111000/metrics.yaml`
- `reports/read_only_evidence_dependency_map_report.md`
- `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`
- `reports/read_only_step_execution_preflight_report.md`
- `runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml`
- `reports/read_only_step_approval_packet_coverage_report.md`
- `runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V128 reports `audit_passed = true`,
`selection_plan_complete = true`, candidate steps `5`, first candidate
`phase1_mounted_stack_tcp_contact_measurement`, first worksheet
`tcp_contact_measurements.csv`, required phrase
`I approve this read-only measurement step`, exact step ID required true,
approved packets `0`, execution-authorizing packets `0`,
live-access-authorizing packets `0`,
`approved_read_only_evidence_created = false`,
`selection_authorizes_live_access = false`,
`selection_authorizes_execution = false`, `overall_goal_complete = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v128 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v128 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V128 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v128-readonly-next-step-selection
```

V128 artifacts:

```text
scripts/audit_read_only_next_step_selection.py
tests/test_read_only_next_step_selection.py
runs/read_only_next_step_selection/20260525T111000
reports/read_only_next_step_selection_report.md
```

Key result:

```text
audit_passed = true
selection_plan_complete = true
candidate_step_count = 5
first_candidate_step_id = phase1_mounted_stack_tcp_contact_measurement
first_candidate_worksheet = tcp_contact_measurements.csv
approval_phrase_required = I approve this read-only measurement step
exact_step_id_required = true
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
approved_read_only_evidence_created = false
selection_authorizes_live_access = false
selection_authorizes_execution = false
selection_creates_approved_evidence = false
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V129 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, the first exact step to name is
`phase1_mounted_stack_tcp_contact_measurement`. Instantiate a fresh run folder,
fill only `tcp_contact_measurements.csv`, finalize with the matching registered
step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage, execution preflight, the v127 dependency map, and the
  v128 selector separate from approved evidence.
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

- `python3 -m py_compile scripts/audit_read_only_next_step_selection.py`
- `scripts/run_tests.sh tests/test_read_only_next_step_selection.py`
  reported `3 passed in 0.13s`.
- `python3 scripts/audit_read_only_next_step_selection.py --run-id 20260525T111000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v128 run
  directory.
- Full tests passed with `217 passed in 11.80s`.
- `git diff --check` passed.
