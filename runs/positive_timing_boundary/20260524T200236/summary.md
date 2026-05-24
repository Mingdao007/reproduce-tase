# Positive Timing Boundary Summary

Run root: `/home/andy/reproduce-tase/runs/positive_timing_boundary/20260524T200236`

- Case count: `9`
- Stitched pass count: `2 / 9`
- Max passing paper_time_scale: `0.0052`
- Min failing paper_time_scale: `0.0054`
- Stage A passed every case: `True`

| paper_time_scale | stitched | Stage B pass | E2 pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 failed criteria |
| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `0.005` | `True` | `4/4` | `True` | `0.1199788204275829` | `0.006` | `0.0014580486861575888` | `none` |
| `0.0052` | `True` | `4/4` | `True` | `0.11999846384112321` | `0.006` | `0.0015159989338741078` | `none` |
| `0.0054` | `False` | `3/4` | `False` | `0.12001811086329595` | `0.006` | `0.0015739339697212471` | `max_orientation_error_rad` |
| `0.0056` | `False` | `3/4` | `False` | `0.12003776159897517` | `0.006` | `0.0016318411885509457` | `max_orientation_error_rad` |
| `0.0058` | `False` | `3/4` | `False` | `0.12005741611102583` | `0.006` | `0.001840488196324605` | `max_orientation_error_rad` |
| `0.006` | `False` | `3/4` | `False` | `0.12007703866232994` | `0.007` | `0.001750886518560959` | `max_orientation_error_rad` |
| `0.0065` | `False` | `3/4` | `False` | `0.1201260838562` | `0.008` | `0.001898776739473921` | `max_orientation_error_rad` |
| `0.007` | `False` | `3/4` | `False` | `0.12015423656433318` | `0.999` | `1.0` | `qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `0.0075` | `False` | `3/4` | `False` | `0.12020305872871904` | `0.999` | `1.0` | `qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |

Interpretation:

- The `+1.0 mm` timing boundary is primarily an E2 orientation boundary immediately above `paper_time_scale = 0.0052`.
- At larger timing scales, E2 also accumulates qdot saturation and tail qdot utilization failures.
- This does not change the qdot012 recovery from v75 or the tightened-orientation sensitivity limit from v73.
