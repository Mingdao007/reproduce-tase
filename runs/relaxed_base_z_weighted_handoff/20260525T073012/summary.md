# Relaxed Base-Z Weighted Handoff Summary

Run root: `runs/relaxed_base_z_weighted_handoff/20260525T073012`

- Case count: `6`
- Tested Stage A durations: `15.0, 16.0`
- Passing cases: `4`
- Weighted candidate recovered any duration: `True`
- Weighted candidate recovered all durations: `True`
- Original failed cell closed: `False`
- Best orientation case: `weighted_kp0_normal1 @ 15.0 s`
- Minimum max Stage B orientation: `0.11956645203696047`

| duration | scenario | priority | normal weight | stitched | Stage B pass | failed rows | max orientation | qdot sat | tail qdot | force err |
| ---: | --- | --- | ---: | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `15.0` | `linear_kp0_normal1` | `linear_primary` | `1.0` | `False` | `3/4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12043140848858806` | `0.997` | `1.0` | `0.014411641468066758` |
| `15.0` | `weighted_kp0_normal1` | `weighted` | `1.0` | `True` | `4/4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `15.0` | `weighted_kp0_normal30` | `weighted` | `30.0` | `True` | `4/4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `16.0` | `linear_kp0_normal1` | `linear_primary` | `1.0` | `False` | `3/4` | `e2-figure-eight:qdot_saturation_fraction,tail_max_qdot_utilization,max_orientation_error_rad` | `0.12043140848858806` | `0.997` | `1.0` | `0.014411641468066758` |
| `16.0` | `weighted_kp0_normal1` | `weighted` | `1.0` | `True` | `4/4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `16.0` | `weighted_kp0_normal30` | `weighted` | `30.0` | `True` | `4/4` | `none` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |

Interpretation:

- This probe keeps the v70 run-local `0.12 rad` orientation gate explicit and non-canonical.
- Passing weighted rows are diagnostic Stage B handoff candidates for the relaxed `base_z_plus1mm` path.
- The original v99 `base_z_plus1mm` failed cell is not marked closed because this audit does not accept the relaxed gate or weighted priority as canonical.
