# Positive Relaxed Orientation Recovery Summary

Run root: `/home/andy/reproduce-tase/runs/positive_relaxed_orientation_recovery/20260524T172909`

- Case count: `8`
- Start pass count: `8`
- Terminal pass count: `8`
- Path geometry pass count: `8`
- Duration recovered count: `0`
- Max positive terminal-pass delta mm: `1.0`
- Max positive recovered delta mm: `None`

| delta mm | status | start | terminal | path pass | path min duration s | recovered durations | terminal orientation rad |
| ---: | --- | --- | --- | --- | ---: | --- | ---: |
| `0.05` | `stitched_failed` | `True` | `True` | `True` | `14.198707940657611` | `none` | `0.0838175590896232` |
| `0.1` | `stitched_failed` | `True` | `True` | `True` | `14.206784149197896` | `none` | `0.08565245135290023` |
| `0.15` | `stitched_failed` | `True` | `True` | `True` | `14.211524053903112` | `none` | `0.0874945141256073` |
| `0.2` | `stitched_failed` | `True` | `True` | `True` | `14.424277184724716` | `none` | `0.08934348318237911` |
| `0.25` | `stitched_failed` | `True` | `True` | `True` | `11.996410618897185` | `none` | `0.09119904265401833` |
| `0.5` | `stitched_failed` | `True` | `True` | `True` | `11.224745619891337` | `none` | `0.10056247728510045` |
| `0.75` | `stitched_failed` | `True` | `True` | `True` | `10.367805178961204` | `none` | `0.11002164736335575` |
| `1.0` | `stitched_failed` | `True` | `True` | `True` | `10.018584837157274` | `none` | `0.11948560786548146` |

Interpretation:

- This audit tests whether the v69 `0.12 rad` diagnostic orientation margin can unlock positive-side terminal, path, and stitched recovery in the current contact-point model.
- It uses a run-local relaxed Stage A target config and does not change the canonical v58 target config.
- It remains diagnostic-label simulation evidence only, not strict paper-equivalent feasibility, robustness, contact-model calibration, or hardware readiness.
