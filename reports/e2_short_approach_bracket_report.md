# E2 Short Approach Bracket Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v31-e2-short-approach-bracket`

Starting commit: `63a7910bd10d43e55ed2ecf05137745f8245e53f`

## Scope

Test whether E2 improves if the weighted Stage A prealignment stops close to
the first tilted-normal orientation threshold crossing instead of running for
the fixed `4 s` used in v29 and v30.

The tested Stage A durations are `0.94`, `1.00`, `1.20`, `2.00`, and `4.00 s`.
Stage B stays fixed to the v29 E2 condition:

- `paper_time_scale = 0.075`
- `trajectory_orientation_kp = 0.10`
- `trajectory_qdot_limit_rad_s = 0.15`

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_e2_short_approach_bracket/20260524T101113`

Common runner:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --approach-duration-s <0.94|1.00|1.20|2.00|4.00> \
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

## Result

Aggregate files:

- `runs/staged_orientation_e2_short_approach_bracket/20260524T101113/summary.md`
- `runs/staged_orientation_e2_short_approach_bracket/20260524T101113/summary.csv`
- `runs/staged_orientation_e2_short_approach_bracket/20260524T101113/summary.yaml`
- `runs/staged_orientation_e2_short_approach_bracket/20260524T101113/summary.json`

Counts:

- Approach terminal-orientation passes: `5 / 5`
- Approach ordinary-feasibility passes: `0 / 5`
- Trajectory-after-approach passes: `0 / 5`
- Trajectory feasibility passes: `0 / 5`
- Full staged-feasibility passes: `0 / 5`

| case | approach s | approach orient err | approach drift m | E2 failed criteria | E2 orient err | E2 qdot sat |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| `approach0p94` | 0.94 | `0.029326677012512806` | `0.005511250096345505` | qdot saturation, tail qdot utilization, orientation, angular slack | `0.04359451698383457` | `0.94175` |
| `approach1p00` | 1.00 | `0.026344676181529823` | `0.005757642179203222` | qdot saturation, tail qdot utilization, orientation, angular slack | `0.04142406189804967` | `0.94925` |
| `approach1p20` | 1.20 | `0.01856973738776605` | `0.006423414172320667` | qdot saturation, tail qdot utilization, orientation | `0.035706552138982606` | `0.9555` |
| `approach2p00` | 2.00 | `0.0056419034973640815` | `0.00785568116254086` | qdot saturation, tail qdot utilization | `0.024082964025574225` | `0.99775` |
| `approach4p00` | 4.00 | `0.0020290714973557108` | `0.008347977658392892` | qdot saturation, tail qdot utilization | `0.020294558071100602` | `0.9935` |

## Interpretation

Stopping near the first orientation threshold crossing reduces Stage A planar
drift from about `8.35 mm` to about `5.51-5.76 mm`, but the following E2
trajectory no longer satisfies the orientation and angular-slack gates.

Letting the approach run longer improves the E2 orientation gate, but it does
not reduce qdot saturation. At `2 s` and `4 s`, E2 fails only qdot saturation
and tail qdot utilization, with saturation fractions `0.99775` and `0.9935`.

The E2 blocker is therefore not solved by simply stopping Stage A at the first
orientation threshold. The tradeoff is now explicit: shorter approach helps
drift but leaves insufficient orientation margin for E2, while longer approach
aligns orientation but leaves the E2 tangent-direction velocity budget
saturated.

## Decision

Do not treat threshold-duration Stage A stopping as the E2 fix. The next
useful step should change the terminal configuration more directly, for
example by adding a posture objective during or after prealignment, or by
testing a different tangent allocation for E2.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
git diff --cached --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_e2_short_approach_bracket/20260524T101113/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `54 passed in 1.20s`
- `git diff --check` passed
- aggregate check printed `5 0 0 0`

## Limits

- This is E2-only tilted-plane simulation evidence.
- Stage A remains infeasible under the ordinary approach budget.
- It does not implement a new posture objective or new QP task structure.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
