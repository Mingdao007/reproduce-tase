# Long Approach Probe Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v26-long-approach-probe`

Starting commit: `2b2f515988ed1f703f26fbba73a850fa40780edd`

## Scope

Test whether the v25 Stage A failure can be reduced by using longer,
lower-gain weighted approaches before changing controller formulation. This
branch also includes a long `linear-primary` reference case.

This is simulation-only. It does not move or write settings to the real UR10e,
OnRobot, TCP, payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_long_approach_probe/20260524T094156`

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
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --angular-slack-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

Varied cases:

| case | approach priority | approach kp | approach duration s |
| --- | --- | ---: | ---: |
| `weighted_kp0p50_4s` | `weighted` | 0.50 | 4.0 |
| `weighted_kp0p35_6s` | `weighted` | 0.35 | 6.0 |
| `weighted_kp0p25_8s` | `weighted` | 0.25 | 8.0 |
| `weighted_kp0p15_12s` | `weighted` | 0.15 | 12.0 |
| `weighted_kp0p10_18s` | `weighted` | 0.10 | 18.0 |
| `linear_primary_kp0p50_18s` | `linear-primary` | 0.50 | 18.0 |

## Approach Budget

The ordinary approach feasibility gate includes `max_orientation_error_rad <=
0.03`, so it rejects every approach that starts from the known 10 degree
tilted-normal mismatch. To test whether a longer approach is at least a
reasonable prealignment maneuver, this report also records a terminal approach
budget:

```text
final_orientation_error_rad <= 0.03
contact_present_fraction >= 1.0
tail_mean_abs_force_error_N <= 0.25
max_tangential_position_error_m <= 0.002
max_planar_velocity_slack_m_s <= 0.001
max_abs_normal_velocity_slack_m_s <= 0.0002
qdot_saturation_fraction <= 0.01
tail_max_qdot_utilization <= 0.98
max_angular_velocity_slack_rad_s <= 0.03
```

## Result

Aggregate files:

- `runs/staged_orientation_long_approach_probe/20260524T094156/summary.md`
- `runs/staged_orientation_long_approach_probe/20260524T094156/summary.csv`
- `runs/staged_orientation_long_approach_probe/20260524T094156/summary.yaml`
- `runs/staged_orientation_long_approach_probe/20260524T094156/summary.json`

| case | duration s | kp | final orientation error rad | first <=0.03 s | qdot sat | planar drift m | angular slack rad/s | terminal budget | trajectory after approach |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_kp0p50_4s` | 4.0 | 0.50 | 0.0275192 | 3.778 | 0.6145 | 0.00501401 | 0.00317123 | `False` | `False` |
| `weighted_kp0p35_6s` | 6.0 | 0.35 | 0.0262618 | 5.470 | 0.6127 | 0.00514998 | 0.00287884 | `False` | `False` |
| `weighted_kp0p25_8s` | 8.0 | 0.25 | 0.0290636 | 7.810 | 0.5827 | 0.00480077 | 0.00254512 | `False` | `False` |
| `weighted_kp0p15_12s` | 12.0 | 0.15 | 0.0348579 | none | 0.5285 | 0.00410258 | 0.00198321 | `False` | `False` |
| `weighted_kp0p10_18s` | 18.0 | 0.10 | 0.0365550 | none | 0.5261 | 0.00390159 | 0.00196148 | `False` | `False` |
| `linear_primary_kp0p50_18s` | 18.0 | 0.50 | 0.0741633 | none | 0.9143 | 0.00000808 | 0.0376932 | `False` | `False` |

Counts:

- Approach terminal-orientation passes: `3 / 6`
- Approach terminal-budget passes: `0 / 6`
- Approach ordinary-feasibility passes: `0 / 6`
- Trajectory-after-approach passes: `0 / 6`
- Full staged-feasibility passes: `0 / 6`

## Interpretation

Longer lower-gain weighted approaches do not recover a clean Stage A. The
weighted cases can reduce angular slack and sometimes reach the terminal
orientation threshold, but qdot saturation remains between `0.5261111111111111`
and `0.6145`, with tail qdot utilization still at `1.0`. Planar drift also
remains above the `0.002 m` budget.

The long `linear-primary` reference preserves planar drift at
`8.083945131196271e-06 m`, but it stalls at `0.07416325057807228 rad`, so it
does not prealign the TCP to the tilted normal.

The following trajectory phase fails in all six cases. For the low-gain
weighted cases, the trajectory is still qdot-limited; for the lowest gains and
the linear-primary case, it also remains above the orientation threshold.

## Decision

Do not continue longer low-gain Stage A probes under the same controller. The
next step needs a controller change or a formally accepted relaxed approach
budget. The most direct simulation-only controller change is to add an
orientation-rate-limited approach schedule so Stage A can explicitly cap the
desired angular velocity while holding position and contact separately.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_long_approach_probe/20260524T094156/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_terminal_budget_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `51 passed in 1.15s`
- `git diff --check` passed
- aggregate check printed `6 0 0 0`

## Limits

- This is E1-only tilted-plane simulation evidence.
- It tests longer scalar gain schedules, not a new controller.
- The contact surface is a single analytic plane, not a curved unknown surface.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
