# Approach Rate Cap Probe Summary

Run root: `runs/staged_orientation_rate_cap_probe/20260524T094752`

## Result

- Cases: `6`
- Command cap respected: `6`
- Approach terminal-orientation passes: `5`
- Approach terminal-budget passes: `0`
- Approach ordinary-feasibility passes: `0`
- Trajectory-after-approach passes: `3`
- Full staged-feasibility passes: `0`

| case | cap rad/s | duration s | max cmd rad/s | terminal err rad | first <=0.03 s | qdot sat | drift m | terminal budget | traj pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_uncapped_kp2_4s` | none | 4.0 | 0.349066 | 0.0020238 | 0.912 | 0.961 | 0.00973854 | `False` | `True` |
| `weighted_cap0p05_kp2_4s` | 0.050 | 4.0 | 0.05 | 0.00621702 | 2.988 | 0.546 | 0.0077846 | `False` | `False` |
| `weighted_cap0p03_kp2_6s` | 0.030 | 6.0 | 0.03 | 0.00805794 | 4.990 | 0.4637 | 0.0075547 | `False` | `False` |
| `weighted_cap0p02_kp2_10s` | 0.020 | 10.0 | 0.02 | 0.00280475 | 7.516 | 0.5072 | 0.0082407 | `False` | `True` |
| `weighted_cap0p01_kp2_20s` | 0.010 | 20.0 | 0.01 | 0.00254981 | 15.272 | 0.5001 | 0.00827622 | `False` | `True` |
| `linear_primary_cap0p03_kp2_12s` | 0.030 | 12.0 | 0.03 | 0.074162 | None | 0.7318 | 6.7497e-06 | `False` | `False` |

## Interpretation

The new cap is respected in every capped case, but it does not recover a feasible Stage A. Capping angular command lowers the requested angular rate, yet qdot saturation remains well above the budget and planar drift stays above the 0.002 m gate for weighted cases. The linear-primary capped reference preserves drift better, but still does not reach the terminal orientation threshold.
