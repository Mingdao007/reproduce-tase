# E2 Posture Regularization Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v32-posture-regularization`

Starting commit: `e1af9174121dedb56af4489dcffbe06f3ef8cb9b`

## Scope

Add a simulation-only joint-velocity posture regularization hook to the
bounded velocity controller, then retest the E2 figure-eight failure from v29
through v31.

The new regularization target is:

```text
qdot_ref = clip_inf(kp * (q_posture - q), max_posture_velocity)
```

and it is added as a weighted velocity objective inside the optimizer. For
`linear-primary` trajectory orientation, the primary linear solve keeps its
existing behavior and the posture target is applied in the secondary
nullspace objective that preserves the primary TCP linear velocity.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_e2_posture_regularization/20260524T102224`

Common runner:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --approach-duration-s 4.0 \
  --trajectory-duration-s 8.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --qdot-limit-rad-s 0.15 \
  --approach-qdot-limit-rad-s 0.25 \
  --trajectory-qdot-limit-rad-s 0.15 \
  --trajectory e2-figure-eight \
  --omega-rad-s 0.1 \
  --paper-time-scale 0.075 \
  --planar-kp 0.5 \
  --planar-slack-weight 1.0 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --approach-orientation-priority-mode weighted \
  --approach-orientation-kp 2.0 \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp 0.10 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

Posture cases use target `q = [0, -0.1, 0.15, -0.05, 0, 0]`, `kp = 1.0`,
and max posture velocity `0.05 rad/s`, with posture weights `0.001`, `0.01`,
and `0.1` applied to trajectory-only, approach-only, or both phases.

## Result

Aggregate files:

- `runs/staged_orientation_e2_posture_regularization/20260524T102224/summary.md`
- `runs/staged_orientation_e2_posture_regularization/20260524T102224/summary.csv`
- `runs/staged_orientation_e2_posture_regularization/20260524T102224/summary.yaml`
- `runs/staged_orientation_e2_posture_regularization/20260524T102224/summary.json`

Counts:

- Approach terminal-orientation passes: `10 / 10`
- Approach ordinary-feasibility passes: `0 / 10`
- Trajectory feasibility passes: `4 / 10`
- Trajectory-after-approach passes: `4 / 10`
- Full staged-feasibility passes: `0 / 10`

| case | phase | weight | failed criteria | E2 orient err | E2 qdot sat | tail util | force err N |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `baseline` | none | 0.0 | qdot saturation, tail qdot utilization | `0.020294558071100602` | `0.9935` | `1.0` | `0.015543559546856045` |
| `trajectory_w0p001` | trajectory | 0.001 | none | `0.0203545748607252` | `0.0` | `0.015816929731774558` | `0.011842144259021303` |
| `trajectory_w0p01` | trajectory | 0.01 | none | `0.02257965740356133` | `0.0` | `0.012156427259521778` | `0.01199958307572846` |
| `trajectory_w0p1` | trajectory | 0.1 | orientation | `0.0470714526557534` | `0.0` | `0.03872667331311572` | `0.012019995583968601` |
| `approach_w0p001` | approach | 0.001 | qdot saturation, tail qdot utilization | `0.020262454514735267` | `0.99875` | `1.0` | `0.01554842357981645` |
| `approach_w0p01` | approach | 0.01 | qdot saturation, tail qdot utilization | `0.018046083032793606` | `0.873` | `1.0` | `0.015541878599242054` |
| `approach_w0p1` | approach | 0.1 | contact, force error | `0.004585181966021033` | `0.0` | `0.19286920174859198` | `5.0` |
| `both_w0p001` | both | 0.001 | none | `0.02032274607472726` | `0.0` | `0.015813124322961183` | `0.01164567391060789` |
| `both_w0p01` | both | 0.01 | none | `0.020634679203137215` | `0.0` | `0.013426156756298442` | `0.011815380010165022` |
| `both_w0p1` | both | 0.1 | contact, force error | `0.014264369164437523` | `0.0` | `0.16691630259259307` | `5.0` |

## Interpretation

Moderate trajectory-phase posture regularization fixes the isolated E2 Stage B
blocker. The `trajectory_w0p001`, `trajectory_w0p01`, `both_w0p001`, and
`both_w0p01` cases all pass the trajectory-after-approach gate, with qdot
saturation fraction `0.0` and tail qdot utilization below `0.016`.

This does not solve the full staged reproduction. Stage A still has
`0 / 10` ordinary-feasibility passes because the weighted prealignment phase
continues to spend the qdot budget. Strong approach posture weighting
(`0.1`) also breaks contact/force tracking rather than producing a safe
approach fix.

The new controller hook is therefore useful, but the accepted claim is narrow:
E2 Stage B can be made feasible after the current relaxed weighted
prealignment by adding a moderate secondary posture objective. The next
remaining blocker is still the Stage A approach task structure.

## Decision

Use trajectory-phase posture regularization as the E2 Stage B fix candidate.
Do not claim full staged feasibility until Stage A has an accepted budget or a
new task structure that avoids sustained saturation and unbounded drift.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
git diff --cached --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_e2_posture_regularization/20260524T102224/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `58 passed in 1.21s`
- `git diff --check` passed
- aggregate check printed `10 0 4 0`

## Limits

- This is E2-only tilted-plane simulation evidence.
- It depends on the relaxed weighted prealignment state from the previous
  staged experiments.
- Stage A remains infeasible under the ordinary approach budget.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
