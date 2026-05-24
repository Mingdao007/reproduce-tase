# Weighted Timing Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_timing_recovery/20260524T231454`

- Full-delta scenario count: `5`
- Full-delta stitched pass count: `23 / 40`
- Full-delta all-pass scenarios: `weighted_kp0_normal1, weighted_kp0_normal30`
- Timing sweep stitched pass count: `10 / 10`
- Timing sweep max passing scale: `0.01`
- Timing sweep min failing scale: `None`

## Full Positive-Delta Stress

| scenario | priority | normal weight | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot | max force err |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `linear_kp0_normal1` | `linear_primary` | `1.0` | `7/8` | `0.75` | `0.12020305872871904` | `0.999` | `1.0` | `0.006603888075066666` |
| `planar_normal30_kp0p001` | `planar_primary` | `30.0` | `0/8` | `None` | `0.11983992753823672` | `0.143` | `1.0` | `0.20098660314203312` |
| `planar_normal30_kp0p002` | `planar_primary` | `30.0` | `0/8` | `None` | `0.11972166555008389` | `0.234` | `1.0` | `0.275874931458737` |
| `weighted_kp0_normal1` | `weighted` | `1.0` | `8/8` | `1.0` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0009911909058976187` |
| `weighted_kp0_normal30` | `weighted` | `30.0` | `8/8` | `1.0` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0009911909058976187` |

## Timing Sweep

| paper_time_scale | stitched | Stage B pass | E2 orientation | E2 qdot sat | E2 tail qdot | E2 force err | failed rows |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0.005` | `True` | `4/4` | `0.11952603093174877` | `0.0` | `0.41260146469178177` | `0.0006455387847314942` | `none` |
| `0.006` | `True` | `4/4` | `0.11953415992450067` | `0.0` | `0.49681833572454004` | `0.0007653276857842162` | `none` |
| `0.0065` | `True` | `4/4` | `0.11953815417606216` | `0.0` | `0.5076053725908033` | `0.0007381564171879917` | `none` |
| `0.007` | `True` | `4/4` | `0.11954220571930371` | `0.0` | `0.5093691895088811` | `0.0007640004154607327` | `none` |
| `0.0075` | `True` | `4/4` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008094383419582085` | `none` |
| `0.008` | `True` | `4/4` | `0.11955021599931354` | `0.0` | `0.5210348702552344` | `0.0007546838609746364` | `none` |
| `0.0085` | `True` | `4/4` | `0.1195543287381386` | `0.0` | `0.5248884090370669` | `0.0007687977162068371` | `none` |
| `0.009` | `True` | `4/4` | `0.11955829106493644` | `0.0` | `0.5278218979712962` | `0.0007908673750422501` | `none` |
| `0.0095` | `True` | `4/4` | `0.11956229681499174` | `0.0` | `0.5243799604781224` | `0.0007834322084013489` | `none` |
| `0.01` | `True` | `4/4` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0007810274125596095` | `none` |

## Failed Case Detail

| group | case | stitched | Stage A | Stage B pass | E2 orientation | E2 qdot sat | failed rows |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `full_delta` | `linear_kp0_normal1:time_0p0075:delta1p000mm` | `False` | `True` | `3/4` | `0.12020305872871904` | `0.999` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p050mm` | `False` | `True` | `3/4` | `0.08427301402372706` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p100mm` | `False` | `True` | `3/4` | `0.08610724680672958` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p150mm` | `False` | `True` | `3/4` | `0.08794836711464664` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p200mm` | `False` | `True` | `3/4` | `0.08979608301951979` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p250mm` | `False` | `True` | `3/4` | `0.09165005008791383` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p500mm` | `False` | `True` | `3/4` | `0.10099571817848935` | `0.041` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta0p750mm` | `False` | `True` | `3/4` | `0.11041305737921629` | `0.143` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p001:time_0p0075:delta1p000mm` | `False` | `True` | `3/4` | `0.11983992753823672` | `0.072` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p050mm` | `False` | `True` | `3/4` | `0.08421322077190706` | `0.214` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p100mm` | `False` | `True` | `3/4` | `0.0860442766288064` | `0.222` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p150mm` | `False` | `True` | `3/4` | `0.08788223085242461` | `0.227` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p200mm` | `False` | `True` | `3/4` | `0.0897266919070735` | `0.231` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p250mm` | `False` | `True` | `3/4` | `0.09157731566302724` | `0.234` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p500mm` | `False` | `True` | `3/4` | `0.10090941314447023` | `0.213` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta0p750mm` | `False` | `True` | `3/4` | `0.11032227907958207` | `0.13` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `full_delta` | `planar_normal30_kp0p002:time_0p0075:delta1p000mm` | `False` | `True` | `3/4` | `0.11972166555008389` | `0.001` | `e2-figure-eight:tail_mean_abs_force_error_N` |

Interpretation:

- The weighted zero-angular-command candidate is tested as a faster-timing recovery, not as a new canonical controller default.
- Full-delta rows compare it against the v72 linear-primary baseline and the v80 planar-primary candidates on the same `0.0075` timing face.
- The timing sweep localizes the `+1.0 mm` faster-timing boundary for the weighted candidate.
- This remains diagnostic-label simulation evidence only.
