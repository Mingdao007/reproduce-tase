# Approach Qdot Budget Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v28-approach-qdot-budget`

Starting commit: `f621584c6a3e90cf8ed55837d317ac9e4541e30b`

## Scope

Add and test separate hard qdot caps for the Stage A approach and Stage B
trajectory phases. This makes relaxed approach-budget probes explicit while
keeping the paper-trajectory phase at the existing `0.15 rad/s` cap.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Implementation

Updated files:

- `src/tase_repro/staged_force_motion.py`
- `scripts/run_staged_orientation_force_motion.py`
- `tests/test_staged_force_motion.py`

New API/CLI surface:

```text
simulate_orientation_prealign_then_planar_force_motion(
    ...,
    qdot_min=<approach lower bounds>,
    qdot_max=<approach upper bounds>,
    trajectory_qdot_min=<optional trajectory lower bounds>,
    trajectory_qdot_max=<optional trajectory upper bounds>,
)
scripts/run_staged_orientation_force_motion.py \
  --approach-qdot-limit-rad-s <rad/s> \
  --trajectory-qdot-limit-rad-s <rad/s>
```

If the new trajectory limits are omitted, Stage B uses the existing shared
limits. Each phase records its own qdot limit source and bound arrays.

## Run

Run root:

- `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305`

Common runner:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --approach-duration-s 4.0 \
  --trajectory-duration-s 2.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --qdot-limit-rad-s 0.15 \
  --trajectory-qdot-limit-rad-s 0.15 \
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

| case | approach priority | approach qdot cap rad/s | trajectory qdot cap rad/s |
| --- | --- | ---: | ---: |
| `weighted_a0p15_t0p15_kp2_4s` | `weighted` | 0.15 | 0.15 |
| `weighted_a0p25_t0p15_kp2_4s` | `weighted` | 0.25 | 0.15 |
| `weighted_a0p35_t0p15_kp2_4s` | `weighted` | 0.35 | 0.15 |
| `weighted_a0p50_t0p15_kp2_4s` | `weighted` | 0.50 | 0.15 |
| `linear_primary_a0p25_t0p15_kp2_4s` | `linear-primary` | 0.25 | 0.15 |
| `linear_primary_a0p35_t0p15_kp2_4s` | `linear-primary` | 0.35 | 0.15 |
| `linear_primary_a0p50_t0p15_kp2_4s` | `linear-primary` | 0.50 | 0.15 |

## Result

Aggregate files:

- `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/summary.md`
- `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/summary.csv`
- `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/summary.yaml`
- `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/summary.json`

| case | final orientation error rad | first <=0.03 s | approach qdot sat | max qdot rad/s | planar drift m | trajectory after approach | full staged pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_a0p15_t0p15_kp2_4s` | 0.0020238 | 0.912 | 0.961 | 0.15 | 0.00973854 | `True` | `False` |
| `weighted_a0p25_t0p15_kp2_4s` | 0.00202907 | 0.926 | 1.0 | 0.25 | 0.00834798 | `True` | `False` |
| `weighted_a0p35_t0p15_kp2_4s` | 0.0020275 | 0.926 | 0.932 | 0.35 | 0.00834736 | `True` | `False` |
| `weighted_a0p50_t0p15_kp2_4s` | 0.00201843 | 0.926 | 0.908 | 0.50 | 0.00834505 | `False` | `False` |
| `linear_primary_a0p25_t0p15_kp2_4s` | 0.0741399 | none | 1.0 | 0.25 | 0.000011013 | `False` | `False` |
| `linear_primary_a0p35_t0p15_kp2_4s` | 0.0740139 | none | 0.924 | 0.35 | 0.000015885 | `False` | `False` |
| `linear_primary_a0p50_t0p15_kp2_4s` | 0.0738197 | none | 0.908 | 0.50 | 0.000030353 | `False` | `False` |

Counts:

- Approach terminal-orientation passes: `4 / 7`
- Approach terminal-budget passes: `0 / 7`
- Approach ordinary-feasibility passes: `0 / 7`
- Trajectory-after-approach passes: `3 / 7`
- Full staged-feasibility passes: `0 / 7`

## Interpretation

Separate Stage A/Stage B qdot caps work mechanically and keep the trajectory
phase at `0.15 rad/s`.

Relaxing only the Stage A qdot cap does not solve the approach. Weighted
approaches still ride the relaxed cap for most of the approach and keep planar
drift around `8 mm`. Higher weighted approach caps do not improve terminal
alignment materially, and the `0.50 rad/s` weighted case no longer preserves a
passing Stage B trajectory.

The `linear-primary` cases preserve planar position, but they still stall near
`0.074 rad` and do not reach the terminal orientation threshold even with a
`0.50 rad/s` Stage A cap.

## Decision

Keep separate Stage A/Stage B qdot-limit support because it makes budget
experiments explicit. Do not treat relaxed Stage A qdot alone as an accepted
prealignment budget. The evidence still points to a task-structure issue:
weighted mode aligns by allowing drift, while `linear-primary` preserves
position but lacks enough feasible orientation authority.

The next progress point should be either a real position/contact-first
approach formulation with a controlled orientation secondary objective, or a
decision record that accepts a relaxed-drift prealignment phase as separate
from paper-trajectory feasibility.

## Verification

Commands:

```bash
python3 -m py_compile \
  src/tase_repro/staged_force_motion.py \
  scripts/run_staged_orientation_force_motion.py
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_terminal_budget_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `54 passed in 1.19s`
- `git diff --check` passed
- aggregate check printed `7 0 3 0`

## Limits

- This is E1-only tilted-plane simulation evidence.
- It tests qdot budgets, not a new task-priority solver.
- The contact surface is a single analytic plane, not a curved unknown surface.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
