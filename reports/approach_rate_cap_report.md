# Approach Rate Cap Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v27-approach-rate-cap`

Starting commit: `5bf5cb829744625a52905d82e996b20515049f84`

## Scope

Add and test a simulation-only angular-command cap for the tilted-plane Stage A
orientation approach. This caps the commanded angular velocity before the hard
joint-velocity solve, so the logs can distinguish the requested orientation
rate from downstream qdot saturation.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Implementation

Updated files:

- `src/tase_repro/force_feedback.py`
- `src/tase_repro/staged_force_motion.py`
- `scripts/run_staged_orientation_force_motion.py`
- `tests/test_staged_force_motion.py`

New API/CLI surface:

```text
simulate_planar_force_motion(..., max_angular_command_rad_s=None)
simulate_orientation_prealign_then_planar_force_motion(
    ...,
    approach_max_angular_command_rad_s=None,
    trajectory_max_angular_command_rad_s=None,
)
scripts/run_staged_orientation_force_motion.py \
  --approach-max-angular-command-rad-s <rad/s> \
  --trajectory-max-angular-command-rad-s <rad/s>
```

Negative cap values raise `ValueError`. Capped runs keep the cap visible in
phase metrics as `max_angular_command_rad_s`, while existing summary metrics
record the measured maximum commanded and actual angular velocity.

## Run

Run root:

- `runs/staged_orientation_rate_cap_probe/20260524T094752`

Common runner:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
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
  --approach-orientation-kp 2.0 \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

Varied cases:

| case | approach priority | cap rad/s | approach duration s |
| --- | --- | ---: | ---: |
| `weighted_uncapped_kp2_4s` | `weighted` | none | 4.0 |
| `weighted_cap0p05_kp2_4s` | `weighted` | 0.05 | 4.0 |
| `weighted_cap0p03_kp2_6s` | `weighted` | 0.03 | 6.0 |
| `weighted_cap0p02_kp2_10s` | `weighted` | 0.02 | 10.0 |
| `weighted_cap0p01_kp2_20s` | `weighted` | 0.01 | 20.0 |
| `linear_primary_cap0p03_kp2_12s` | `linear-primary` | 0.03 | 12.0 |

## Result

Aggregate files:

- `runs/staged_orientation_rate_cap_probe/20260524T094752/summary.md`
- `runs/staged_orientation_rate_cap_probe/20260524T094752/summary.csv`
- `runs/staged_orientation_rate_cap_probe/20260524T094752/summary.yaml`
- `runs/staged_orientation_rate_cap_probe/20260524T094752/summary.json`

| case | max commanded angular rad/s | final orientation error rad | first <=0.03 s | qdot sat | planar drift m | trajectory after approach | full staged pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_uncapped_kp2_4s` | 0.349066 | 0.0020238 | 0.912 | 0.961 | 0.00973854 | `True` | `False` |
| `weighted_cap0p05_kp2_4s` | 0.05 | 0.00621702 | 2.988 | 0.546 | 0.0077846 | `False` | `False` |
| `weighted_cap0p03_kp2_6s` | 0.03 | 0.00805794 | 4.990 | 0.46366666666666667 | 0.0075547 | `False` | `False` |
| `weighted_cap0p02_kp2_10s` | 0.02 | 0.00280475 | 7.516 | 0.5072 | 0.0082407 | `True` | `False` |
| `weighted_cap0p01_kp2_20s` | 0.01 | 0.00254981 | 15.272 | 0.5001 | 0.00827622 | `True` | `False` |
| `linear_primary_cap0p03_kp2_12s` | 0.03 | 0.0741620 | none | 0.7318333333333333 | 0.00000675 | `False` | `False` |

Counts:

- Command cap respected: `6 / 6`
- Approach terminal-orientation passes: `5 / 6`
- Approach terminal-budget passes: `0 / 6`
- Approach ordinary-feasibility passes: `0 / 6`
- Trajectory-after-approach passes: `3 / 6`
- Full staged-feasibility passes: `0 / 6`

## Interpretation

The command cap works mechanically. Each capped case reports maximum commanded
angular velocity at the configured cap.

The cap is not sufficient to make Stage A feasible. Weighted capped cases
reduce qdot saturation versus the uncapped v24/v25 baseline, but they still
exceed the qdot budget by a large margin and keep planar drift above the
`0.002 m` threshold. The best capped weighted qdot saturation fraction is
`0.46366666666666667`, still far above the current `0.01` gate.

The capped `linear-primary` reference keeps planar drift small, but it stalls
at `0.07416203560682781 rad` and does not reach the terminal orientation
threshold.

## Decision

Keep the angular-command cap as useful instrumentation and a safe controller
surface, but do not treat it as the Stage A solution. The next Stage A attempt
should change the task structure, not only the orientation command magnitude.
Candidate next steps are:

- explicit position-hold constraints during approach;
- a separate orientation-only prealignment state that admits documented planar
  drift and relaxed qdot budget;
- or a new task-priority formulation that preserves contact/position first and
  uses remaining velocity budget for orientation.

## Verification

Commands:

```bash
python3 -m py_compile \
  src/tase_repro/force_feedback.py \
  src/tase_repro/staged_force_motion.py \
  scripts/run_staged_orientation_force_motion.py
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_rate_cap_probe/20260524T094752/summary.yaml').read_text())
print(
    m['case_count'],
    m['cap_respected_count'],
    m['approach_terminal_budget_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `53 passed in 1.17s`
- `git diff --check` passed
- aggregate check printed `6 6 0 3 0`

## Limits

- This is E1-only tilted-plane simulation evidence.
- It tests a command cap, not a new task-priority solver.
- The contact surface is a single analytic plane, not a curved unknown surface.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
