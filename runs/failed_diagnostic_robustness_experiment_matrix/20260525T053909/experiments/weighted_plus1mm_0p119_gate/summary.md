# Weighted Gate/Time Matrix Summary

Run root: `/home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`

- Group count: `8`
- Total case count: `20`
- Total stitched pass count: `9 / 20`
- All-pass groups: `time0p01_gate0p11995:weighted_kp0_normal1, time0p01_gate0p11995:weighted_kp0_normal30`
- Failing groups: `time0p0075_gate0p119:weighted_kp0_normal1, time0p0075_gate0p119:weighted_kp0_normal30, time0p01_gate0p119:weighted_kp0_normal1, time0p01_gate0p119:weighted_kp0_normal30, gate_boundary_plus1mm_time_0p0075, gate_boundary_plus1mm_time_0p01`

## Full Matrix Groups

| group | scenario | time scale | gate | pass count | max pass delta mm | max orientation | max qdot sat | max tail qdot | max force err |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `time0p01_gate0p11995:weighted_kp0_normal1` | `weighted_kp0_normal1` | `0.01` | `0.11995` | `1/1` | `1.0` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `time0p01_gate0p11995:weighted_kp0_normal30` | `weighted_kp0_normal30` | `0.01` | `0.11995` | `1/1` | `1.0` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `weighted_kp0_normal1` | `0.0075` | `0.119` | `0/1` | `None` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `weighted_kp0_normal30` | `0.0075` | `0.119` | `0/1` | `None` | `0.11954627160547111` | `0.0` | `0.5177926211135458` | `0.0008422275835027282` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `weighted_kp0_normal1` | `0.01` | `0.119` | `0/1` | `None` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `weighted_kp0_normal30` | `0.01` | `0.119` | `0/1` | `None` | `0.11956645203696047` | `0.0` | `0.520987929048311` | `0.0008424456782388923` |

## Gate Boundary Groups

| group | time scale | pass count | min passing gate | max failing gate | max orientation | max qdot sat |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gate_boundary_plus1mm_time_0p0075` | `0.0075` | `4/7` | `0.11955` | `0.1195` | `0.11954627160547111` | `0.0` |
| `gate_boundary_plus1mm_time_0p01` | `0.01` | `3/7` | `0.1196` | `0.11955` | `0.11956645203696047` | `0.0` |

## Failed Case Detail

| group | case | stitched | Stage A | Stage B pass | gate | time scale | delta mm | E2 orientation | E2 qdot sat | failed rows |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `weighted_kp0_normal1:time0p0075_gate0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.0075` | `1.0` | `0.11954627160547111` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `weighted_kp0_normal30:time0p0075_gate0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.0075` | `1.0` | `0.11954627160547111` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `weighted_kp0_normal1:time0p01_gate0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `weighted_kp0_normal30:time0p01_gate0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p0075` | `weighted_kp0_normal1:time_0p0075_gate_0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.0075` | `1.0` | `0.11954627160547111` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p0075` | `weighted_kp0_normal1:time_0p0075_gate_0p11925:delta1p000mm` | `False` | `False` | `0/4` | `0.11925` | `0.0075` | `1.0` | `0.11954627160547111` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p0075` | `weighted_kp0_normal1:time_0p0075_gate_0p1195:delta1p000mm` | `False` | `True` | `3/4` | `0.1195` | `0.0075` | `1.0` | `0.11954627160547111` | `0.0` | `e2-figure-eight:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p01` | `weighted_kp0_normal1:time_0p01_gate_0p119:delta1p000mm` | `False` | `False` | `0/4` | `0.119` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p01` | `weighted_kp0_normal1:time_0p01_gate_0p11925:delta1p000mm` | `False` | `False` | `0/4` | `0.11925` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e1-cycloid:max_orientation_error_rad; e2-figure-eight:max_orientation_error_rad; e3-circle:max_orientation_error_rad; e4-cardioid:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p01` | `weighted_kp0_normal1:time_0p01_gate_0p1195:delta1p000mm` | `False` | `True` | `3/4` | `0.1195` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e2-figure-eight:max_orientation_error_rad` |
| `gate_boundary_plus1mm_time_0p01` | `weighted_kp0_normal1:time_0p01_gate_0p11955:delta1p000mm` | `False` | `True` | `3/4` | `0.11955` | `0.01` | `1.0` | `0.11956645203696047` | `0.0` | `e2-figure-eight:max_orientation_error_rad` |

Interpretation:

- The `0.01` full matrix checks whether the v82 focused timing sweep generalizes across all positive deltas under the `0.11995 rad` gate.
- The `0.119 rad` full matrix checks whether the weighted candidate changes the tightened-gate `+1.0 mm` limit.
- The focused gate-boundary groups bracket the `+1.0 mm` gate needed by weighted zero-angular-command priority.
- This remains diagnostic-label simulation evidence only.
