# Goal Handoff For Next Codex: T-ASE UR10e Reproduction V145

Date: 2026-05-25

Use this after the v144 phase1 packet freshness audit. Verify every claim from
repository state before editing files.

## Copy-Paste Goal Prompt

```text
Continue the T-ASE finite-time UR10e + OnRobot reproduction in
`/home/andy/reproduce-tase` from the current verified v144 state.

Before changing anything, read:

- `docs/goal.md`
- `docs/goal_handoff_v145.md`
- `reports/completion_audit.md`
- `reports/ITERATION_LOG.md`
- `reports/DECISION_RECORD.md`
- `runs/RUN_ARTIFACTS_MANIFEST.md`
- `reports/phase1_packet_freshness_after_v143_report.md`
- `runs/phase1_packet_freshness_after_v143/20260525T180000/metrics.yaml`
- `reports/post_v142_completion_gate_report.md`
- `runs/post_v142_completion_gate/20260525T170000/metrics.yaml`
- `configs/read_only_sop_step_registry.yaml`

Then run:

- `git status --short --branch`
- `git log --oneline --decorate -6`
- `git remote -v`

Preserve the current claim boundary: formula-faithful Python paper-platform
convergence and tuned Fig.6 landmark evidence remain separate, full
paper-equivalent numerical parity is not achieved, and the UR10e adapted line
is diagnostic simulation only. V144 confirms the exact phase1 packet is still
fresh and not approved: `phase1_packet_fresh = true`,
`packet_hash_unchanged = true`,
`phase1_packet_still_not_approved = true`,
`post_v143_completion_gate_binding = true`, approved read-only runs `0`,
passed approved-read-only audits `0`, `approval_record_created = false`,
`live_access_authorized_now = false`, `execution_authorized_now = false`,
`approved_read_only_evidence_created = false`, and
`do_not_mark_goal_complete = true`.

The exact first read-only candidate remains
`phase1_mounted_stack_tcp_contact_measurement`, scoped to
`tcp_contact_measurements.csv`, but it may only be executed after explicit user
confirmation with the exact registered phrase
`I approve this read-only measurement step` and exact step scope. Without that
approval, continue only non-final offline work. Do not upgrade v127-v144
readiness/status/frontier/freshness artifacts into evidence. Do not repeat the
v113-v116 strict-policy/terminal family over the same accepted contact model
and seeds, and do not rerun gate-blocked robustness cells as closure evidence
before approved contact/gate evidence exists. Keep strict paper-equivalent
setup, v38 relaxed trajectory-after-setup, and v63-v144 diagnostic staged
labels separate. Do not move or configure the real UR10e; real hardware work
is read-only unless a separate approved SOP exists.
```

## Current V144 Evidence

Expected branch:

```text
exp/tase-ur10e-v144-phase1-packet-freshness
```

V144 artifacts:

```text
scripts/audit_phase1_packet_freshness_after_v143.py
tests/test_phase1_packet_freshness_after_v143.py
runs/phase1_packet_freshness_after_v143/20260525T180000
reports/phase1_packet_freshness_after_v143_report.md
```

Key result:

```text
audit_passed = true
phase1_packet_fresh = true
registry_matches_frozen_packet = true
packet_hash_unchanged = true
frozen_step_id = phase1_mounted_stack_tcp_contact_measurement
frozen_worksheet = tcp_contact_measurements.csv
approval_phrase_required = I approve this read-only measurement step
phase1_packet_still_not_approved = true
post_v143_completion_gate_binding = true
approved_read_only_run_count = 0
approved_read_only_audit_passed_count = 0
readiness_completion_evidence_ids = []
approval_record_created = false
live_access_authorized_now = false
execution_authorized_now = false
approved_read_only_evidence_created = false
completion_claim_allowed = false
do_not_mark_goal_complete = true
```

## Recommended V145 Work

If the user gives the exact approval phrase and exact phase1 scope, use only
that one audited packet and registered step. Instantiate a fresh scaffold run,
fill only valid `tcp_contact_measurements.csv` rows, finalize with
`phase1_mounted_stack_tcp_contact_measurement`, and audit in
approved-read-only mode.

If no exact approval exists, continue only non-final offline work that does not
upgrade v127-v144 readiness/status/frontier/freshness artifacts into evidence.
Do not rerun the v113-v116 strict-policy/terminal family or gate-blocked
robustness rows as closure evidence before approved contact/gate evidence
exists.

## Safety Rules

- Do not move the real UR10e.
- Do not run real force control.
- Do not write TCP, payload, CoG, URCap settings, zeroing/biasing/filtering,
  OnRobot configuration, or RTDE registers unless the user approves a separate
  exact SOP step.
- Read-only hardware checks are allowed only if relevant, safe, and explicitly
  confirmed by the user using the exact registered approval scope.

## Validation

- `python3 -m py_compile scripts/audit_phase1_packet_freshness_after_v143.py`
- `scripts/run_tests.sh tests/test_phase1_packet_freshness_after_v143.py`
  reported `4 passed in 0.20s`.
- `python3 scripts/audit_phase1_packet_freshness_after_v143.py --run-id 20260525T180000`

Full tests, YAML anchor scan, raw/heavy artifact scan, and `git diff --check`
are pending final closeout for this branch.
