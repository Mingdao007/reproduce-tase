# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005/cases/paper_time_scale_0p0125_reference_fail`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14332635022814824`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `2.9518821583960353e-05` | `1.8613838774080883e-08` | `0.0724113081316573` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.009659333060181977` | `1.6853621524790917e-06` | `0.0733173098115436` | `0.114` | `1.0` |
| `e3-circle` | `True` | `none` | `2.949644833472487e-05` | `7.726183911643321e-08` | `0.07241142422648127` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `2.9503036248672567e-05` | `1.861308857216415e-08` | `0.0724121639521683` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
