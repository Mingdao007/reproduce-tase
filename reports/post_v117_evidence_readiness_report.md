# Post-V117 Evidence Readiness Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v118-post-v117-evidence-readiness-audit`

Implementation commit: `IMPLEMENTATION_COMMIT_PENDING`

## Objective

Audit the actual post-v117 repository state for claim-closing evidence before
deciding whether the active reproduction goal can be marked complete. This
audit scans current read-only measurement runs, read-only run audits,
orientation-gate reviews, contact/setup-target reviews, strict terminal
optimization metrics, robustness matrix restatement metrics, and the hardware
gate report path.

No hardware command, live read, robot motion, configuration write, zeroing,
force-control step, contact/setup-target acceptance, orientation-gate
acceptance, or hardware-readiness claim is performed.

## Artifacts

- New audit script:
  `scripts/audit_post_v117_evidence_readiness.py`
- New audit run:
  `runs/post_v117_evidence_readiness/20260525T092500`
- New tests:
  `tests/test_post_v117_evidence_readiness.py`

## Result

The v118 audit reports:

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

The checklist remains incomplete for all claim-closing items:

| requirement | current evidence | status |
| --- | --- | --- |
| `approved_read_only_calibration_evidence` | 3 scaffold read-only runs, 0 approved evidence runs, 0 passed approved-read-only audits | Missing approval/evidence |
| `contact_setup_target_acceptance` | v117 contact/setup-target review audit passed, but latest decision is `not_accepted` and accepted reviews are 0 | Not accepted |
| `orientation_gate_acceptance` | v94 orientation review audit passed, but latest decision is `not_accepted` and accepted reviews are 0 | Not accepted |
| `strict_terminal_or_full_staged_feasibility` | v116 strict terminal pass count is `0`, best max-gate ratio is `2.11994927622362` | Not achieved |
| `robustness_to_contact_model_perturbations` | v111 closed robustness cells are `0`, accepted robustness proof is false | Not achieved |
| `hardware_readiness` | `reports/hardware_gate_report.md` does not exist | Not achieved |

## Claim Boundary

V118 is offline bookkeeping over existing artifacts. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a contact model, accept a setup target, relax a gate, calibrate
contact geometry, prove robustness, prove strict paper-equivalent feasibility,
or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/audit_post_v117_evidence_readiness.py`
  passed.
- `scripts/run_tests.sh tests/test_post_v117_evidence_readiness.py`
  passed with `3 passed in 0.24s`.
- `python3 scripts/audit_post_v117_evidence_readiness.py --run-id 20260525T092500`
  created the v118 audit run.
- `rg -n "&id|\*id" runs/post_v117_evidence_readiness/20260525T092500/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/post_v117_evidence_readiness/20260525T092500 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `184 passed in 7.74s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `BRANCH_PUSH_PENDING`.

## Next Step

The top blocker remains explicit approval for a safe read-only calibration
measurement step. Without that approval, continue only non-final offline work
and avoid repeating v113-v116 policy, timing, seed, and terminal-objective
families over the same accepted model.
