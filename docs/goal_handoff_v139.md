# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V139

Date: 2026-05-25

Use this after the v138 post-v137 completion gate audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v138 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v139.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v137_completion_gate_report.md`
- `runs/post_v137_completion_gate/20260525T125000/metrics.yaml`
- `reports/strict_vs_diagnostic_margin_separation_report.md`
- `runs/strict_vs_diagnostic_margin_separation/20260525T124000/metrics.yaml`
- `reports/post_v135_completion_gate_report.md`
- `runs/post_v135_completion_gate/20260525T123000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V138 reports `audit_passed = true`,
`overall_goal_complete = false`, `completion_claim_allowed = false`,
`do_not_mark_goal_complete = true`, top blocker
`approved_read_only_calibration_evidence`, approved read-only runs `0`,
passed approved-read-only audits `0`, accepted orientation reviews `0`,
accepted contact/setup-target reviews `0`, strict terminal pass count `0`,
closed robustness cells `0`, hardware gate report false, readiness artifact
count `4`, `readiness_completion_evidence_ids = []`,
`readiness_artifacts_are_non_evidence = true`,
`finalization_rehearsal_is_non_evidence = true`,
`margin_separation_is_non_evidence = true`,
`margin_strict_to_diagnostic_orientation_ratio = 59.31389790209757`,
`margin_v85_can_close_strict_paper_equivalent_goal = false`, and
`margin_replacement_gate_accepted = false`.

The next branch should execute only a safe read-only SOP subset after explicit
user confirmation using one exact audited packet, the scaffold, finalizer, and
verifier, or continue only non-final offline simulation/paper-platform work
identified by the v95-v138 audits. Use the v117 scaffold before accepting any
contact/setup-target definition. Keep strict paper-equivalent setup, v38
relaxed trajectory-after-setup, and v63-v138 diagnostic staged labels
separate. Do not move or configure the real UR10e; real hardware work is
read-only unless a separate approved SOP exists.
```

## Current V138 Evidence

Expected branch:

```text
exp/tase-ur10e-v138-post-margin-completion-gate
```

V138 artifacts:

```text
scripts/audit_post_v137_completion_gate.py
tests/test_post_v137_completion_gate.py
runs/post_v137_completion_gate/20260525T125000
reports/post_v137_completion_gate_report.md
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
readiness_artifact_count = 4
readiness_completion_evidence_ids = []
readiness_artifacts_are_non_evidence = true
finalization_rehearsal_is_non_evidence = true
margin_separation_is_non_evidence = true
margin_strict_to_diagnostic_orientation_ratio = 59.31389790209757
margin_v85_can_close_strict_paper_equivalent_goal = false
margin_replacement_gate_accepted = false
```

## Recommended V139 Work

Start with explicit user approval before any live bench read. If the user
approves one exact audited packet, use only that packet's exact step ID and
worksheet scope. Instantiate a fresh run folder, fill only valid rows for the
approved worksheet, finalize with the matching registered step ID, and audit in
approved-read-only mode. Do not bundle multiple registered steps into one
approval.

If no live read-only step is approved, continue only non-final offline probes.
Do not repeat the v113-v116 policy, timing, and terminal-objective families
over the same accepted contact model and seeds. Keep v127-v138 readiness,
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

- `python3 -m py_compile scripts/audit_post_v137_completion_gate.py`
- `scripts/run_tests.sh tests/test_post_v137_completion_gate.py`
  reported `4 passed in 0.43s`.
- `python3 scripts/audit_post_v137_completion_gate.py --run-id 20260525T125000`
- Full tests reported `259 passed in 30.32s`.
- YAML anchor check found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads larger than 1 MB in the v138 run
  directory.
- `git diff --check` passed.
