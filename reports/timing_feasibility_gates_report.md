# Timing Feasibility Gates Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v12-feasibility-gates`

Run root:

`runs/timing_feasibility_sweep/20260524T021322`

## Scope

This iteration turns the v11 slack diagnostics into explicit simulation
pass/fail gates and runs a paper-time-scale sweep for the two open full-speed
cases:

- E2 figure-eight.
- E3 circle.

Common settings:

- `--use-slack-solve`
- `--planar-slack-weight 1`
- `--normal-slack-weight 10000`
- `--slack-constraint-weight 1000`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--paper-time-scale 1.0,0.75,0.5,0.35,0.25,0.2,0.15,0.1`

This remains simulation-only. No real UR10e motion or hardware writes were
performed.

## Gates

The feasibility evaluator requires:

- solver success fraction `>= 1.0`
- contact present fraction `>= 1.0`
- tail mean absolute force error `<= 0.25 N`
- max tangential position error `<= 0.002 m`
- max planar velocity slack `<= 0.001 m/s`
- max absolute normal velocity slack `<= 0.0002 m/s`
- max qdot violation `<= 1e-9 rad/s`
- max joint-limit violation `<= 1e-9 rad`
- qdot saturation fraction `<= 0.01`
- tail max qdot utilization `<= 0.98`

The qdot saturation gates intentionally allow a tiny startup transient while
rejecting sustained saturation during the trajectory tail.

## Results

Fastest passing scale:

- E2 figure-eight: `0.2`
- E3 circle: `0.2`

Representative rows:

| trajectory | scale | pass | failed criteria | tail force error N | max position error m | max planar slack m/s | qdot saturation fraction | tail max qdot utilization |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| E2 | `1.0` | `False` | position, planar slack, qdot saturation | `0.0479840836286729` | `0.02114338335402673` | `0.013216502110190214` | `0.78175` | `0.9999999999999998` |
| E2 | `0.25` | `False` | qdot saturation | `0.0007294332645588986` | `0.00031737751452890384` | `0.0007251472811804109` | `0.11525` | `0.9999999999999998` |
| E2 | `0.2` | `True` | none | `0.00034204709355621144` | `1.7888622586078747e-06` | `2.3310453749022684e-07` | `0.00075` | `0.10194983790754977` |
| E3 | `1.0` | `False` | position, planar slack, qdot saturation | `0.014410140908808211` | `0.016176223350410992` | `0.010692708281149576` | `0.7635` | `0.9999999999999998` |
| E3 | `0.25` | `False` | qdot saturation | `0.0003790708341966742` | `0.00023000343483424836` | `0.0009047004546188087` | `0.044` | `0.9999999999999998` |
| E3 | `0.2` | `True` | none | `0.00034345836495965564` | `1.1999829125721333e-06` | `1.592789560750357e-07` | `0.00075` | `0.0713623093095374` |

Full aggregate tables are in:

- `runs/timing_feasibility_sweep/20260524T021322/summary.md`
- `runs/timing_feasibility_sweep/20260524T021322/summary.csv`
- `runs/timing_feasibility_sweep/20260524T021322/summary.yaml`
- `runs/timing_feasibility_sweep/20260524T021322/summary.json`

## Interpretation

The strict timing result is:

- Full-speed E2/E3 remain rejected.
- `paper_time_scale = 0.25` fixes force, contact, path error, and slack, but
  still spends too much of the trajectory at the qdot cap.
- `paper_time_scale = 0.2` is the fastest tested scale that satisfies all
  current gates for both E2 and E3.

This reframes the open blocker: the current velocity-level controller can make
E2/E3 feasible only after slowing the paper timing to about one fifth of the
paper speed under this posture, qdot cap, and MuJoCo contact setup.

## Limitations

- The thresholds are engineering gates for this UR10e adapted simulation, not
  paper-reported acceptance criteria.
- The controller is still velocity-level and lacks torque dynamics,
  impedance, and orientation compliance.
- The starting posture, TCP, contact model, and force source are still
  approximate and not hardware validated.
- The accepted `0.2` result is a slowed trajectory feasibility point, not a
  full-speed paper reproduction.

## Next Step

Use the `0.2` feasible timing point as a controlled baseline, then test whether
posture changes or a planned approach phase can move the fastest passing scale
closer to `1.0` before adding orientation compliance.
