# Stage A Target Handoff Evaluation Summary

Run root: `/home/andy/reproduce-tase/runs/stage_a_target_handoff_eval/20260524T144654`

Scope: start directly from the v58 selected diagnostic terminal target and evaluate Stage B handoff.

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Handoff passes: `0 / 4`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00044731831825411294` | `1.8982311960984542e-06` | `0.07241136531652666` | `1.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.010356910150789211` | `1.0830060958997752e-05` | `0.07798915922321072` | `1.0` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.0005744523497747523` | `1.8786677849133177e-06` | `0.07241136552901739` | `1.0` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.00034897455877974437` | `1.9563864049776486e-06` | `0.07242466860766499` | `1.0` | `1.0` |

Interpretation:

- This is a handoff audit, not Stage A path feasibility.
- A failure here means the selected terminal target is not enough for a trajectory claim.
- A pass here would still require a separate Stage A path controller to reach the target.
