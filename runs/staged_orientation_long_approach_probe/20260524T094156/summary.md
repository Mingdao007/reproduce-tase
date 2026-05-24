# Long Stage A Approach Probe Summary

Run root: `runs/staged_orientation_long_approach_probe/20260524T094156`

## Result

- Cases: `6`
- Approach terminal-orientation passes: `3`
- Approach terminal-budget passes: `0`
- Approach ordinary-feasibility passes: `0`
- Trajectory-after-approach passes: `0`
- Full staged-feasibility passes: `0`

| case | duration s | kp | terminal err rad | first <=0.03 s | qdot sat | tail qdot util | drift m | angular slack rad/s | terminal budget | traj pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_kp0p50_4s` | 4.0 | 0.50 | 0.0275192 | 3.778 | 0.6145 | 1 | 0.00501401 | 0.00317123 | `False` | `False` |
| `weighted_kp0p35_6s` | 6.0 | 0.35 | 0.0262618 | 5.470 | 0.6127 | 1 | 0.00514998 | 0.00287884 | `False` | `False` |
| `weighted_kp0p25_8s` | 8.0 | 0.25 | 0.0290636 | 7.810 | 0.5827 | 1 | 0.00480077 | 0.00254512 | `False` | `False` |
| `weighted_kp0p15_12s` | 12.0 | 0.15 | 0.0348579 | None | 0.5285 | 1 | 0.00410258 | 0.00198321 | `False` | `False` |
| `weighted_kp0p10_18s` | 18.0 | 0.10 | 0.036555 | None | 0.5261 | 1 | 0.00390159 | 0.00196148 | `False` | `False` |
| `linear_primary_kp0p50_18s` | 18.0 | 0.50 | 0.0741633 | None | 0.9143 | 1 | 8.08395e-06 | 0.0376932 | `False` | `False` |

## Interpretation

Extending Stage A with lower gains does not recover a clean approach budget. The low-gain weighted cases can eventually reach the terminal orientation gate, but qdot saturation remains above the 0.01 budget and planar drift remains above the 0.002 m approach threshold. The long linear-primary reference preserves planar drift, but it still stalls above the terminal orientation gate.
