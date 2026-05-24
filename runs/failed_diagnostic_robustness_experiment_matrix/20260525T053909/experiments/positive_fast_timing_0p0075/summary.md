# Positive Stitched Sensitivity Summary

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`

- Scenario count: `1`
- Matrix stitched pass count: `0 / 1`
- All-pass scenarios: `0 / 1`
- Failing scenarios: `paper_time_scale_0p0075`

| scenario | pass count | Stage A pass count | max pass delta mm | max Stage A terminal orientation | max Stage B orientation | max Stage B qdot sat | failing deltas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `paper_time_scale_0p0075` | `0/1` | `1/1` | `None` | `0.11948560786547915` | `0.12020305872871904` | `0.999` | `delta_p1p000mm` |

Failure Detail:

| scenario | delta mm | stitched | Stage A | Stage B pass | Stage A terminal orientation | Stage B max orientation | failed Stage A criteria | failed Stage B rows |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| `paper_time_scale_0p0075` | `1.0` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.12020305872871904` | `none` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |

Interpretation:

- Passing rows preserve the v72 positive stitched diagnostic result only under the listed perturbation.
- Failing rows bound the v72 recovery and prevent a robustness or paper-equivalent claim.
- This audit remains simulation-only and does not authorize hardware motion or configuration changes.
