# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/full_matrix/time0p01_gate0p11995/weighted_kp0_normal1/delta_1p000mm`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `True`
- Stage A gate pass: `True`
- Stage B handoff passes: `4 / 4`
- Stage A duration: `15.0`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.10018584837167505`
- Stage A qdot saturation fraction: `0.0`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | `none` | `0.0008419470004960328` | `3.0694440330525453e-07` | `0.11948583687393066` | `0.0` | `1.0` |
| `e2-figure-eight` | `True` | `none` | `0.0007810274125596095` | `8.205083236642724e-05` | `0.11956645203696047` | `0.0` | `1.0` |
| `e3-circle` | `True` | `none` | `0.0008424456782388923` | `5.4218235796420334e-05` | `0.11948583087348669` | `0.0` | `1.0` |
| `e4-cardioid` | `True` | `none` | `0.0008414282785725735` | `3.1966302934437964e-07` | `0.11948589054856217` | `0.0` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
