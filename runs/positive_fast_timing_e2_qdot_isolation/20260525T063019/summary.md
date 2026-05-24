# Positive Stage B E2 Margin Summary

Run root: `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019`

- Timing rows: `7`
- Fastest all-pass paper_time_scale: `0.0052`
- Qdot-only probe rows: `5`
- Qdot-only probe pass count: `0 / 5`

| paper_time_scale | E2 pass count | max recovered positive delta mm |
| ---: | ---: | ---: |
| `0.0075` | `0 / 1` | `None` |
| `0.007` | `0 / 1` | `None` |
| `0.0065` | `0 / 1` | `None` |
| `0.006` | `0 / 1` | `None` |
| `0.0055` | `0 / 1` | `None` |
| `0.0052` | `1 / 1` | `1.0` |
| `0.005` | `1 / 1` | `1.0` |

| delta mm | max passing paper_time_scale | E2 failed criteria at first scale | first-scale qdot sat | first-scale tail qdot | first-scale max orientation rad |
| ---: | ---: | --- | ---: | ---: | ---: |
| `1.0` | `0.0052` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.999` | `1.0` | `0.12020305872871904` |

Qdot-only probe at `paper_time_scale = 0.0075`:

| qdot limit rad/s | pass | failed criteria | qdot sat | tail qdot | max orientation rad |
| ---: | --- | --- | ---: | ---: | ---: |
| `0.15` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.999` | `1.0` | `0.12020305872871904` |
| `0.18` | `False` | `max_orientation_error_rad` | `0.005` | `0.7467597744996136` | `0.1202243264055315` |
| `0.2` | `False` | `max_orientation_error_rad` | `0.001` | `0.6698534796410496` | `0.12022431830306979` |
| `0.25` | `False` | `max_orientation_error_rad` | `0.001` | `0.5371183912531953` | `0.12022428616393772` |
| `0.3` | `False` | `max_orientation_error_rad` | `0.0` | `0.44759865937766274` | `0.12022428616393772` |

Interpretation:

- Slowing E2 to `paper_time_scale = 0.0052` recovers all tested positive deltas under the v70 run-local `0.12 rad` gate.
- Raising qdot limit alone at `paper_time_scale = 0.0075` does not recover the hardest tested `+1.0 mm` case because max orientation error remains above `0.12 rad`.
- This is diagnostic-label simulation evidence only, not a canonical config change, robustness proof, paper-equivalent claim, or hardware readiness result.
