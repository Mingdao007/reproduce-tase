# Positive Stitched Sensitivity Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stitched_sensitivity/20260524T193845`

- Scenario count: `5`
- Matrix stitched pass count: `37 / 40`
- All-pass scenarios: `2 / 5`
- Failing scenarios: `qdot012_stage_a18s, paper_time_scale_0p0075, orientation_gate_0p119`

| scenario | pass count | Stage A pass count | max pass delta mm | max Stage A terminal orientation | max Stage B orientation | max Stage B qdot sat | failing deltas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `nominal_v72` | `8/8` | `8/8` | `1.0` | `0.11948560786547915` | `0.1199788204275829` | `0.006` | `none` |
| `stage_a_14p5s` | `8/8` | `8/8` | `1.0` | `0.11948560786547915` | `0.1199788204275829` | `0.006` | `none` |
| `qdot012_stage_a18s` | `7/8` | `7/8` | `1.0` | `0.11948560786547915` | `0.11997895388586574` | `0.009` | `delta_p0p200mm` |
| `paper_time_scale_0p0075` | `7/8` | `8/8` | `0.75` | `0.11948560786547915` | `0.12020305872871904` | `0.999` | `delta_p1p000mm` |
| `orientation_gate_0p119` | `7/8` | `7/8` | `0.75` | `0.11948560786547915` | `0.1199788204275829` | `0.006` | `delta_p1p000mm` |

Failure Detail:

| scenario | delta mm | stitched | Stage A | Stage B pass | Stage A terminal orientation | Stage B max orientation | failed Stage A criteria | failed Stage B rows |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| `qdot012_stage_a18s` | `0.2` | `False` | `False` | `4/4` | `0.08931515980019815` | `0.08955538795286133` | `final_tracking_error_norm_rad` | `none` |
| `paper_time_scale_0p0075` | `1.0` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.12020305872871904` | `none` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `orientation_gate_0p119` | `1.0` | `False` | `False` | `0/4` | `0.11948560786547915` | `0.1199788204275829` | `terminal_gate:terminal_force_normal_orientation_error_rad` | `e1-cycloid:max_orientation_error_rad;e2-figure-eight:max_orientation_error_rad;e3-circle:max_orientation_error_rad;e4-cardioid:max_orientation_error_rad` |

Interpretation:

- Passing rows preserve the v72 positive stitched diagnostic result only under the listed perturbation.
- Failing rows bound the v72 recovery and prevent a robustness or paper-equivalent claim.
- This audit remains simulation-only and does not authorize hardware motion or configuration changes.
