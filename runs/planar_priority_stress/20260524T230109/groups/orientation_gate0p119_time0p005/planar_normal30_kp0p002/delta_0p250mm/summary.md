# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/planar_priority_stress/20260524T230109/groups/orientation_gate0p119_time0p005/planar_normal30_kp0p002/delta_0p250mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.11996410618909473`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.01575906280310234` | `2.611741937140073e-06` | `0.09119881037545309` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.08225749906102553` | `5.669870041049988e-06` | `0.0914607343920079` | `0.001` | `1.0` |
| `e3-circle` | `True` | `none` | `0.015742068656448935` | `2.61102041407992e-06` | `0.09119881037701634` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.015783057156883627` | `2.6129898684874517e-06` | `0.09119881037545309` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
