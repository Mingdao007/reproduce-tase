# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V118

Date: 2026-05-25

Use this after the v117 contact/setup-target acceptance review scaffold. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v117 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v118.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/offline_completion_blockers_report.md`
- `reports/strict_feasibility_blockers_report.md`
- `reports/remaining_blocker_prioritization_report.md`
- `reports/strict_feasibility_policy_probe_report.md`
- `reports/strict_command_limited_stage_a_report.md`
- `reports/explicit_stage_a_constraint_probe_report.md`
- `reports/strict_terminal_constrained_optimization_report.md`
- `reports/contact_setup_target_acceptance_review_template_report.md`
- `runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
- `runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
- `runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
- `runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml`
- `runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml`
- `runs/contact_setup_target_acceptance_review/20260525T091500/metrics.yaml`
- `runs/contact_setup_target_acceptance_review_audit/20260525T091501/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- `reports/orientation_gate_acceptance_review_template_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V112 ranks the remaining blockers: top priority is
`approved_read_only_calibration_evidence`, remaining blocker count is `6`,
live/approval-blocked count is `4`, offline-actionable non-final count is `2`,
closed cells remain `0`, candidate matrix complete is `false`, and
`do_not_mark_goal_complete = true`. V113-v116 did not recover strict setup:
v113 strict setup `0 / 8`, v114 strict setup-chain `0 / 4`, v115 strict
setup-path `0 / 5`, and v116 strict terminal `0 / 12`. V117 adds a separate
contact/setup-target acceptance review scaffold and audit. It defaults to
`not_accepted`, cites v116 as the latest terminal compatibility boundary,
reports audit pass with `violations = []`, and keeps supports-contact-model,
supports-setup-target, calibration, hardware-readiness, and goal-completion
claims false.

Concrete v118 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, avoid repeating v113-v116 matrices over the same policy, timing,
seed, and objective families. The practical next blocker is approved read-only
calibration evidence. Do not move the real UR10e. Do not write TCP, payload,
CoG, URCap settings, OnRobot settings, RTDE registers, zero/bias/filter
settings, or run force control unless the user separately approves that exact
SOP step.
```

## Current Verified V117 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v117-contact-setup-target-review-scaffold
```

Verified implementation commit:

```text
IMPLEMENTATION_COMMIT_PENDING
```

V117 contact/setup-target acceptance review artifacts:

```text
templates/contact_setup_target_acceptance_review/
scripts/create_contact_setup_target_acceptance_review.py
scripts/audit_contact_setup_target_acceptance_review.py
tests/test_contact_setup_target_acceptance_review_template.py
runs/contact_setup_target_acceptance_review/20260525T091500
runs/contact_setup_target_acceptance_review_audit/20260525T091501
reports/contact_setup_target_acceptance_review_template_report.md
```

Key result:

```text
review_status = review_scaffold_not_executed
audit_passed = true
violations = []
contact_setup_target_acceptance.decision = not_accepted
supports_contact_model_update = false
supports_setup_target_update = false
contact_calibration_claim = false
hardware_readiness = false
do_not_mark_goal_complete = true
```

## Recommended V118 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, then run:

```bash
python3 scripts/finalize_read_only_calibration_measurement_evidence.py <run-folder> \
  --confirmation-phrase "I approve this read-only measurement step" \
  --approved-step-id <approved-step-id> \
  --operator <operator> \
  --live-hardware-accessed true

python3 scripts/audit_read_only_calibration_measurement_run.py <run-folder> \
  --audit-mode approved-read-only
```

If no live read-only step is approved, continue only non-final offline probes:

- Use v117 as the current acceptance-scaffold boundary for contact/setup-target
  changes.
- Treat `approved_read_only_calibration_evidence` as the top overall blocker.
- Avoid repeating v113-v116 matrices over the same policy, timing, seed, and
  objective families.
- Keep gate acceptance, contact calibration, hardware readiness, failed-cell
  closure, canonical controller changes, and robustness claims false unless a
  later audit supplies stronger evidence.

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
