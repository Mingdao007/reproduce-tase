# Positive Orientation Gate Boundary Summary

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`

- Case count: `9`
- Stitched pass count: `2 / 9`
- Max failing orientation gate: `0.11997`
- Min passing orientation gate: `0.11998`
- Stage A passed every case: `False`

| orientation gate | stitched | Stage A | Stage B pass | Stage A orientation | Max Stage B orientation | failed rows |
| ---: | --- | --- | ---: | ---: | ---: | --- |
| `0.119` | `False` | `False` | `0/4` | `0.11948560786547915` | `0.1199788204275829` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `0.11925` | `False` | `False` | `0/4` | `0.11948560786547915` | `0.1199788204275829` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `0.1195` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.1199788204275829` | `e2-figure-eight:max_orientation_error_rad` |
| `0.11975` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.1199788204275829` | `e2-figure-eight:max_orientation_error_rad` |
| `0.1199` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.1199788204275829` | `e2-figure-eight:max_orientation_error_rad` |
| `0.11995` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.1199788204275829` | `e2-figure-eight:max_orientation_error_rad` |
| `0.11997` | `False` | `True` | `3/4` | `0.11948560786547915` | `0.1199788204275829` | `e2-figure-eight:max_orientation_error_rad` |
| `0.11998` | `True` | `True` | `4/4` | `0.11948560786547915` | `0.1199788204275829` | `none` |
| `0.12` | `True` | `True` | `4/4` | `0.11948560786547915` | `0.1199788204275829` | `none` |

Interpretation:

- The `+1.0 mm` tightened-orientation boundary is controlled by the maximum Stage B orientation error under the v72 timing.
- Stage A passes once the gate is above the terminal orientation value, but stitched recovery still needs the Stage B maximum to fit.
- This does not change the v75 qdot012 recovery or the v76 faster-timing boundary.
