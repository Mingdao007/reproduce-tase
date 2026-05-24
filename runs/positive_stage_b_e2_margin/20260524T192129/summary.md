# Positive Stage B E2 Margin Summary

Run root: `/home/andy/reproduce-tase/runs/positive_stage_b_e2_margin/20260524T192129`

- Timing rows: `32`
- Fastest all-pass paper_time_scale: `0.005`
- Qdot-only probe rows: `4`

| paper_time_scale | E2 pass count | max recovered positive delta mm |
| ---: | ---: | ---: |
| `0.01` | `0 / 8` | `None` |
| `0.0075` | `7 / 8` | `0.75` |
| `0.005` | `8 / 8` | `1.0` |
| `0.0025` | `8 / 8` | `1.0` |

| delta mm | max passing paper_time_scale | original E2 failed criteria at 0.01 | original qdot sat | original tail qdot | original max orientation rad |
| ---: | ---: | --- | ---: | ---: | ---: |
| `0.05` | `0.0075` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.51` | `1.0` | `0.08458026026618173` |
| `0.1` | `0.0075` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.525` | `1.0` | `0.08642296614707717` |
| `0.15` | `0.0075` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.541` | `1.0` | `0.08827285798416469` |
| `0.2` | `0.0075` | `tail_max_qdot_utilization` | `0.005` | `0.9879754823217709` | `0.09014617602004879` |
| `0.25` | `0.0075` | `tail_max_qdot_utilization` | `0.006` | `0.9999999999999998` | `0.09201059129093692` |
| `0.5` | `0.0075` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.685` | `1.0` | `0.10140420246203012` |
| `0.75` | `0.0075` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.825` | `1.0` | `0.11091835714279596` |
| `1.0` | `0.005` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.997` | `1.0` | `0.12043140848858806` |

Qdot-only probe at original `paper_time_scale = 0.01`:

| qdot limit rad/s | pass | failed criteria | qdot sat | tail qdot | max orientation rad |
| ---: | --- | --- | ---: | ---: | ---: |
| `0.15` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.997` | `1.0` | `0.12043140848858806` |
| `0.18` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization;max_orientation_error_rad` | `0.016` | `0.9851360920235176` | `0.12046981651469077` |
| `0.2` | `False` | `max_orientation_error_rad` | `0.01` | `0.974311748817342` | `0.12046964616379696` |
| `0.25` | `False` | `max_orientation_error_rad` | `0.001` | `0.7921364784960163` | `0.12046974135448098` |

Interpretation:

- Slowing E2 to `paper_time_scale = 0.005` recovers all tested positive deltas under the v70 run-local `0.12 rad` gate.
- Raising qdot limit alone at the original `paper_time_scale = 0.01` does not recover the hardest tested `+1.0 mm` case because max orientation error remains above `0.12 rad`.
- This is diagnostic-label simulation evidence only, not a canonical config change, robustness proof, paper-equivalent claim, or hardware readiness result.
