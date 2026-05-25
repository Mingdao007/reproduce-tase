# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V124

Date: 2026-05-25

Use this after the v123 post-v122 completion gate. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v123 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v124.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v122_completion_gate_report.md`
- `runs/post_v122_completion_gate/20260525T102000/metrics.yaml`
- `reports/read_only_step_execution_preflight_report.md`
- `runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml`
- `reports/read_only_step_approval_packet_coverage_report.md`
- `runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml`
- `reports/read_only_sop_step_registry_guard_report.md`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V118 scans the actual post-v117 repository state and reports
no approved read-only evidence, no accepted orientation review, no accepted
contact/setup-target review, strict terminal pass `0`, closed robustness cells
`0`, and no hardware gate report. V119 adds an exact read-only SOP step
registry and guards finalization/audit. V120 creates an audited not-approved
approval packet for `phase1_mounted_stack_tcp_contact_measurement`. V121
extends audited not-approved approval-packet coverage to every
finalizer-eligible registered step. V122 verifies the offline command path
from audited packet to future scaffold/finalizer/approved-read-only audit for
all `5 / 5` finalizer-eligible steps. V123 scans readiness artifacts together
with real evidence paths and reports `overall_goal_complete = false`,
`completion_claim_allowed = false`, approved read-only runs `0`, passed
approved-read-only audits `0`, accepted orientation reviews `0`, accepted
contact/setup-target reviews `0`, strict terminal pass `0`, closed robustness
cells `0`, no hardware gate report, and
`readiness_artifacts_are_non_evidence = true`.

Concrete v124 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using one audited not-approved packet after the user approves that
exact registered step ID, the v93 read-only scaffold, v91/v119 finalizer,
v90/v119 verifier, and v122 preflight command path, or, if no such approval
exists, continue only offline non-final work. With no approval, avoid
repeating v113-v116 matrices over the same policy, timing, seed, and
objective families. Use the v117 scaffold before accepting any contact/setup-target
definition. Do not move the real UR10e. Do not write TCP, payload, CoG,
URCap settings, OnRobot settings, RTDE registers, zero/bias/filter settings,
or run force control unless the user separately approves that exact SOP step.
```

## Current Verified V123 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v123-post-v122-completion-gate
```

Verified implementation commit:

```text
ae2abb566b12dbc348a0675babe8f33f08c608bc
```

V123 artifacts:

```text
scripts/audit_post_v122_completion_gate.py
tests/test_post_v122_completion_gate.py
runs/post_v122_completion_gate/20260525T102000
reports/post_v122_completion_gate_report.md
```

Key result:

```text
audit_passed = true
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
top_blocker = approved_read_only_calibration_evidence
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
accepted_orientation_review_count = 0
accepted_contact_setup_target_review_count = 0
strict_terminal_pass_count = 0
closed_robustness_cell_count = 0
hardware_gate_report_exists = false
readiness_artifacts_are_non_evidence = true
```

## Recommended V124 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, instantiate a fresh run folder, fill only
that registered step's allowed worksheet, finalize with the matching
registered step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Keep packet coverage and preflight readiness separate from evidence.
- Keep contact/setup-target acceptance, orientation gate acceptance, contact
  calibration, robustness proof, strict feasibility, and hardware readiness
  false unless a later audit supplies stronger evidence.
- Avoid repeating v113-v116 policy, command-limiting, explicit-constraint, or
  terminal minimax experiments over the same accepted model and seeds.

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
