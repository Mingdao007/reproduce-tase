# Staged Approach Bracket Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v25-approach-bracket`

Starting commit: `0a686dcb4972b9c4292f414af41c3fbb97f544ca`

## Scope

Run a compact simulation-only bracket on the tilted-plane Stage A orientation
approach from v24. The goal is to test whether simple changes to approach
orientation gain, planar slack weight, angular slack weight, or priority mode
can reduce approach drift and sustained qdot saturation while still enabling
the following E1 trajectory phase.

This branch does not move or write settings to the real UR10e, OnRobot, TCP,
payload, URCap, or force sensor.

## Run

Run root:

- `runs/staged_orientation_approach_bracket/20260524T093536`

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
  --trajectory e1-cycloid \
  --omega-rad-s 0.1 \
  --paper-time-scale 0.075 \
  --planar-kp 0.5 \
  --normal-slack-weight 10000.0 \
  --slack-constraint-weight 1000.0 \
  --normal-velocity-mode contact-normal \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-orientation-kp 0.1 \
  --angular-axis-weight 1.0 \
  --approach-orientation-threshold-rad 0.03 \
  --max-orientation-error-rad 0.03 \
  --max-angular-slack-rad-s 0.03
```

Varied cases:

| case | approach priority | approach kp | planar slack weight | angular slack weight |
| --- | --- | ---: | ---: | ---: |
| `weighted_kp0p5_planar1_ang1` | `weighted` | 0.5 | 1.0 | 1.0 |
| `weighted_kp1p0_planar1_ang1` | `weighted` | 1.0 | 1.0 | 1.0 |
| `weighted_kp2p0_planar1_ang1` | `weighted` | 2.0 | 1.0 | 1.0 |
| `weighted_kp2p0_planar10_ang1` | `weighted` | 2.0 | 10.0 | 1.0 |
| `weighted_kp2p0_planar100_ang1` | `weighted` | 2.0 | 100.0 | 1.0 |
| `weighted_kp2p0_planar1_ang10` | `weighted` | 2.0 | 1.0 | 10.0 |
| `linear_primary_kp2p0_planar1_ang1` | `linear-primary` | 2.0 | 1.0 | 1.0 |

## Result

Aggregate files:

- `runs/staged_orientation_approach_bracket/20260524T093536/summary.md`
- `runs/staged_orientation_approach_bracket/20260524T093536/summary.csv`
- `runs/staged_orientation_approach_bracket/20260524T093536/summary.yaml`
- `runs/staged_orientation_approach_bracket/20260524T093536/summary.json`

| case | final orientation error rad | first <=0.03 s | approach qdot sat | planar drift m | angular slack rad/s | trajectory after approach | full staged pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `weighted_kp0p5_planar1_ang1` | 0.0275192 | 3.778 | 0.6145 | 0.00501401 | 0.00317123 | `False` | `False` |
| `weighted_kp1p0_planar1_ang1` | 0.00706716 | 1.862 | 0.9995 | 0.00765065 | 0.00538346 | `True` | `False` |
| `weighted_kp2p0_planar1_ang1` | 0.0020238 | 0.912 | 0.961 | 0.00973854 | 0.0608503 | `True` | `False` |
| `weighted_kp2p0_planar10_ang1` | 0.0149423 | 1.258 | 1.0 | 0.00658333 | 0.138029 | `False` | `False` |
| `weighted_kp2p0_planar100_ang1` | 0.0484506 | none | 1.0 | 0.00246083 | 0.158078 | `False` | `False` |
| `weighted_kp2p0_planar1_ang10` | 0.000261202 | 0.882 | 0.8875 | 0.0125303 | 0.00915376 | `True` | `False` |
| `linear_primary_kp2p0_planar1_ang1` | 0.0741477 | none | 1.0 | 0.0000095434 | 0.16336 | `False` | `False` |

Counts:

- Approach terminal-orientation passes: `5 / 7`
- Approach full-feasibility passes: `0 / 7`
- Trajectory-after-approach passes: `3 / 7`
- Full staged-feasibility passes: `0 / 7`

## Interpretation

The bracket did not find a simple slack or scalar gain setting that makes
Stage A a normal feasibility pass.

Lowering approach orientation gain reduces angular slack, but the `kp = 0.5`
case still has approach qdot saturation fraction `0.6145` and the following
trajectory fails qdot saturation. The `kp = 1.0` and `kp = 2.0` weighted cases
enable the trajectory phase, but their approach phases remain saturated for
almost the full approach.

Increasing planar slack weight to `10` or `100` does not produce a clean
approach. The `100` case reduces planar drift to `0.0024608283718913233 m`,
but it no longer reaches the `0.03 rad` terminal orientation threshold and
keeps qdot saturated for the full approach.

Increasing angular slack weight to `10` improves terminal orientation error
and lowers angular slack relative to the v24 baseline, but it increases planar
drift to `0.012530340042995497 m`, loses some contact samples in the approach,
and still has qdot saturation fraction `0.8875`.

The `linear-primary` approach preserves planar position best, but it stalls at
`0.07414766093770783 rad`, above the orientation threshold. That makes it a
negative reference for using the trajectory-phase priority mode as the
approach controller.

## Decision

Treat simple Stage A scalar and slack bracketing as exhausted for this tilted
setup. The next progress point should be one of:

- a redesigned approach controller with explicit position-hold and orientation
  scheduling under the velocity budget;
- a longer, lower-gain approach with a separate approach-specific gate and
  documented acceptance criteria;
- or an explicit decision that prealignment uses a relaxed qdot/contact/drift
  budget and is not part of the paper-trajectory feasibility claim.

## Verification

Commands:

```bash
scripts/run_tests.sh
git diff --check
python3 - <<'PY'
from pathlib import Path
import yaml
m = yaml.safe_load(Path('runs/staged_orientation_approach_bracket/20260524T093536/summary.yaml').read_text())
print(
    m['case_count'],
    m['approach_feasibility_pass_count'],
    m['trajectory_after_approach_pass_count'],
    m['full_staged_feasibility_pass_count'],
)
PY
```

Result:

- `51 passed in 1.13s`
- `git diff --check` passed
- aggregate check printed `7 0 3 0`

## Limits

- This is E1-only tilted-plane simulation evidence.
- The contact surface is a single analytic plane, not a curved unknown surface.
- The controller is kinematic velocity-level simulation, not the paper's
  torque-level finite-time RNN.
- The approximate UR10e MJCF and unverified 85 mm TCP remain simulation
  scaffolding.
