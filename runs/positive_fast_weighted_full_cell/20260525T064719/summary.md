# Positive Fast Weighted Full-Cell Summary

Run root: `runs/positive_fast_weighted_full_cell/20260525T064719`

- Scenario count: `3`
- Passing scenarios: `weighted_kp0_normal1, weighted_kp0_normal30`
- Weighted candidate recovered: `True`
- Original failed cell closed: `False`
- Best orientation scenario: `weighted_kp0_normal1`
- Minimum max Stage B orientation: `0.11954627160547111`

| scenario | priority | normal weight | stitched | Stage B pass | failed rows | max orientation | qdot sat | tail qdot | force err |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `linear_primary` | `1.0` | `False` | `3/4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `weighted_kp0_normal1` | `weighted` | `1.0` | `True` | `4/4` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |
| `weighted_kp0_normal30` | `weighted` | `30.0` | `True` | `4/4` | `none` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |

Interpretation:

- This probe keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15 rad/s`, and the run-local `0.12 rad` orientation gate fixed.
- Passing weighted rows are full E1-E4 diagnostic recovery candidates for the `+1.0 mm` fast-timing face.
- The original v99 failed cell is not marked closed because this audit does not accept a canonical controller change.
