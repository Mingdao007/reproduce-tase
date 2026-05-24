# Qdot-Aware Diagnostic Handoff Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v60-qdot-aware-diagnostic-handoff`

## Scope

This iteration evaluates a qdot-aware diagnostic handoff prototype from the
v58 selected terminal target. It starts directly from the selected q and does
not implement a Stage A path controller.

No real UR10e motion, TCP writes, payload writes, URCap writes, ROS config
writes, or OnRobot configuration changes were performed.

## Prototype

The v59 handoff failed all E1-E4 rows because qdot saturation stayed active.
The v60 prototype changes only the diagnostic handoff policy:

- `paper_time_scale = 0.01`
- `force_gain = 1e-4`
- `orientation_kp = 0.0`
- `qdot_limit = 0.15 rad/s`

Interpretation:

- `orientation_kp = 0.0` holds the already-accepted diagnostic orientation
  envelope instead of spending qdot budget on additional force-normal
  convergence.
- `paper_time_scale = 0.01` is an explicit slowed-trajectory diagnostic
  timing. It is not a paper-equivalent trajectory timing claim.
- `force_gain = 1e-4` reduces normal-force correction aggressiveness while
  keeping target-pair force error inside the diagnostic force budget.

## Run

- Run: `runs/stage_a_target_handoff_eval/20260524T145433`
- Command:

```bash
scripts/evaluate_stage_a_target_handoff.py \
  --orientation-kp 0.0 \
  --paper-time-scale 0.01 \
  --force-gain 1e-4
```

## Result

- handoff passes: `4 / 4`
- selected label: `ur10e_adapted_terminal_setup_diagnostic`
- qdot saturation fraction: `0.0` for all rows
- target contact fraction: `1.0` for all rows

| trajectory | pass | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | tail qdot utilization |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `2.9518820398761747e-05` | `1.861383876553019e-08` | `0.07241130795799401` | `0.0` | `0.0001944004185648214` |
| `e2-figure-eight` | `True` | `0.003461025015189971` | `1.2123675244811085e-06` | `0.07314538284753326` | `0.0` | `0.0020943118909209214` |
| `e3-circle` | `True` | `2.950975921846677e-05` | `6.28103669350004e-08` | `0.07241138231384438` | `0.0` | `0.0007581388650151451` |
| `e4-cardioid` | `True` | `2.9512246949807698e-05` | `1.8613358680752423e-08` | `0.07241185573280741` | `0.0` | `0.00019740180668604472` |

## Claim Boundary

This can be recorded as:

```text
ur10e_qdot_aware_diagnostic_handoff:
  pass count = 4 / 4
  starts from selected diagnostic terminal q = true
  target-pair contact accounting = true
  path feasibility = false
  strict trajectory feasibility = false
  paper-equivalent feasibility = false
  hardware readiness = false
```

It must not be relabeled as a full Stage A/Stage B solution, because the run
does not show how to reach the selected terminal target from an ordinary
initial state.

## Next Step

Implement a qdot-aware Stage A path to the selected diagnostic terminal target,
or keep this result labeled as direct-target handoff evidence only.

## Verification

- `scripts/run_tests.sh tests/test_stage_a_target_handoff.py` -> `3 passed`
- `python3 -m py_compile scripts/evaluate_stage_a_target_handoff.py src/tase_repro/stage_a_target_handoff.py`
- `scripts/run_tests.sh` -> `96 passed in 2.43s`
- `git diff --check` passed
