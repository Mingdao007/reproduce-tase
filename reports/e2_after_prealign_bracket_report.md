# E2 After Prealignment Bracket Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v30-e2-after-prealign-bracket`

Starting commit: `5e98b0f3516e6a171de6151046bda12be3bfca78`

## Scope

Isolate the E2 figure-eight failure found in the v29 staged E1-E4 matrix. This
branch keeps the same tilted-plane Stage A weighted prealignment and varies
only the Stage B paper time scale and trajectory orientation gain.

The tested Stage B grid is:

- `paper_time_scale`: `0.075`, `0.05`, `0.025`
- `trajectory_orientation_kp`: `0.10`, `0.05`, `0.02`, `0.00`

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429`

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
  --paper-time-scale <0.075|0.05|0.025> \
  --planar-kp 0.5 \
  --planar-slack-weight 1.0 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --approach-orientation-priority-mode weighted \
  --approach-orientation-kp 2.0 \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp <0.10|0.05|0.02|0.00> \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

## Result

Aggregate files:

- `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/summary.md`
- `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/summary.csv`
- `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/summary.yaml`
- `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/summary.json`

Counts:

- Approach terminal-orientation passes: `12 / 12`
- Approach ordinary-feasibility passes: `0 / 12`
- Trajectory-after-approach passes: `0 / 12`
- Trajectory feasibility passes: `0 / 12`
- Full staged-feasibility passes: `0 / 12`

| case | scale | kp | failed criteria | force error N | max orient err rad | qdot saturation | tail qdot util |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| `scale0p075_kp0p10` | 0.075 | 0.10 | qdot saturation, tail qdot utilization | `0.015191179672980932` | `0.020294558071100602` | `0.9935` | `1.0` |
| `scale0p075_kp0p00` | 0.075 | 0.00 | qdot saturation, tail qdot utilization | `0.015192783113904573` | `0.02029445962658342` | `0.99025` | `1.0` |
| `scale0p050_kp0p10` | 0.050 | 0.10 | qdot saturation, tail qdot utilization | `0.00763033693710233` | `0.013992485295420454` | `0.98375` | `1.0` |
| `scale0p050_kp0p00` | 0.050 | 0.00 | qdot saturation, tail qdot utilization | `0.007630272304588416` | `0.013992589911331708` | `0.97775` | `1.0` |
| `scale0p025_kp0p10` | 0.025 | 0.10 | qdot saturation, tail qdot utilization | `0.0026498747493683304` | `0.007889159305917036` | `0.93475` | `1.0` |
| `scale0p025_kp0p00` | 0.025 | 0.00 | qdot saturation, tail qdot utilization | `0.0020953131569018523` | `0.007897757695261808` | `0.906` | `1.0` |

All twelve rows fail only the two qdot-budget criteria. Force, position,
orientation, and slack stay inside thresholds in every case.

## Interpretation

Reducing trajectory orientation gain does not remove the E2 qdot failure. At
each tested paper time scale, the qdot saturation fraction changes only
slightly between `kp = 0.10` and `kp = 0.00`.

Slowing the E2 paper trajectory helps but not enough. The lowest tested scale
(`0.025`) and zero trajectory orientation gain still have qdot saturation
fraction `0.906` and tail qdot utilization `1.0`.

The E2 post-prealignment blocker is therefore not primarily the trajectory
orientation task. It is a kinematic velocity-budget issue for the E2 tangent
direction from the post-prealignment posture under the current `0.15 rad/s`
Stage B qdot cap.

## Decision

Do not keep expanding scalar E2 timing/gain brackets under this same posture
and task structure. The next useful experiment should change the posture,
prealignment terminal configuration, or tangent task allocation, or add an
explicit posture/nullspace objective before E2.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
git diff --cached --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `54 passed in 1.21s`
- `git diff --check` passed
- aggregate check printed `12 0 0 0`

## Limits

- This is E2-only tilted-plane simulation evidence.
- Stage A remains infeasible under the ordinary approach budget.
- The tested scales are already slower than the paper timing.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
