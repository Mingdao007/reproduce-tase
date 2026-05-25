# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V122

Date: 2026-05-25

Use this after the v121 read-only approval-packet coverage work. Verify every
claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v121 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v122.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/read_only_step_approval_packet_coverage_report.md`
- `runs/read_only_step_approval_packet_coverage/20260525T100500/metrics.yaml`
- `reports/read_only_step_approval_packet_report.md`
- `runs/read_only_step_approval_packet/20260525T095500/metrics.yaml`
- `runs/read_only_step_approval_packet_audit/20260525T095501/metrics.yaml`
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
registry and guards finalization/audit. V120 creates an audited
not-approved approval packet for
`phase1_mounted_stack_tcp_contact_measurement`. V121 extends audited
not-approved approval-packet coverage to every finalizer-eligible registered
step: coverage `5 / 5`, `missing_step_ids = []`, approved packets `0`,
execution-authorizing packets `0`, live-access-authorizing packets `0`, and
`do_not_mark_goal_complete = true`.

Concrete v122 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using one audited not-approved packet after the user approves that
exact registered step ID, the v93 read-only scaffold, v91/v119 finalizer, and
v90/v119 verifier, or, if no such approval exists, continue only offline
non-final work. With no approval, avoid repeating v113-v116 matrices over the
same policy, timing, seed, and objective families. Use the v117 scaffold
before accepting any contact/setup-target definition. Do not move the real
UR10e. Do not write TCP, payload, CoG, URCap settings, OnRobot settings, RTDE
registers, zero/bias/filter settings, or run force control unless the user
separately approves that exact SOP step.
```

## Current Verified V121 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v121-readonly-approval-packet-coverage
```

Verified implementation commit:

```text
5cd3b3d8d4bb8672a8c74ba5832439c3faba7c7a
```

V121 artifacts:

```text
scripts/audit_read_only_step_approval_packet_coverage.py
tests/test_read_only_step_approval_packet_coverage.py
runs/read_only_step_approval_packet/20260525T100000
runs/read_only_step_approval_packet/20260525T100100
runs/read_only_step_approval_packet/20260525T100200
runs/read_only_step_approval_packet/20260525T100300
runs/read_only_step_approval_packet_audit/20260525T100001
runs/read_only_step_approval_packet_audit/20260525T100101
runs/read_only_step_approval_packet_audit/20260525T100201
runs/read_only_step_approval_packet_audit/20260525T100301
runs/read_only_step_approval_packet_coverage/20260525T100500
reports/read_only_step_approval_packet_coverage_report.md
```

Key result:

```text
audit_passed = true
coverage_complete = true
required_finalizer_step_count = 5
covered_step_count = 5
missing_step_ids = []
approval_packet_count = 5
approval_packet_audit_count = 5
approved_packet_count = 0
execution_authorizing_packet_count = 0
live_access_authorizing_packet_count = 0
heavy_payloads = []
do_not_mark_goal_complete = true
```

Covered steps:

```text
phase1_mounted_stack_tcp_contact_measurement
phase2_ksm_contact_patch_convention
phase3_plane_normal_external_measurement
phase4_force_source_read_only_comparison
phase5_orientation_gate_semantics_evidence
```

## Recommended V122 Work

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
