# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V119

Date: 2026-05-25

Use this after the v118 post-v117 evidence readiness audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v118 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v119.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v117_evidence_readiness_report.md`
- `runs/post_v117_evidence_readiness/20260525T092500/metrics.yaml`
- `reports/read_only_calibration_measurement_sop.md`
- `reports/contact_setup_target_acceptance_review_template_report.md`
- `reports/strict_terminal_constrained_optimization_report.md`
- `reports/weighted_profile_matrix_restatement_report.md`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: the project is not strict
paper-equivalent, not robust to contact/model perturbations, not contact
calibrated, and not hardware-ready. The UR10e adapted line is diagnostic
simulation only. V118 scans the actual post-v117 repository state and reports
`overall_goal_complete = false`, `completion_claim_allowed = false`,
`approved_read_only_run_count = 0`,
`approved_read_only_audit_passed_count = 0`,
`accepted_orientation_review_count = 0`,
`accepted_contact_setup_target_review_count = 0`,
`strict_terminal_pass_count = 0`, `closed_robustness_cell_count = 0`, and
`hardware_gate_report_exists = false`.

Concrete v119 objective:

Either execute only a safe, explicitly user-confirmed read-only subset of the
v87 SOP using the v93 read-only scaffold, v91 finalizer, and v90/v93 verifier,
or, if no such approval exists, continue only offline non-final work. With no
approval, avoid repeating v113-v116 matrices over the same policy, timing,
seed, and objective families. Use the v117 scaffold before accepting any
contact/setup-target definition. Do not move the real UR10e. Do not write TCP,
payload, CoG, URCap settings, OnRobot settings, RTDE registers,
zero/bias/filter settings, or run force control unless the user separately
approves that exact SOP step.
```

## Current Verified V118 Evidence

Authoritative clone:

```text
/home/andy/reproduce-tase
```

Expected branch:

```text
exp/tase-ur10e-v118-post-v117-evidence-readiness-audit
```

Verified implementation commit:

```text
a11668032fb01accde9ed55aaaf95c04b5465075
```

V118 evidence readiness artifacts:

```text
scripts/audit_post_v117_evidence_readiness.py
tests/test_post_v117_evidence_readiness.py
runs/post_v117_evidence_readiness/20260525T092500
reports/post_v117_evidence_readiness_report.md
```

Key result:

```text
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
```

## Recommended V119 Work

Start with explicit user approval before any live bench read. If a specific
read-only step is approved, instantiate a fresh run folder, collect only the
approved worksheet rows, finalize it, and audit it in approved-read-only mode.

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
