# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V120

Date: 2026-05-25

Use this after the v119 read-only SOP step registry guard. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v119 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v120.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v117_evidence_readiness_report.md`
- `reports/read_only_sop_step_registry_guard_report.md`
- `configs/read_only_sop_step_registry.yaml`
- `runs/read_only_sop_step_registry_audit/20260525T094000/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/contact_setup_target_acceptance_review_template_report.md`

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
`0`, and no hardware gate report. V119 adds
`configs/read_only_sop_step_registry.yaml` and guards the read-only finalizer
and approved-read-only audit so future finalization must use a registered exact
step ID and may only populate that step's allowed worksheet rows.

Concrete v120 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using one registered finalizer-eligible step ID, the v93 read-only
scaffold, v91/v119 finalizer, and v90/v119 verifier, or, if no such approval
exists, continue only offline non-final work. With no approval, avoid
repeating v113-v116 matrices over the same policy, timing, seed, and objective
families. Use the v117 scaffold before accepting any contact/setup-target
definition. Do not move the real UR10e. Do not write TCP, payload, CoG, URCap
settings, OnRobot settings, RTDE registers, zero/bias/filter settings, or run
force control unless the user separately approves that exact SOP step.
```

## Current Verified V119 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v119-readonly-step-registry-finalizer-guard
```

Verified implementation commit:

```text
c1c8febca4a41009d1fb8b55e19cfbe64931c17b
```

V119 artifacts:

```text
configs/read_only_sop_step_registry.yaml
scripts/audit_read_only_sop_step_registry.py
scripts/finalize_read_only_calibration_measurement_evidence.py
scripts/audit_read_only_calibration_measurement_run.py
templates/read_only_calibration_measurement/
tests/test_read_only_calibration_measurement_template.py
runs/read_only_sop_step_registry_audit/20260525T094000
reports/read_only_sop_step_registry_guard_report.md
```

Key result:

```text
registry_audit_passed = true
violations = []
step_count = 6
finalizer_eligible_step_count = 5
registry_authorizes_robot_motion = false
registry_authorizes_configuration_writes = false
registry_authorizes_zeroing_or_biasing = false
registry_authorizes_force_control = false
registry_accepts_contact_model = false
registry_accepts_setup_target = false
registry_accepts_orientation_gate = false
registry_establishes_hardware_readiness = false
```

## Recommended V120 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, fill only the
approved step's worksheet rows, finalize with the registered step ID, and audit
in approved-read-only mode.

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
