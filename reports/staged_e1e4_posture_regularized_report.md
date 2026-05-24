# Staged E1-E4 Posture-Regularized Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v33-e1e4-posture-regularized`

Starting commit: `5892c29ae030c19b518eaddafdf0185726fbc04d`

## Scope

Carry the least intrusive passing v32 E2 posture objective into the full
slowed E1-E4 staged tilted-plane matrix.

Stage A is unchanged from v29-v32: weighted force-normal prealignment with
`approach_qdot_limit_rad_s = 0.25`. Stage B uses `linear-primary` trajectory
orientation with `trajectory_qdot_limit_rad_s = 0.15`, plus trajectory-phase
posture regularization:

- target posture: `q = [0, -0.1, 0.15, -0.05, 0, 0]`
- posture kp: `1.0`
- posture weight: `0.001`
- max posture velocity: `0.05 rad/s`

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747`

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
  --trajectory <e1-cycloid|e2-figure-eight|e3-circle|e4-cardioid> \
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
  --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 \
  --trajectory-posture-kp 1.0 \
  --trajectory-posture-weight 0.001 \
  --trajectory-max-posture-velocity-rad-s 0.05 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

## Result

Aggregate files:

- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.md`
- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.csv`
- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.yaml`
- `runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.json`

Counts:

- Approach terminal-orientation passes: `4 / 4`
- Approach ordinary-feasibility passes: `0 / 4`
- Trajectory feasibility passes: `4 / 4`
- Trajectory-after-approach passes: `4 / 4`
- Full staged-feasibility passes: `0 / 4`

| trajectory | failed criteria | orient err | qdot sat | tail util | force err N |
| --- | --- | ---: | ---: | ---: | ---: |
| `e1-cycloid` | none | `0.0038625381780712795` | `0.0` | `0.018807562833131748` | `0.0020256252939621078` |
| `e2-figure-eight` | none | `0.0203545748607252` | `0.0` | `0.015816929731774558` | `0.011842144259021303` |
| `e3-circle` | none | `0.007845080262833704` | `0.0` | `0.018773299004054896` | `0.0020256252939621078` |
| `e4-cardioid` | none | `0.003984908454267708` | `0.0` | `0.015004030029303684` | `0.0020256252939621078` |

## Interpretation

The v32 trajectory posture objective removes the last Stage B blocker in the
slowed E1-E4 tilted-plane matrix. Compared with v29, E2 no longer fails qdot
saturation. All four Stage B trajectories pass force, tangential tracking,
orientation, angular slack, qdot saturation, and joint-limit gates after the
current weighted prealignment state.

The full staged result still fails because Stage A remains unacceptable under
the ordinary approach gate. Each row repeats the same weighted prealignment,
which reaches the terminal orientation threshold but spends the approach qdot
budget and drifts tangentially. This branch therefore separates the current
state cleanly:

- Stage B after prealignment: solved for slowed E1-E4 under the current gates.
- Stage A approach: still unresolved.

## Decision

Treat the trajectory-after-prealignment E1-E4 matrix as passing with the v32
posture objective. Do not claim full staged feasibility until Stage A is fixed
or an explicit relaxed approach budget is accepted and documented.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
git diff --cached --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_e1e4_posture_regularized/20260524T102747/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `58 passed in 1.22s`
- `git diff --check` passed
- aggregate check printed `4 0 4 0`

## Limits

- This is slowed `paper_time_scale = 0.075` tilted-plane simulation evidence.
- It uses the current weighted prealignment state, which is not an accepted
  approach solution.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
