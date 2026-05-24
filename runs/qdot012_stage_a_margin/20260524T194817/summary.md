# Qdot012 Stage A Duration Margin Summary

Run root: `/home/andy/reproduce-tase/runs/qdot012_stage_a_margin/20260524T194817`

- Case count: `7`
- Stitched pass count: `3 / 7`
- Last failing Stage A duration s: `18.03`
- First passing Stage A duration s: `18.035`
- All Stage B rows pass in every case: `True`

| Stage A duration s | stitched | Stage A | Stage B pass | Stage A max qdot | final tracking error | failed Stage A criteria | failed Stage B rows |
| ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| `18.0` | `False` | `False` | `4/4` | `0.12` | `2.8323382178791726e-05` | `final_tracking_error_norm_rad` | `none` |
| `18.01` | `False` | `False` | `4/4` | `0.12` | `1.8979504676181077e-05` | `final_tracking_error_norm_rad` | `none` |
| `18.02` | `False` | `False` | `4/4` | `0.12` | `9.645997736770176e-06` | `final_tracking_error_norm_rad` | `none` |
| `18.03` | `False` | `False` | `4/4` | `0.12` | `3.2284410533080015e-07` | `final_tracking_error_norm_rad` | `none` |
| `18.035` | `True` | `True` | `4/4` | `0.1199690367457867` | `0.0` | `none` | `none` |
| `18.04` | `True` | `True` | `4/4` | `0.11993578590413784` | `0.0` | `none` | `none` |
| `18.05` | `True` | `True` | `4/4` | `0.11986933948543452` | `0.0` | `none` | `none` |

Interpretation:

- The v73 `qdot012_stage_a18s` `+0.2 mm` failure is a narrow Stage A duration margin, not a Stage B handoff failure.
- Extending Stage A from `18.03 s` to `18.035 s` recovers the failing cell in this diagnostic setup.
- This does not change the faster-timing or tighter-orientation sensitivity limits from v73.
