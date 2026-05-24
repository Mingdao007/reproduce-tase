# Adapted Terminal Setup Diagnostic Gate Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v57-adapted-terminal-gate`

## Scope

This iteration turns the v56 gate-definition finding into an explicit
diagnostic-only UR10e adapted terminal setup gate. It does not change the
strict paper-equivalent setup gate, and it does not create a path, trajectory,
or hardware-readiness claim.

No real UR10e motion, TCP writes, payload writes, URCap writes, ROS config
writes, or OnRobot configuration changes were performed.

## Gate

Added to `configs/ur10e_adapted_acceptance.yaml`:

```text
ur10e_adapted_terminal_setup_diagnostic_gate:
  max_terminal_tangential_error_m: 0.004
  max_terminal_orientation_error_rad: 0.08
  max_terminal_force_error_N: 0.25
  min_target_contact_count: 1
  claim_scope: ur10e_adapted_terminal_setup_diagnostic_only
```

The thresholds are rounded above the v56 strict-best terminal candidate:

- x/y error: `0.0030075787462736734 m`
- orientation error: `0.07240603326354965 rad`
- force error: `0.005097551486581864 N`

## Evaluation

Run:

- `runs/terminal_setup_gate_eval/20260524T143019`

Command:

```bash
scripts/evaluate_terminal_setup_gate.py \
  --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml \
  --acceptance-config configs/ur10e_adapted_acceptance.yaml
```

Result:

- source candidates: `513`
- diagnostic terminal setup passes: `1`
- passed seed labels: `initial`
- best force error: `0.005097546556703136 N`
- best x/y error: `0.0030075762251302427 m`
- best orientation error: `0.07240605683117833 rad`
- best target contact count: `1`
- best max gate ratio: `0.9050757103897291`

## Interpretation

The v57 diagnostic gate is intentionally narrow. It is a bookkeeping label for
the best target-contact terminal state under the current adapted UR10e
simulation, after v56 showed that the strict setup gate is mutually in tension.

It must not be used as evidence for:

- paper-equivalent full staged feasibility
- path feasibility
- trajectory feasibility
- real-robot safety or hardware readiness

## Conclusion

The project now has three distinct setup labels:

- strict paper-equivalent setup: still failed
- v38 relaxed trajectory-after-setup budget: applies to the slowed E1-E4
  trajectory matrix only
- v57 diagnostic terminal setup: one terminal candidate passes under relaxed
  diagnostic thresholds, with no path or trajectory claim

The next controller step should only proceed after choosing which adapted
setup label the controller is meant to satisfy.

## Verification

- `scripts/run_tests.sh tests/test_terminal_setup_gate.py` -> `2 passed`
- `scripts/run_tests.sh` -> `92 passed in 2.41s`
- `git diff --check` passed
