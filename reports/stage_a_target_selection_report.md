# Stage A Target Selection Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v58-stage-a-target-selection`

## Scope

This iteration chooses the setup label for the next UR10e adapted Stage A
simulation prototype. It does not implement a new controller and does not make
a path, trajectory, paper-equivalent, or hardware-readiness claim.

No real UR10e motion, TCP writes, payload writes, URCap writes, ROS config
writes, or OnRobot configuration changes were performed.

## Decision

Added:

- `configs/ur10e_adapted_stage_a_target.yaml`

The selected target label is:

```text
ur10e_adapted_terminal_setup_diagnostic
```

Reason:

- strict paper-equivalent setup remains blocked by v56 gate-definition
  evidence
- v38 relaxed trajectory-after-setup applies to an existing slowed trajectory
  matrix, not to a terminal target for the next controller prototype
- v57 diagnostic terminal setup has one explicitly labeled passing candidate
  under a diagnostic gate

## Selected Target

Source:

- `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml`
- `runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml`

Target joint vector:

```text
q_rad = [
  -1.1745579135426345e-08,
  -0.02440152369247043,
  -0.00048297839388595083,
  0.0002982283198967393,
  2.405416739224147e-10,
  0.12671314216940235,
]
```

Target TCP:

```text
tcp_m = [0.001970353198813028, 4.032096983994156e-11, -0.00031401714282958126]
```

Diagnostic-gate source errors:

- force error: `0.005097546556703136 N`
- x/y error: `0.0030075762251302427 m`
- orientation error: `0.07240605683117833 rad`
- target contact count: `1`

## Limits

This target is only a simulation target for the next controller prototype. It
must not be relabeled as:

- strict paper-equivalent setup
- v38 trajectory-after-relaxed-setup
- path feasibility
- trajectory feasibility
- hardware readiness

## Next Step

Implement or evaluate any next Stage A controller only against the selected
diagnostic terminal setup target, unless a new decision explicitly changes the
target setup label.

## Verification

- `scripts/run_tests.sh tests/test_terminal_setup_gate.py` -> `3 passed`
- `python3 -m py_compile src/tase_repro/terminal_setup_gate.py scripts/evaluate_terminal_setup_gate.py`
- `scripts/run_tests.sh` -> `93 passed in 2.49s`
- `git diff --check` passed
