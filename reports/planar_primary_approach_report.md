# Planar-Primary Approach Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v34-planar-primary-approach`

Starting commit: `9973dd16cfb445487c02d843854e40fb3892af42`

## Scope

Add and test a simulation-only Stage A controller structure that preserves
planar x/y TCP velocity as the primary task, then optimizes contact-normal
force velocity and force-normal orientation as secondary tasks under the same
hard joint and velocity bounds.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Implementation

Updated files:

- `src/tase_repro/constraints.py`
- `src/tase_repro/controller.py`
- `src/tase_repro/force_feedback.py`
- `scripts/run_staged_orientation_force_motion.py`
- `tests/test_constraints.py`
- `tests/test_controller.py`
- `tests/test_force_motion.py`

New API/CLI surface:

```text
CartesianVelocityCommand(..., angular_priority_mode="planar_primary")
simulate_planar_force_motion(..., orientation_priority_mode="planar_primary")
scripts/run_staged_orientation_force_motion.py \
  --approach-orientation-priority-mode planar-primary
```

The new solver helper preserves primary rows:

```text
primary_A qdot = primary_A qdot_primary
```

and minimizes weighted secondary residuals plus damping under the same hard
velocity and one-step joint bounds.

## Runs

Primary run root:

- `runs/staged_orientation_planar_primary_approach/20260524T103539`

Normal-weight follow-up root:

- `runs/staged_orientation_planar_primary_normal_weight/20260524T103646`

Common runner shape:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --trajectory-duration-s 2.0 \
  --target-force-N 5.0 \
  --force-gain 5e-4 \
  --r 0.5 \
  --base-z-offset-m=-0.0011631221220595766 \
  --initial-q 0,-0.1,0.15,-0.05,0,0 \
  --trajectory-qdot-limit-rad-s 0.15 \
  --trajectory e1-cycloid \
  --omega-rad-s 0.1 \
  --paper-time-scale 0.075 \
  --planar-kp 0.5 \
  --planar-slack-weight 1.0 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --approach-orientation-priority-mode planar-primary \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp 0.10 \
  --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 \
  --trajectory-posture-kp 1.0 \
  --trajectory-posture-weight 0.001 \
  --trajectory-max-posture-velocity-rad-s 0.05 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

## Primary Result

Aggregate files:

- `runs/staged_orientation_planar_primary_approach/20260524T103539/summary.md`
- `runs/staged_orientation_planar_primary_approach/20260524T103539/summary.csv`
- `runs/staged_orientation_planar_primary_approach/20260524T103539/summary.yaml`
- `runs/staged_orientation_planar_primary_approach/20260524T103539/summary.json`

Counts:

- Approach terminal-orientation passes: `6 / 6`
- Approach terminal-budget passes: `0 / 6`
- Approach ordinary-feasibility passes: `0 / 6`
- Trajectory-after-approach passes: `1 / 6`
- Full staged-feasibility passes: `0 / 6`

| case | terminal budget failed | final orient | qdot sat | drift m | planar slack | force err N | trajectory after |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `weighted_ref_kp2_a0p25_4s` | drift, planar slack, qdot saturation, tail qdot utilization | `0.0020290714973557108` | `1.0` | `0.008347977658392892` | `0.019029396767311284` | `0.003600515115319756` | `True` |
| `planar_primary_kp2_a0p25_4s` | contact, force, normal slack, qdot saturation, tail qdot utilization | `7.570584319181321e-05` | `0.185` | `1.5446522353872519e-06` | `8.19003835426546e-11` | `5.0` | `False` |
| `planar_primary_kp2_a0p35_4s` | contact, force, normal slack, qdot saturation | `7.565716621433935e-05` | `0.0715` | `2.063170116845328e-05` | `1.2117730267564345e-10` | `5.0` | `False` |
| `planar_primary_kp2_a0p50_4s` | contact, force, normal slack, qdot saturation | `7.565056974434516e-05` | `0.029` | `2.025056658426158e-05` | `1.2193143147714868e-10` | `5.0` | `False` |
| `planar_primary_kp1_a0p25_8s` | contact, force, normal slack, qdot saturation | `9.379294441211913e-05` | `0.03975` | `2.807367009237914e-05` | `1.1939196704305498e-10` | `5.0` | `False` |
| `planar_primary_kp2_cap0p05_a0p25_8s` | contact, force, normal slack, qdot saturation, tail qdot utilization | `1.8807622454296194e-05` | `0.02925` | `2.789035007869957e-05` | `1.188966914560247e-10` | `5.0` | `False` |

## Normal-Weight Follow-Up Result

Aggregate files:

- `runs/staged_orientation_planar_primary_normal_weight/20260524T103646/summary.md`
- `runs/staged_orientation_planar_primary_normal_weight/20260524T103646/summary.csv`
- `runs/staged_orientation_planar_primary_normal_weight/20260524T103646/summary.yaml`
- `runs/staged_orientation_planar_primary_normal_weight/20260524T103646/summary.json`

Counts:

- Approach terminal-orientation passes: `1 / 5`
- Approach terminal-budget passes: `0 / 5`
- Approach ordinary-feasibility passes: `0 / 5`
- Trajectory-after-approach passes: `0 / 5`
- Full staged-feasibility passes: `0 / 5`

| case | terminal budget failed | final orient | qdot sat | drift m | normal slack | force err N |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `pp_kp2_a0p35_n10_4s` | contact, force, normal slack, qdot saturation, tail qdot utilization | `0.0017768432101110674` | `0.9235` | `1.9531942401696326e-05` | `0.0034414195124211782` | `5.0` |
| `pp_kp2_a0p35_n100_4s` | terminal orientation, force, normal slack, qdot saturation, tail qdot utilization, angular slack | `0.06864583059182422` | `0.923` | `0.000211221375408294` | `0.0007202393756496103` | `2.1082523243052753` |
| `pp_kp2_a0p35_n1000_4s` | terminal orientation, qdot saturation, tail qdot utilization, angular slack | `0.07398431554093947` | `0.924` | `1.818489728897324e-05` | `7.932092216135997e-06` | `0.009879165281529831` |
| `pp_kp2_a0p50_n100_4s` | terminal orientation, force, normal slack, qdot saturation, tail qdot utilization, angular slack | `0.0684460435312527` | `0.908` | `0.00021667148066177415` | `0.0007172576372811926` | `2.20126388185431` |
| `pp_kp1_a0p35_n100_8s` | terminal orientation, force, normal slack, qdot saturation, tail qdot utilization, angular slack | `0.07151974250780353` | `0.90075` | `0.00014456150912877525` | `0.0003860123894250379` | `0.7095111442795621` |

## Interpretation

Planar-primary priority removes the large planar drift problem. The first
bracket keeps x/y drift below `3e-5 m` and planar velocity slack near zero in
the planar-primary rows.

That improvement is not a Stage A fix. With the default normal secondary
weight, planar-primary alignment loses contact and force tracking. Increasing
normal secondary weight restores force quality only by returning to the same
orientation stall seen in earlier linear-primary runs, around `0.07 rad`.
Sustained qdot saturation also remains above the terminal budget in every
normal-weight follow-up case.

The result narrows the Stage A conflict: planar drift can be controlled, but
the 6DOF arm cannot simultaneously satisfy planar hold, contact-normal force,
tilted-normal orientation, and the current qdot saturation gate with this
two-level planar-primary formulation.

## Decision

Keep `planar-primary` as a useful diagnostic controller mode, but do not use
it as the accepted Stage A approach solution. The next Stage A work should
either formulate an explicit relaxed approach budget, or move beyond
two-level weighted velocity priority to a planned prealignment path with
separate contact-maintenance and terminal-state gates.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
git diff --cached --check
python3 - <<'PY'
from pathlib import Path
import yaml
for p in [
    Path('runs/staged_orientation_planar_primary_approach/20260524T103539/summary.yaml'),
    Path('runs/staged_orientation_planar_primary_normal_weight/20260524T103646/summary.yaml'),
]:
    m = yaml.safe_load(p.read_text())
    print(
        m['case_count'],
        m['approach_terminal_budget_pass_count'],
        m['trajectory_after_approach_pass_count'],
        m['full_staged_feasibility_pass_count'],
    )
PY
```

Result:

- `61 passed in 1.26s`
- `git diff --check` passed
- aggregate checks printed `6 0 1 0` and `5 0 0 0`

## Limits

- This is E1-only tilted-plane simulation evidence for Stage A structure.
- It does not test curved unknown surfaces.
- It does not change the force source, TCP, contact model, or hardware state.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
