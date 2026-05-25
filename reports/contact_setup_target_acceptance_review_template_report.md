# Contact Setup Target Acceptance Review Template Report

Date: 2026-05-25

Branch: `exp/tase-ur10e-v117-contact-setup-target-review-scaffold`

Implementation commit: `f89b1dc4be31b213a28b493a277137c14e1977a0`

## Objective

Create a separate, non-default review path for any future contact model or
setup-target definition change. The scaffold must default to `not_accepted`,
cite the latest v116 strict terminal compatibility boundary, and preserve all
hardware, calibration, gate-relaxation, paper-equivalent, robustness, and
hardware-readiness claim boundaries.

No hardware command, live read, TCP/payload/configuration write, zeroing,
force-control step, contact calibration, setup-target acceptance, or gate
acceptance is performed.

## Artifacts

- New template:
  `templates/contact_setup_target_acceptance_review/`
- New scaffold command:
  `scripts/create_contact_setup_target_acceptance_review.py`
- New audit command:
  `scripts/audit_contact_setup_target_acceptance_review.py`
- New scaffold run:
  `runs/contact_setup_target_acceptance_review/20260525T091500`
- New scaffold audit:
  `runs/contact_setup_target_acceptance_review_audit/20260525T091501`
- New tests:
  `tests/test_contact_setup_target_acceptance_review_template.py`

## Result

The review scaffold records:

```text
status = review_scaffold_not_executed
source_read_only_run = null
source_run_audit = null
approved_read_only_audit_passed = false
latest_terminal_optimization = runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml
strict_terminal_pass_count = 0
best_max_gate_ratio = 2.11994927622362
v56_strict_best_max_gate_ratio = 2.413534442118322
contact_setup_target_acceptance.decision = not_accepted
contact_setup_target_acceptance.review_only = true
supports_contact_model_update = false
supports_setup_target_update = false
supports_force_source_update = false
supports_gate_relaxation = false
supports_hardware_claim = false
hardware_readiness = false
do_not_mark_goal_complete = true
```

The audit passed:

```text
audit_passed = true
violations = []
review_status = review_scaffold_not_executed
decision = not_accepted
review_only = true
live_hardware_accessed = false
robot_motion_commanded = false
configuration_written = false
force_control_run = false
supports_contact_model_update = false
supports_setup_target_update = false
supports_hardware_claim = false
hardware_readiness = false
heavy_payloads = []
```

The audit rejects drift toward an accepted contact/setup-target definition,
including non-null accepted-definition fields, changed decision status, and any
false claim-boundary or verdict field changing to true.

## Claim Boundary

V117 is offline scaffold/audit work only. It does not collect live
measurements, execute the read-only SOP, move the UR10e, write configuration,
zero/bias/filter the force sensor, run force control, reconcile force-source
frames, accept a contact model, accept a setup target, relax a gate, calibrate
contact geometry, prove robustness, prove strict paper-equivalent feasibility,
or make a hardware-readiness claim.

## Validation

- `python3 -m py_compile scripts/create_contact_setup_target_acceptance_review.py scripts/audit_contact_setup_target_acceptance_review.py`
  passed.
- `scripts/run_tests.sh tests/test_contact_setup_target_acceptance_review_template.py`
  passed with `3 passed in 0.35s`.
- `python3 scripts/create_contact_setup_target_acceptance_review.py --review-id 20260525T091500`
  created the v117 scaffold.
- `python3 scripts/audit_contact_setup_target_acceptance_review.py runs/contact_setup_target_acceptance_review/20260525T091500 --run-id 20260525T091501`
  passed.
- `rg -n "&id|\*id" runs/contact_setup_target_acceptance_review/20260525T091500/metrics.yaml runs/contact_setup_target_acceptance_review_audit/20260525T091501/metrics.yaml`
  found no YAML anchors in the root summary metrics.
- `find runs/contact_setup_target_acceptance_review/20260525T091500 runs/contact_setup_target_acceptance_review_audit/20260525T091501 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
  found no raw or heavy payload artifacts.
- `scripts/run_tests.sh`
  passed with `181 passed in 7.50s`.
- `git diff --check`
  passed.
- Branch push was verified at
  `f89b1dc4be31b213a28b493a277137c14e1977a0`.

## Next Step

Without explicit live bench approval, continue only non-final offline work.
The top practical blocker remains approved read-only calibration evidence. If
future evidence is collected, use this separate review scaffold before any
contact model or setup-target definition is accepted.
