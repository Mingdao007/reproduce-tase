# Planar-Priority Stress Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109`

- Group count: `8`
- Total case count: `66`
- Total stitched pass count: `35 / 66`
- All groups pass all cases: `False`
- Failing groups: `timing_boundary_plus1mm, orientation_gate_boundary_plus1mm, timing_0p0075_gate0p11995, orientation_gate0p119_time0p005, timing_boundary_plus1mm, orientation_gate_boundary_plus1mm, timing_0p0075_gate0p11995, orientation_gate0p119_time0p005`

## Group Aggregates

| group | scenario | pass count | Stage A all pass | max orientation | max qdot sat | max tail qdot | max force err | boundary |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p001` | `7/9` | `True` | `0.11983992753823672` | `0.072` | `1.0` | `0.20098660314203312` | `max pass scale=0.0065, min fail scale=0.007` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001` | `3/8` | `False` | `0.11973133163816624` | `0.001` | `0.0010367427075651814` | `0.1223546677432889` | `min pass gate=0.1198, max fail gate=0.1197` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001` | `0/8` | `True` | `0.11983992753823672` | `0.143` | `1.0` | `0.20098660314203312` | `n/a` |
| `orientation_gate0p119_time0p005` | `planar_normal30_kp0p001` | `7/8` | `False` | `0.11973133163816624` | `0.001` | `0.0010837631758864566` | `0.1223546677432889` | `n/a` |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p002` | `7/9` | `True` | `0.11972166555008389` | `0.001` | `0.0012133347645829611` | `0.275874931458737` | `max pass scale=0.0065, min fail scale=0.007` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p002` | `4/8` | `False` | `0.11961552028823065` | `0.001` | `0.0007980873518407317` | `0.1902561439715911` | `min pass gate=0.1197, max fail gate=0.1196` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002` | `0/8` | `True` | `0.11972166555008389` | `0.234` | `1.0` | `0.275874931458737` | `n/a` |
| `orientation_gate0p119_time0p005` | `planar_normal30_kp0p002` | `7/8` | `False` | `0.11961552028823065` | `0.001` | `0.0009960728846485063` | `0.1902561439715911` | `n/a` |

## Failed Case Detail

| group | case | stitched | Stage A | Stage B pass | time scale | gate | delta mm | E2 orientation | E2 qdot sat | failed rows |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p001:time_0p007:delta1p000mm` | `False` | `True` | `3/4` | `0.007` | `0.11995` | `1.0` | `0.11982445784240647` | `0.013` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p001:time_0p0075:delta1p000mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `1.0` | `0.11983992753823672` | `0.072` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001:gate_0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.119` | `1.0` | `0.11973133163816624` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001:gate_0p11925:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.11925` | `1.0` | `0.11973133163816624` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001:gate_0p1195:delta1p000mm` | `False` | `True` | `3/4` | `0.005` | `0.1195` | `1.0` | `0.11973133163816624` | `0.001` | `e2-figure-eight:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001:gate_0p1196:delta1p000mm` | `False` | `True` | `3/4` | `0.005` | `0.1196` | `1.0` | `0.11973133163816624` | `0.001` | `e2-figure-eight:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p001:gate_0p1197:delta1p000mm` | `False` | `True` | `3/4` | `0.005` | `0.1197` | `1.0` | `0.11973133163816624` | `0.001` | `e2-figure-eight:max_orientation_error_rad` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p050mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.05` | `0.08427301402372706` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p100mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.1` | `0.08610724680672958` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p150mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.15` | `0.08794836711464664` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p200mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.2` | `0.08979608301951979` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p250mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.25` | `0.09165005008791383` | `0.003` | `e2-figure-eight:tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p500mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.5` | `0.10099571817848935` | `0.041` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta0p750mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.75` | `0.11041305737921629` | `0.143` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p001:timing_0p0075_gate0p11995:delta1p000mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `1.0` | `0.11983992753823672` | `0.072` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `orientation_gate0p119_time0p005` | `planar_normal30_kp0p001:orientation_gate0p119_time0p005:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.119` | `1.0` | `0.11973133163816624` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p002:time_0p007:delta1p000mm` | `False` | `True` | `3/4` | `0.007` | `0.11995` | `1.0` | `0.11970125387669314` | `0.001` | `e2-figure-eight:tail_mean_abs_force_error_N` |
| `timing_boundary_plus1mm` | `planar_normal30_kp0p002:time_0p0075:delta1p000mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `1.0` | `0.11972166555008389` | `0.001` | `e2-figure-eight:tail_mean_abs_force_error_N` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p002:gate_0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.119` | `1.0` | `0.11961552028823065` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p002:gate_0p11925:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.11925` | `1.0` | `0.11961552028823065` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p002:gate_0p1195:delta1p000mm` | `False` | `True` | `3/4` | `0.005` | `0.1195` | `1.0` | `0.11961552028823065` | `0.001` | `e2-figure-eight:max_orientation_error_rad` |
| `orientation_gate_boundary_plus1mm` | `planar_normal30_kp0p002:gate_0p1196:delta1p000mm` | `False` | `True` | `3/4` | `0.005` | `0.1196` | `1.0` | `0.11961552028823065` | `0.001` | `e2-figure-eight:max_orientation_error_rad` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p050mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.05` | `0.08421322077190706` | `0.214` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p100mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.1` | `0.0860442766288064` | `0.222` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p150mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.15` | `0.08788223085242461` | `0.227` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p200mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.2` | `0.0897266919070735` | `0.231` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p250mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.25` | `0.09157731566302724` | `0.234` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p500mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.5` | `0.10090941314447023` | `0.213` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta0p750mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `0.75` | `0.11032227907958207` | `0.13` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `timing_0p0075_gate0p11995` | `planar_normal30_kp0p002:timing_0p0075_gate0p11995:delta1p000mm` | `False` | `True` | `3/4` | `0.0075` | `0.11995` | `1.0` | `0.11972166555008389` | `0.001` | `e2-figure-eight:tail_mean_abs_force_error_N` |
| `orientation_gate0p119_time0p005` | `planar_normal30_kp0p002:orientation_gate0p119_time0p005:delta1p000mm` | `False` | `False` | `0/4` | `0.005` | `0.119` | `1.0` | `0.11961552028823065` | `0.001` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |

Interpretation:

- This stress audit reuses the v80 planar-primary Stage B candidates without changing canonical defaults.
- The timing boundary rows isolate whether planar priority moves the old v76 `+1.0 mm` faster-timing limit.
- The orientation-gate rows isolate whether planar priority moves the old v77 `+1.0 mm` tightened-gate limit.
- The full-delta stress rows test the old v73 failing scenario faces across all positive base-z deltas.
- This remains diagnostic-label simulation evidence, not strict paper-equivalent, robustness, contact calibration, or hardware readiness.
