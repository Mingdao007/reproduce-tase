# Approach Qdot Budget Probe Summary

Run root: `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305`

## Result

- Cases: `7`
- Approach terminal-orientation passes: `4`
- Approach terminal-budget passes: `0`
- Approach ordinary-feasibility passes: `0`
- Trajectory-after-approach passes: `3`
- Full staged-feasibility passes: `0`

| case | approach cap | terminal err rad | first <=0.03 s | approach qdot sat | max qdot | drift m | terminal budget | traj pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_a0p15_t0p15_kp2_4s` | 0.15 | 0.0020238 | 0.912 | 0.961 | 0.15 | 0.00973854 | `False` | `True` |
| `weighted_a0p25_t0p15_kp2_4s` | 0.25 | 0.00202907 | 0.926 | 1 | 0.25 | 0.00834798 | `False` | `True` |
| `weighted_a0p35_t0p15_kp2_4s` | 0.35 | 0.0020275 | 0.926 | 0.932 | 0.35 | 0.00834736 | `False` | `True` |
| `weighted_a0p50_t0p15_kp2_4s` | 0.50 | 0.00201843 | 0.926 | 0.908 | 0.5 | 0.00834505 | `False` | `False` |
| `linear_primary_a0p25_t0p15_kp2_4s` | 0.25 | 0.0741399 | None | 1 | 0.25 | 1.10131e-05 | `False` | `False` |
| `linear_primary_a0p35_t0p15_kp2_4s` | 0.35 | 0.0740139 | None | 0.924 | 0.35 | 1.58854e-05 | `False` | `False` |
| `linear_primary_a0p50_t0p15_kp2_4s` | 0.50 | 0.0738197 | None | 0.908 | 0.5 | 3.03535e-05 | `False` | `False` |

## Interpretation

Relaxing only the Stage A qdot cap shows two different failure modes. Weighted approaches align quickly, but planar drift remains above the approach budget and high relaxed caps can lose the following trajectory pass. Linear-primary approaches preserve planar drift but still do not reach the terminal orientation threshold under the tested durations and caps.
