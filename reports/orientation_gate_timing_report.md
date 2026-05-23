# Orientation Gate Timing Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v16-orientation-gates`

## Scope

This iteration turns the v15 orientation metrics into optional pass/fail
criteria and uses them to test timing feasibility. The sweep keeps the v14
calibrated `bend_0p10` MuJoCo posture and the v15 orientation-hold task, but
uses stronger angular priority than the v15 full-speed passing run.

This remains simulation-only and does not authorize real UR10e motion.

## Gate

The v12 force-motion gates are retained and two provisional orientation gates
are added:

- max orientation error `<= 0.03 rad`
- max angular velocity slack `<= 0.03 rad/s`

These values are engineering thresholds for simulation triage, not paper
claims or hardware acceptance thresholds.

## Runs

Common settings:

- `--orientation-mode hold`
- `--orientation-kp 1.0`
- `--angular-slack-weight 0.1`
- `--max-orientation-error-rad 0.03`
- `--max-angular-slack-rad-s 0.03`
- `--initial-q 0,-0.1,0.15,-0.05,0,0`
- `--base-z-offset-m=-0.0009710693359375`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`

Run roots:

- `runs/orientation_gate_timing_sweep/20260524T023847`
- `runs/orientation_gate_timing_sweep/20260524T023938_e2e3_slow`
- `runs/orientation_gate_timing_sweep/20260524T024000_e3_slowest`
- `runs/orientation_gate_timing_sweep/20260524T024026_common_0p075`

## Results

Fastest tested per-trajectory scale passing the combined force-motion and
orientation gates:

| trajectory | fastest passing scale |
| --- | ---: |
| E1 cycloid | `0.5` |
| E2 figure-eight | `0.1` |
| E3 circle | `0.075` |
| E4 cardioid | `0.5` |

The common `paper_time_scale = 0.075` E1-E4 matrix passes all combined gates:

| trajectory | pass | force error N | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s | tail qdot util |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 cycloid | `True` | `0.0002761448535938249` | `1.8868465925812454e-05` | `1.4265227440402491e-05` | `3.059816704048032e-05` | `3.780945473030017e-05` | `0.003832267316618259` |
| E2 figure-eight | `True` | `0.00027738073633691964` | `0.0008569078322545231` | `0.0005386775381705987` | `0.0012822401289417794` | `0.0014280104295813921` | `0.013350766959419039` |
| E3 circle | `True` | `0.0002767261880519001` | `0.0012876485738243357` | `0.0008100249550457771` | `0.0019271205686722252` | `0.0021471302908745147` | `0.02105363299341864` |
| E4 cardioid | `True` | `0.00027616389789717475` | `2.2219365951485773e-06` | `1.9594471061394405e-06` | `3.821381556607561e-06` | `5.1934498799531995e-06` | `0.0038831888029910574` |

## Interpretation

Once orientation is a hard gate, the full-speed v14/v15 posture baseline no
longer passes with this stronger angular priority. E1 and E4 can pass at
`0.5`, E2 needs `0.1`, and E3 needs `0.075`. The hardest trajectory remains
E3 circle because it carries the largest planar slack under the angular task.

The common `0.075` matrix is a conservative, gated simulation baseline for
force, contact, planar tracking, qdot saturation, joint limits, and initial
orientation hold. It is not a full-speed paper reproduction and not the
paper's original orientation law.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- Orientation hold uses the initial TCP orientation, not the paper's ambiguous
  orientation signal.
- The gate values are provisional and should be revisited after the paper
  orientation signal is fully extracted and mapped.
- The common passing matrix is slowed to `paper_time_scale = 0.075`.

## Next Step

Decide whether to pursue full-speed orientation feasibility through a stricter
task-priority solve, a different posture sweep, or a paper-specific orientation
signal. Keep the `0.075` common matrix as the current gated simulation
fallback.
