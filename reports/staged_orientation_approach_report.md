# Staged Orientation Approach Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v24-staged-orientation-approach`

Starting commit: `9059345767e6f2282013a2d6bc28d530b0e99440`

## Scope

Implement and test a simulation-only staged tilted-plane orientation approach.
Stage A aligns TCP local z to the tilted contact normal while holding a zero
planar trajectory. Stage B restarts the E1 paper trajectory from the
prealigned q. This does not move or write settings to the real UR10e, OnRobot,
TCP, payload, URCap, or force sensor.

## Implementation

New files:

- `src/tase_repro/staged_force_motion.py`
- `scripts/run_staged_orientation_force_motion.py`
- `tests/test_staged_force_motion.py`

The staged helper runs:

```text
Stage A: stationary planar command + force-normal orientation approach
Stage B: paper planar trajectory from Stage A terminal q
```

The runner writes separate `approach/` and `trajectory/` phase metrics and an
aggregate root summary. This keeps approach-phase saturation and planar drift
visible instead of mixing them into the paper-trajectory phase.

## Run

Run root:

- `runs/staged_orientation_force_motion/20260524T092927`

Command:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --output-dir runs/staged_orientation_force_motion/20260524T092927 \
  --approach-duration-s 4.0 \
  --trajectory-duration-s 2.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --qdot-limit-rad-s 0.15 \
  --trajectory e1-cycloid \
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
  --trajectory-orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

## Result

| phase | pass | key result |
| --- | --- | --- |
| approach terminal orientation | `True` | final orientation error `0.0020237968932491765 rad`, first below `0.03 rad` at `0.912 s` |
| approach full feasibility gate | `False` | qdot saturation fraction `0.961`, max planar drift `0.009738544642078033 m`, max angular slack `0.06085033484246333 rad/s` |
| trajectory after approach | `True` | max orientation error `0.0020303573682621625 rad`, qdot saturation fraction `0.003`, no failed criteria |
| full staged feasibility | `False` | approach phase still fails the ordinary run gates |

The staged approach solves the v23 trajectory-start problem: after
prealignment, the E1 trajectory phase passes all current force-motion,
orientation, qdot, and joint-limit gates. It does not solve the approach
phase itself. The approach uses sustained qdot saturation and allows planar
drift while rotating the TCP into the tilted normal.

## Verification

Commands:

```bash
python3 -m py_compile src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_force_motion/20260524T092927/metrics.yaml').read_text())
print(m['trajectory_after_approach_pass'], m['full_staged_feasibility_pass'])
PY
```

Result:

- `51 passed in 1.10s`
- `git diff --check` passed
- aggregate metrics report `trajectory_after_approach_pass: true`
- aggregate metrics report `full_staged_feasibility_pass: false`

## Limits

- This is a single tilted analytic plane, not a curved unknown surface.
- Stage A is an adapted prealignment maneuver, not the paper's torque-level
  finite-time RNN.
- The approach phase consumes sustained qdot saturation and should not be
  treated as a validated robot approach.
- The approximate UR10e MJCF and unverified 85 mm TCP remain simulation
  scaffolding.

## Next Step

Improve Stage A so it reaches the tilted normal with less planar drift and
without sustained qdot saturation, or explicitly decide that tilted-surface
prealignment uses a separate relaxed approach budget before paper-trajectory
tracking begins.
