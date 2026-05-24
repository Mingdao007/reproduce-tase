# Staged Approach Bracket Summary

Run root: `runs/staged_orientation_approach_bracket/20260524T093536`

## Result

- Cases: `7`
- Approach terminal-orientation passes: `5`
- Approach full-feasibility passes: `0`
- Trajectory-after-approach passes: `3`
- Full staged-feasibility passes: `0`

| case | terminal err rad | first <=0.03 s | approach qdot sat | drift m | contact frac | angular slack rad/s | approach pass | trajectory pass | full pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `weighted_kp0p5_planar1_ang1` | 0.0275192 | 3.778 | 0.6145 | 0.00501401 | 1 | 0.00317123 | `False` | `False` | `False` |
| `weighted_kp1p0_planar1_ang1` | 0.00706716 | 1.862 | 0.9995 | 0.00765065 | 1 | 0.00538346 | `False` | `True` | `False` |
| `weighted_kp2p0_planar1_ang1` | 0.0020238 | 0.912 | 0.961 | 0.00973854 | 1 | 0.0608503 | `False` | `True` | `False` |
| `weighted_kp2p0_planar10_ang1` | 0.0149423 | 1.258 | 1 | 0.00658333 | 1 | 0.138029 | `False` | `False` | `False` |
| `weighted_kp2p0_planar100_ang1` | 0.0484506 | None | 1 | 0.00246083 | 1 | 0.158078 | `False` | `False` | `False` |
| `weighted_kp2p0_planar1_ang10` | 0.000261202 | 0.882 | 0.8875 | 0.0125303 | 0.9615 | 0.00915376 | `False` | `True` | `False` |
| `linear_primary_kp2p0_planar1_ang1` | 0.0741477 | None | 1 | 9.5434e-06 | 1 | 0.16336 | `False` | `False` | `False` |

## Interpretation

The compact bracket did not find a Stage A setting that satisfies the ordinary approach feasibility gate. Lower orientation gains reduce angular slack, but they either leave too much saturation/force error or do not make the following trajectory pass. Raising planar slack cost trades drift for worse angular slack and can miss terminal alignment. The linear-primary approach preserves planar position but stalls above the tilted-normal threshold, so the trajectory-after-approach condition fails.
