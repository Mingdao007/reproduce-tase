# Stage B Priority Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/stage_b_priority_recovery/20260524T224404`

- Scenario count: `7`
- Stitched pass count: `2 / 7`
- Passing scenarios: `planar_normal30_kp0p001, planar_normal30_kp0p002`
- Stage A passed every scenario: `True`

| scenario | priority | normal weight | orientation_kp | posture weight | stitched | Stage B pass | max orientation | max qdot sat | max tail qdot | max force err | failed rows |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `linear_kp0` | `linear_primary` | `1.0` | `0.0` | `0.0` | `False` | `3/4` | `0.1199788204275829` | `0.006` | `0.0014580486861575888` | `0.0004859525136908127` | `e2-figure-eight:max_orientation_error_rad` |
| `linear_kp0p003` | `linear_primary` | `1.0` | `0.003` | `0.0` | `False` | `3/4` | `0.11994467909936898` | `1.0` | `1.0` | `0.009642392425932473` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization` |
| `linear_kp0p003_posture0p001` | `linear_primary` | `1.0` | `0.003` | `0.001` | `False` | `3/4` | `0.11997869470710999` | `0.0` | `0.002951372343394818` | `0.0004862322920638773` | `e2-figure-eight:max_orientation_error_rad` |
| `planar_normal10_kp0p001` | `planar_primary` | `10.0` | `0.001` | `0.0` | `False` | `3/4` | `0.11948537939100295` | `0.0` | `0.0005752160515418898` | `0.3544639543616428` | `e2-figure-eight:tail_mean_abs_force_error_N` |
| `planar_normal30_kp0p001` | `planar_primary` | `30.0` | `0.001` | `0.0` | `True` | `4/4` | `0.11973133163816624` | `0.001` | `0.0010367427075651814` | `0.1223546677432889` | `none` |
| `planar_normal30_kp0p002` | `planar_primary` | `30.0` | `0.002` | `0.0` | `True` | `4/4` | `0.11961552028823065` | `0.001` | `0.0007980873518407317` | `0.1902561439715911` | `none` |
| `planar_normal100_kp0p001` | `planar_primary` | `100.0` | `0.001` | `0.0` | `False` | `3/4` | `0.11995127502040462` | `0.188` | `1.0` | `0.009768843872853603` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` |

Interpretation:

- Linear-primary orientation feedback still trades orientation correction against qdot saturation, and handoff-posture regularization preserves qdot by giving up the orientation correction.
- Planar-primary priority with too little normal secondary weighting gives up force tracking.
- Planar-primary priority with normal-axis weight `30` recovers the full E1-E4 `+1.0 mm` tightened-gate diagnostic row at the tested `0.11995 rad` gate.
- This is a targeted priority-formulation recovery, not a robustness proof or hardware-ready claim.
