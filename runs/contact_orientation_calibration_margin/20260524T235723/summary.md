# Contact Orientation Calibration Margin Summary

Run root: `/home/andy/reproduce-tase/runs/contact_orientation_calibration_margin/20260524T235723`

## Critical Rows

| group | time scale | Stage A orientation | Stage B orientation | Stage B excess over 0.119 | qdot sat | tail qdot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `time0p0075_gate0p119:weighted_kp0_normal1` | `0.0075` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p0075_gate0p119:weighted_kp0_normal30` | `0.0075` | `0.11948560786547915` | `0.11954627160547111` | `0.0005462716054711186` | `0.0` | `0.5177926211135458` |
| `time0p01_gate0p119:weighted_kp0_normal1` | `0.01` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |
| `time0p01_gate0p119:weighted_kp0_normal30` | `0.01` | `0.11948560786547915` | `0.11956645203696047` | `0.0005664520369604714` | `0.0` | `0.520987929048311` |

## Equivalent Correction

- Required normal rotation: `0.0005664520369604714` rad (`0.03245531101442353` deg).
- Equivalent base-z/contact-point correction under the terminal slope proxy: `0.014963398168061883` mm (`14.963398168061882` um).
- Contact-point versus legacy-center convention shift: `0.024227219479550713` rad.
- Residual margin is `42.77011626536238` times smaller than that convention shift.

## Gate Options

| option | gate | recovered by existing metric | accepted replacement gate | scope |
| --- | ---: | --- | --- | --- |
| `current_0p119` | `0.119` | `False` | `False` | full positive-delta weighted matrix at +1.0 mm |
| `v83_min_passing_time0p0075` | `0.11955` | `True` | `False` | focused +1.0 mm gate-boundary row at paper_time_scale = 0.0075 |
| `v83_min_passing_time0p01` | `0.1196` | `True` | `False` | focused +1.0 mm gate-boundary row at paper_time_scale = 0.01 |
| `diagnostic_0p11995` | `0.11995` | `True` | `False` | full positive-delta weighted matrix at paper_time_scale = 0.01 |

## Answers

- 1. What exact orientation margin remains at the hardest currently known row?: 0.0005664520369604714 rad (0.03245531101442353 deg) over the 0.119 rad gate at time0p01_gate0p119:weighted_kp0_normal1.
- 2. How large a contact normal angular correction would close that margin?: At least 0.0005664520369604714 rad (0.03245531101442353 deg), assuming the correction acts in the error-reducing direction.
- 3. What equivalent contact-point/TCP/base-z correction is implied?: 0.014963398168061883 mm (14.963398168061882 um) using the v84 high-end terminal slope proxy of 0.03785584200850284 rad/mm.
- 4. Which correction sizes are plausibly below measurement/calibration noise?: The 0.0325 deg normal correction and 15 um equivalent geometry correction are small relative to the current unmeasured model-convention ambiguity, but no accepted measurement noise budget exists yet.
- 5. Which physical measurements are required before a hardware claim?: measured mounted-stack TCP/contact point from robot flange or design flange datum; verified contact sphere/patch convention and whether the 85 mm EOAT datum is center or surface; plane/contact normal measured in the robot base frame; force sensor zero, frame, compensation, and UR RTDE versus OnRobot source reconciliation; accepted diagnostic orientation definition that states whether force-normal-only or full frame rotation is the gate
- 6. Do existing metrics justify accepting 0.119, 0.11955, 0.1196, or 0.11995 rad?: They show which rows recover at those gates, but they do not justify a replacement diagnostic gate without calibrated geometry/normal evidence.
- 7. Does this support more Stage B qdot tuning?: No. The hardest weighted rows report 0.0 qdot saturation and miss only by a small orientation margin.

## Claim Boundary

- This is a calibration/definition margin audit only.
- It does not recover the `+1.0 mm`, `0.119 rad` gate.
- It does not accept a relaxed diagnostic gate.
- It does not calibrate the contact model, prove robustness, prove strict paper-equivalent feasibility, or authorize hardware motion/configuration.
