# Staged E1-E4 After Prealignment Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v29-staged-e1-e4-after-prealign`

Starting commit: `7045c23005cd9932e4b8bc6a9c2f57ff74fc11dc`

## Scope

Test whether the weighted tilted-normal prealignment that reaches the terminal
orientation gate can support the full Section VI E1-E4 trajectory family in
the following Stage B phase.

This is not an acceptance of the Stage A approach budget. Prior evidence shows
that this Stage A setup fails ordinary approach feasibility because it uses
sustained qdot saturation and about `8 mm` planar drift.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_e1e4_after_prealign/20260524T095804`

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
  --trajectory-orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

## Result

Aggregate files:

- `runs/staged_orientation_e1e4_after_prealign/20260524T095804/summary.md`
- `runs/staged_orientation_e1e4_after_prealign/20260524T095804/summary.csv`
- `runs/staged_orientation_e1e4_after_prealign/20260524T095804/summary.yaml`
- `runs/staged_orientation_e1e4_after_prealign/20260524T095804/summary.json`

Counts:

- Approach terminal-orientation passes: `4 / 4`
- Approach ordinary-feasibility passes: `0 / 4`
- Trajectory-after-approach passes: `3 / 4`
- Trajectory feasibility passes: `3 / 4`
- Full staged-feasibility passes: `0 / 4`

| trajectory | Stage B pass | failed criteria | force error N | max pos err m | max orient err rad | qdot saturation |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `e1-cycloid` | `True` | none | `0.0002608776054143602` | `2.323702463815581e-08` | `0.0020386821878491048` | `0.0005` |
| `e2-figure-eight` | `False` | qdot saturation, tail qdot utilization | `0.015191179672980932` | `2.0850437675500445e-05` | `0.020294558071100602` | `0.9935` |
| `e3-circle` | `True` | none | `0.00024053609321311064` | `7.491694364837392e-07` | `0.007108778321016299` | `0.0005` |
| `e4-cardioid` | `True` | none | `0.00024069599478070082` | `6.072721953184356e-07` | `0.0024109462623841393` | `0.0005` |

The repeated Stage A metrics are:

- final orientation error: `0.0020290714973557108 rad`
- first time below `0.03 rad`: `0.926 s`
- qdot saturation fraction: `1.0`
- max tangential drift: `0.008347977658392892 m`
- tail mean absolute force error: `0.003600515115319756 N`

## Interpretation

The positive part is limited but useful: after the relaxed weighted
prealignment, E1, E3, and E4 all pass the existing Stage B gates at the common
slow `paper_time_scale = 0.075`.

The negative part is more important for the reproduction claim. E2 still fails
the Stage B gate due qdot saturation (`0.9935`) and tail qdot utilization
(`1.0`) even though its force, position, orientation, and slack metrics are
inside the configured thresholds. The approach itself also fails ordinary
feasibility in every case.

Therefore this branch does not establish an E1-E4 staged tilted-plane
reproduction. It shows that prealignment removes the initial tilted-normal
orientation error for 3 of 4 slow trajectories, while E2 remains a
post-prealignment velocity-budget blocker.

## Decision

Do not accept relaxed-drift prealignment as the complete staged solution. Keep
the run as partial trajectory-after-prealignment evidence and treat E2 as the
next isolated blocker.

The next executable experiment should run a small E2 timing or task-priority
bracket after the same prealignment, or implement a genuinely different Stage
A task structure that avoids both planar drift and sustained qdot saturation.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_e1e4_after_prealign/20260524T095804/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `54 passed in 1.19s`
- `git diff --check` passed
- aggregate check printed `4 0 3 0`

## Limits

- This is tilted-plane simulation evidence only.
- Stage A is not accepted as an ordinary feasible motion.
- The passing Stage B cases use `paper_time_scale = 0.075`, not full paper
  timing.
- The contact surface is a single analytic plane, not a curved unknown
  surface.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
