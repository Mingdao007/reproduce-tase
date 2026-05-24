# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909/cases/delta_p0p100mm/stitched_15p0s`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `True`
- Stage B handoff passes: `3 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.14206784149212412`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `3.361322499492836e-05` | `2.778624093569611e-09` | `0.0856534397507393` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.01067888435259038` | `1.8906596481947406e-06` | `0.08642296614707717` | `0.525` | `1.0` |
| `e3-circle` | `True` | `none` | `3.360461716182428e-05` | `6.0059519952505e-08` | `0.08565344091460507` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `3.360717967467064e-05` | `2.7783519642929355e-09` | `0.08565402631525638` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
