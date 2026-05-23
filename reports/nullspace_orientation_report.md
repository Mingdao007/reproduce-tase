# Linear-Primary Orientation Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v18-nullspace-orientation`

## Scope

This iteration replaces the scalar angular-priority tradeoff with an explicit
two-stage option:

1. solve the linear force-motion task with the existing slack-aware bounded
   solver;
2. solve the orientation-hold task subject to preserving the first-stage TCP
   linear velocity.

The goal is to test whether a linear-primary hierarchy can preserve the v14
full-speed planar/force behavior while using the remaining UR10e velocity
space for orientation hold. This remains simulation-only and does not authorize
real UR10e motion.

## Code Changes

- Added `solve_linear_primary_angular_secondary_with_slack(...)` in
  `src/tase_repro/constraints.py`.
- Added `angular_priority_mode="linear_primary"` to
  `CartesianVelocityCommand` and the force-motion simulation path.
- Added CLI support via `--orientation-priority-mode linear-primary` in the
  paper trajectory, timing sweep, and posture sweep drivers.
- Added tests proving the secondary angular solve preserves the primary linear
  rows and reports angular slack as desired-minus-actual angular velocity.

## Gates

The v16 combined gates are reused:

- max orientation error `<= 0.03 rad`
- max angular velocity slack `<= 0.03 rad/s`
- v12 force/contact/planar/qdot/joint-limit gates unchanged

Common settings:

- `--orientation-mode hold`
- `--orientation-priority-mode linear-primary`
- `--orientation-kp 1.0`
- `--angular-axis-weight 1.0`
- `--initial-q 0,-0.1,0.15,-0.05,0,0`
- `--base-z-offset-m=-0.0009710693359375`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`

## Runs

- `runs/nullspace_orientation_timing_sweep/20260524T042206`: E2/E3 timing
  sweep over `1.0`, `0.75`, `0.5`, `0.35`, `0.25`, `0.2`, `0.15`, `0.1`,
  and `0.075`.
- `runs/nullspace_orientation_timing_sweep/20260524T042206_common_0p075`:
  E1-E4 confirmation matrix at `paper_time_scale = 0.075`.

## E2/E3 Timing Result

| trajectory | fastest passing scale | full-speed binding failures |
| --- | ---: | --- |
| E2 figure-eight | `0.075` | qdot saturation, orientation error, angular slack |
| E3 circle | `0.075` | qdot saturation, orientation error, angular slack |

At full speed, the hierarchy preserves the linear force-motion gates but still
cannot satisfy the orientation gates inside the `0.15 rad/s` qdot cap:

| trajectory | scale | max pos err m | max planar slack m/s | qdot sat frac | max orient err rad | max angular slack rad/s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E2 | `1.0` | `8.944242741889184e-06` | `1.9575401563049538e-07` | `0.1845` | `0.03774766436372975` | `0.04492437394720665` |
| E3 | `1.0` | `5.999914591096698e-06` | `6.312024736453601e-07` | `0.15675` | `0.08131187102533075` | `0.08921566880313665` |

## Common 0.075 Matrix

The linear-primary E1-E4 matrix passes all combined gates at
`paper_time_scale = 0.075`:

| trajectory | pass | force error N | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s | tail qdot util |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `True` | `0.000276144819236912` | `1.1694975573206327e-08` | `5.958126716066033e-10` | `0.00010183147439858829` | `0.0001272290438944111` | `0.0038318015338999816` |
| E2 figure-eight | `True` | `0.0002771005815372496` | `6.708191085550114e-07` | `2.4433712474975925e-09` | `0.004516128236962064` | `0.005076738194606452` | `0.005903898478793365` |
| E3 circle | `True` | `0.00027633354479075225` | `4.49993594371628e-07` | `3.695694551120664e-09` | `0.006787233568225033` | `0.007632937570076151` | `0.005652094795331068` |
| E4 cardioid | `True` | `0.00027616389259353056` | `2.3656478121235595e-08` | `5.958126716066033e-10` | `1.2211424954475569e-05` | `1.6778016440715262e-05` | `0.0038831831175570393` |

## Interpretation

The hierarchy fixes the v17 failure mode where stronger angular priority
created large planar slack. However, it does not recover full-speed
orientation-gated E2/E3 because the remaining orientation correction drives the
controller into the qdot cap and still leaves too much orientation error at
high paper-time scales.

The accepted orientation-gated common timing remains `0.075`. The v18
linear-primary formulation is a cleaner controller baseline than the weighted
v16 solve at that timing because it preserves planar tracking much more
tightly, but it is not a full-speed paper reproduction.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- The secondary step preserves first-stage TCP linear velocity, not a complete
  torque-level hierarchy.
- Orientation hold still uses the initial TCP orientation, not a PDF-verified
  paper orientation law.
- The qdot cap is the current conservative simulation gate; relaxing it would
  require a separate safety and modeling decision.
