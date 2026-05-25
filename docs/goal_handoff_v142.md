# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V142

Date: 2026-05-25

Use this after the v141 post-v140 completion-gate audit. Verify every claim
from repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v141 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v142.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/post_v140_completion_gate_report.md`
- `runs/post_v140_completion_gate/20260525T150000/metrics.yaml`
- `reports/post_v139_continuation_boundary_report.md`
- `runs/post_v139_continuation_boundary/20260525T140000/metrics.yaml`
- `reports/full_reproduction_status_after_v138_report.md`
- `runs/full_reproduction_status_after_v138/20260525T130000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V141 confirms that v139 status and v140
continuation-boundary artifacts are non-evidence: `readiness_artifact_count =
6`, `readiness_completion_evidence_ids = []`,
`status_answer_is_non_evidence = true`,
`continuation_boundary_is_non_evidence = true`,
`approved_read_only_run_count = 0`,
`approved_read_only_audit_passed_count = 0`, and
`do_not_mark_goal_complete = true`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not repeat the v113-v116
strict-policy/terminal family over the same accepted contact model and seeds.
Use the v117 scaffold before accepting any contact/setup-target definition.
Keep strict paper-equivalent setup, v38 relaxed trajectory-after-setup, and
v63-v141 diagnostic staged labels separate. Do not move or configure the real
UR10e; real hardware work is read-only unless a separate approved SOP exists.
```

## Current V141 Evidence

Expected branch:

```text
exp/tase-ur10e-v141-post-v140-completion-gate
```

V141 artifacts:

```text
scripts/audit_post_v140_completion_gate.py
tests/test_post_v140_completion_gate.py
runs/post_v140_completion_gate/20260525T150000
reports/post_v140_completion_gate_report.md
```

Key result:

```text
audit_passed = true
overall_goal_complete = false
completion_claim_allowed = false
readiness_artifact_count = 6
readiness_completion_evidence_ids = []
readiness_artifacts_are_non_evidence = true
status_answer_is_non_evidence = true
continuation_boundary_is_non_evidence = true
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
v140_read_only_sop_can_execute_now = false
v140_live_access_authorized_now = false
v140_execution_authorized_now = false
do_not_mark_goal_complete = true
```

## Recommended V142 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that is not a
repeat of the v113-v116 strict-feasibility policy and terminal-objective
family. Do not upgrade v127-v141 readiness, sequence, acceptance, row-quality,
finalization-rehearsal, completion-gate, margin-separation, status,
continuation-boundary, or post-continuation-gate artifacts into evidence.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_post_v140_completion_gate.py`
- `scripts/run_tests.sh tests/test_post_v140_completion_gate.py`
  reported `4 passed in 0.44s`.
- `python3 scripts/audit_post_v140_completion_gate.py --run-id 20260525T150000`
- Full tests passed with `271 passed in 30.76s`.
- YAML anchor scan found no anchors in the generated metrics.
- Raw/heavy artifact scan found no payloads in the v141 run artifact.
- `git diff --check` passed.
