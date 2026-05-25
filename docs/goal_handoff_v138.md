# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V138

Date: 2026-05-25

Use this after the v137 strict-vs-diagnostic margin separation audit. Verify
every claim from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v137 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v138.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/strict_vs_diagnostic_margin_separation_report.md`
- `runs/strict_vs_diagnostic_margin_separation/20260525T124000/metrics.yaml`
- `reports/post_v135_completion_gate_report.md`
- `runs/post_v135_completion_gate/20260525T123000/metrics.yaml`
- `reports/strict_terminal_relaxation_budget_report.md`
- `runs/strict_terminal_relaxation_budget/20260525T105000/metrics.yaml`
- `reports/contact_orientation_calibration_margin_report.md`
- `runs/contact_orientation_calibration_margin/20260524T235723/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V137 reports `audit_passed = true`,
`strict_vs_diagnostic_margin_separation_complete = true`,
`diagnostic_required_normal_rotation_rad = 0.0005664520369604714`,
`strict_orientation_increase_rad = 0.0335984782867086`,
`strict_to_diagnostic_orientation_margin_ratio = 59.31389790209757`,
`minimum_uniform_multiplier = 2.11994927622362`,
`minimum_uniform_requires_all_three_scalar_gates = true`,
`v85_margin_can_close_strict_paper_equivalent_goal = false`,
`replacement_gate_accepted = false`, approved read-only runs `0`, passed
approved-read-only audits `0`, `overall_goal_complete = false`,
`completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v137 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v137 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V137 Evidence

Expected branch:

```text
exp/tase-ur10e-v137-strict-diagnostic-margin-separation
```

V137 artifacts:

```text
scripts/audit_strict_vs_diagnostic_margin_separation.py
tests/test_strict_vs_diagnostic_margin_separation.py
runs/strict_vs_diagnostic_margin_separation/20260525T124000
reports/strict_vs_diagnostic_margin_separation_report.md
```

Key result:

```text
audit_passed = true
strict_vs_diagnostic_margin_separation_complete = true
diagnostic_required_normal_rotation_rad = 0.0005664520369604714
strict_orientation_increase_rad = 0.0335984782867086
strict_to_diagnostic_orientation_margin_ratio = 59.31389790209757
minimum_uniform_multiplier = 2.11994927622362
minimum_uniform_requires_all_three_scalar_gates = true
v85_margin_can_close_strict_orientation = false
v85_margin_can_close_strict_uniform_relaxation = false
v85_margin_can_close_strict_paper_equivalent_goal = false
replacement_gate_accepted = false
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
overall_goal_complete = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V138 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v137 readiness,
sequence, acceptance, row-quality, finalization-rehearsal, completion-gate, and
margin-separation artifacts separate from approved evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user.

## Validation

- `python3 -m py_compile scripts/audit_strict_vs_diagnostic_margin_separation.py`
- `scripts/run_tests.sh tests/test_strict_vs_diagnostic_margin_separation.py`
  reported `4 passed in 0.17s`.
- `python3 scripts/audit_strict_vs_diagnostic_margin_separation.py --run-id 20260525T124000`
- Temporary verifier rerun:
  `python3 scripts/audit_strict_vs_diagnostic_margin_separation.py --output-dir /tmp/tase_v137_margin_verify --run-id VERIFY_V137`
- Full tests reported `255 passed in 29.95s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v137 run
  directory.
- `git diff --check` passed.
