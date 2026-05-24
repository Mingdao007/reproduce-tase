# Stage A Diagnostic Target Handoff Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v59-diagnostic-target-handoff`

## Scope

This iteration evaluates whether the v58 selected diagnostic terminal setup
target can hand off directly to the Stage B trajectory controller. It starts
from the selected terminal q and does not implement a Stage A path controller
to reach that q.

No real UR10e motion, TCP writes, payload writes, URCap writes, ROS config
writes, or OnRobot configuration changes were performed.

## Method

Added:

- `src/tase_repro/stage_a_target_handoff.py`
- `scripts/evaluate_stage_a_target_handoff.py`

The evaluator reads:

- `configs/ur10e_adapted_stage_a_target.yaml`
- `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`

It runs E1-E4 from the selected diagnostic terminal q and evaluates the
trajectory gate using force/contact recomputed only for the intended
`contact_plane` / `contact_tip` target pair.

## Run

- Run: `runs/stage_a_target_handoff_eval/20260524T144654`
- Command:

```bash
scripts/evaluate_stage_a_target_handoff.py
```

## Result

- handoff passes: `0 / 4`
- selected label: `ur10e_adapted_terminal_setup_diagnostic`
- qdot limit: `0.15 rad/s`
- claim scope: diagnostic target handoff only

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00044731831825411294` | `1.8982311960984542e-06` | `0.07241136531652666` | `1.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.010356910150789211` | `1.0830060958997752e-05` | `0.07798915922321072` | `1.0` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0005744523497747523` | `1.8786677849133177e-06` | `0.07241136552901739` | `1.0` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00034897455877974437` | `1.9563864049776486e-06` | `0.07242466860766499` | `1.0` | `1.0` |

## Interpretation

The selected diagnostic terminal target is compatible with target-pair contact
and the relaxed diagnostic orientation envelope during the short E1-E4 handoff
runs. It is not enough to make a trajectory claim, because every row saturates
qdot for the full run and fails `tail_max_qdot_utilization`.

This confirms the next controller work should be qdot-budget aware. It should
not only reuse the selected terminal q and call that a trajectory solution.

## Limits

- not a Stage A path controller
- not path feasibility
- not trajectory feasibility
- not paper-equivalent feasibility
- not hardware-ready

## Next Step

Implement a qdot-aware Stage A/Stage B prototype against the selected
diagnostic terminal target, or explicitly change the trajectory timing/gate
before claiming any trajectory feasibility.

## Verification

- `scripts/run_tests.sh tests/test_stage_a_target_handoff.py` -> `3 passed`
- `python3 -m py_compile src/tase_repro/stage_a_target_handoff.py scripts/evaluate_stage_a_target_handoff.py`
- `scripts/run_tests.sh` -> `96 passed in 2.40s`
- `git diff --check` passed
