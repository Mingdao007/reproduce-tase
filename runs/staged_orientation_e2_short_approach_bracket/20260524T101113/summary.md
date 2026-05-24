# E2 Short Approach Bracket Summary

Run root: `runs/staged_orientation_e2_short_approach_bracket/20260524T101113`

## Aggregate

- Case count: `5`
- Approach terminal orientation passes: `5`
- Approach ordinary feasibility passes: `0`
- Trajectory-after-approach passes: `0`
- Trajectory feasibility passes: `0`
- Full staged feasibility passes: `0`
- Passing cases: `none`

## Rows

| case | approach s | approach orient err | approach drift m | trajectory pass | failed criteria | traj orient err | traj qdot sat | tail qdot util |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `approach0p94` | `0.94` | `0.029326677012512806` | `0.005511250096345505` | `False` | qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s | `0.04359451698383457` | `0.94175` | `1.0` |
| `approach1p00` | `1.0` | `0.026344676181529823` | `0.005757642179203222` | `False` | qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad;max_angular_velocity_slack_rad_s | `0.04142406189804967` | `0.94925` | `1.0` |
| `approach1p20` | `1.2` | `0.01856973738776605` | `0.006423414172320667` | `False` | qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad | `0.035706552138982606` | `0.9555` | `1.0` |
| `approach2p00` | `2.0` | `0.0056419034973640815` | `0.00785568116254086` | `False` | qdot_saturation_fraction;tail_max_qdot_utilization | `0.024082964025574225` | `0.99775` | `1.0` |
| `approach4p00` | `4.0` | `0.0020290714973557108` | `0.008347977658392892` | `False` | qdot_saturation_fraction;tail_max_qdot_utilization | `0.020294558071100602` | `0.9935` | `1.0` |

Raw `.npz` files are intentionally ignored by repository policy.
