# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/timing_0p0075_gate0p11995/planar_normal30_kp0p002/delta_0p100mm`

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
| `e1-cycloid` | `True` | `none` | `0.012395895946118719` | `2.3325278306249244e-06` | `0.0856522436299176` | `0.0` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction;tail_max_qdot_utilization` | `0.12305155955167296` | `6.732084053191039e-06` | `0.0860442766288064` | `0.222` | `1.0` |
| `e3-circle` | `True` | `none` | `0.012363441628952265` | `2.331022732517737e-06` | `0.0856522436326047` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.012441797305755183` | `2.335240025873322e-06` | `0.0856522436299176` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
