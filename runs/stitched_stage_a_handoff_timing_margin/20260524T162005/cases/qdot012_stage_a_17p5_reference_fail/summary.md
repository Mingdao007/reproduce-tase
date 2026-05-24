# Stitched Stage A Tracking + Stage B Handoff Summary

Run root: `/home/andy/reproduce-tase/runs/stitched_stage_a_handoff_timing_margin/20260524T162005/cases/qdot012_stage_a_17p5_reference_fail`

- Selected label: `ur10e_adapted_terminal_setup_diagnostic`
- Stitched gate pass: `False`
- Stage A gate pass: `False`
- Stage B handoff passes: `0 / 4`
- Stage A duration: `17.5`
- Stage B duration per trajectory: `2.0`
- Stage A max qdot: `0.12`
- Stage A qdot saturation fraction: `0.0077714285714285715`

| trajectory | pass | failed criteria | target force tail error N | max x/y error m | max orientation error rad | qdot saturation | target contact |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `False` | `qdot_saturation_fraction` | `1.0853789426517046e-05` | `6.389447941279153e-06` | `0.07200378492908399` | `0.016` | `1.0` |
| `e2-figure-eight` | `False` | `qdot_saturation_fraction` | `0.0051716759259824` | `6.050163823413924e-06` | `0.07200389101019385` | `0.016` | `1.0` |
| `e3-circle` | `False` | `qdot_saturation_fraction` | `1.159273360943125e-05` | `6.389774345445081e-06` | `0.07200378492945034` | `0.016` | `1.0` |
| `e4-cardioid` | `False` | `qdot_saturation_fraction` | `1.0203426368704527e-05` | `6.38938486529142e-06` | `0.07200378492908399` | `0.016` | `1.0` |

Interpretation:

- This is the first single-run diagnostic Stage A tracker plus Stage B handoff evaluation.
- It remains diagnostic-label simulation evidence, not strict paper-equivalent feasibility.
- It is not hardware-ready.
