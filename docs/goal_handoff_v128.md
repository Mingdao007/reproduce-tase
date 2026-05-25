# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V128

Date: 2026-05-25

Use this after the v127 read-only evidence dependency-map audit. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v127 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v128.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_evidence_dependency_map_report.md`
- `runs/read_only_evidence_dependency_map/20260525T110000/metrics.yaml`
- `reports/strict_terminal_relaxation_budget_report.md`
- `runs/strict_terminal_relaxation_budget/20260525T105000/metrics.yaml`
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
is diagnostic simulation only. V127 reports `audit_passed = true`,
`dependency_map_complete = true`, mapped readiness checks `5 / 5`, mapped
finalizer steps `5 / 5`, packet-covered steps `5 / 5`, preflight-ready steps
`5 / 5`, approved packets `0`, execution-authorizing packets `0`,
live-access-authorizing packets `0`,
`approved_read_only_evidence_created = false`,
`explicit_user_approval_required = true`, `overall_goal_complete = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v127 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v127 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V127 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v127-readonly-evidence-dependency-map
```

Verified implementation commit:

```text
9b494221728e1ff461fc5f6d6c13381a5f3c12f4
```

V127 artifacts:

```text
scripts/audit_read_only_evidence_dependency_map.py
tests/test_read_only_evidence_dependency_map.py
runs/read_only_evidence_dependency_map/20260525T110000
reports/read_only_evidence_dependency_map_report.md
```

Key result:

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

## Recommended V128 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, instantiate a fresh run folder, fill only
that registered step's allowed worksheet, finalize with the matching
registered step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage, execution preflight, and the v127 dependency map
  separate from approved evidence.
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

- `python3 -m py_compile scripts/audit_read_only_evidence_dependency_map.py`
- `scripts/run_tests.sh tests/test_read_only_evidence_dependency_map.py`
  reported `3 passed in 0.21s`.
- `python3 scripts/audit_read_only_evidence_dependency_map.py --run-id 20260525T110000`
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v127 run
  directory.
- Full tests passed with `214 passed in 11.67s`.
- `git diff --check` passed.
