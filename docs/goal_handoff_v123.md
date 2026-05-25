# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V123

Date: 2026-05-25

Use this after the v122 read-only execution-preflight work. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v122 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v123.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_step_execution_preflight_report.md`
- `runs/read_only_step_execution_preflight/20260525T101000/metrics.yaml`
- `reports/read_only_step_approval_packet_coverage_report.md`
- `runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml`
- `reports/read_only_step_approval_packet_report.md`
- `reports/read_only_sop_step_registry_guard_report.md`
- `configs/read_only_sop_step_registry.yaml`
- `reports/post_v117_evidence_readiness_report.md`

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
all `5 / 5` finalizer-eligible steps, with approved packets `0`,
execution-authorizing packets `0`, live-access-authorizing packets `0`,
`preflight_authorizes_execution = false`,
`approved_read_only_evidence_created = false`, and
`do_not_mark_goal_complete = true`.

Concrete v123 objective:

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

## Current Verified V122 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v122-readonly-execution-preflight
```

V122 artifacts:

```text
scripts/audit_read_only_step_execution_preflight.py
tests/test_read_only_step_execution_preflight.py
runs/read_only_step_execution_preflight/20260525T101000
reports/read_only_step_execution_preflight_report.md
```

Key result:

```text
audit_passed = true
finalizer_eligible_step_count = 5
preflight_ready_step_count = 5
missing_ready_step_ids = []
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
explicit_user_approval_required = true
preflight_authorizes_live_access = false
preflight_authorizes_execution = false
approved_read_only_evidence_created = false
do_not_mark_goal_complete = true
```

Ready steps:

```text
phase1_mounted_stack_tcp_contact_measurement
phase2_ksm_contact_patch_convention
phase3_plane_normal_external_measurement
phase4_force_source_read_only_comparison
phase5_orientation_gate_semantics_evidence
```

## Recommended V123 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, instantiate a fresh run folder, fill only
that registered step's allowed worksheet, finalize with the matching
registered step ID, and audit in approved-read-only mode.

If no live read-only step is approved, continue only non-final offline probes:

- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
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
