# Weighted Orientation Model Sensitivity Summary

Run root: `/home/andy/reproduce-tase/runs/weighted_orientation_model_sensitivity/20260524T233945`

## Critical V83 Rows

| group | pass | Stage A orientation | Stage B orientation | Stage B excess over 0.119 | qdot sat | tail qdot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `7/8` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `7/8` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `7/8` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `7/8` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |

## Gate Boundary

| group | min passing gate | max failing gate | Stage B max orientation |
| --- | ---: | ---: | ---: |
| `gate_boundary_plus1mm_time_0p0075` | `0.11955` | `0.1195` | `0.11954627160547111` |
| `gate_boundary_plus1mm_time_0p01` | `0.1196` | `0.11955` | `0.11956645203696047` |

## Terminal Model Sensitivity

- Contact-point +1.0 mm terminal orientation: `0.11948560786548146` rad
- Legacy-center +1.0 mm terminal orientation: `0.09525838838593075` rad
- Geometry-convention orientation delta: `0.024227219479550713` rad
- High-end terminal slope proxy: `0.03785584200850284` rad/mm

## Interpretation

- The v83 `0.119 rad` failures are orientation-margin failures; qdot saturation is `0.0` in the critical weighted rows.
- The remaining Stage B excess over `0.119 rad` is less than `0.00057 rad` (`0.033 deg`).
- The contact-point versus legacy-center geometry convention changes the +1.0 mm terminal orientation by about `0.024 rad`, much larger than the remaining v83 margin.
- This is a sensitivity/attribution audit only. It is not a recovery, calibration, robustness proof, paper-equivalent claim, or hardware-ready result.
