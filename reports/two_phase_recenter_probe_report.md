# Two-Phase Recenter Probe Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v35-two-phase-approach-recenter`

## Scope

This iteration tests whether a planned second setup phase can repair the
weighted approach drift before the posture-regularized E2 Stage B trajectory.
It remains simulation-only. No real robot motion, hardware writes, TCP writes,
payload writes, URCap writes, or OnRobot setting changes were performed.

The v35 runner adds two setup distinctions:

- Stage A1: the previous weighted force-normal prealignment.
- Stage A2: an optional recenter phase that starts from A1 terminal `q` and
  targets the original approach x/y reference through
  `planar_reference_xy_m`.

The report uses a stricter planned setup gate separate from the legacy
trajectory-after-approach gate. The setup terminal-state gate requires:

- final force-normal orientation error `<= 0.03 rad`
- final x/y error to the original setup reference `<= 0.002 m`
- contact-present fraction `>= 1.0`
- tail mean absolute force error `<= 0.25 N`
- no hard qdot or joint-limit violations

Qdot saturation remains part of ordinary phase feasibility and full staged
feasibility; it is not hidden by the terminal-state gate.

## Artifacts

- Run root:
  `runs/staged_orientation_two_phase_recenter/20260524T104957`
- Aggregate files:
  - `summary.yaml`
  - `summary.md`
- Per-case files:
  - root `metrics.yaml`, `metrics.json`, `summary.md`, `git_state.md`
  - phase `metrics.yaml`, `metrics.json`, force, x/y, orientation, and
    angular-slack plots for `approach`, optional `approach_recenter`, and
    `trajectory`

Raw per-phase `.npz` arrays are generated for local inspection but remain
ignored by Git.

## Common Setup

All cases use the tilted-plane MuJoCo setup with:

```text
initial_q = [0, -0.1, 0.15, -0.05, 0, 0]
base_z_offset_m = -0.0011631221220595766
approach qdot cap = 0.25 rad/s
recenter qdot cap = 0.15 rad/s
trajectory qdot cap = 0.15 rad/s
trajectory = E2 figure-eight
trajectory duration = 8 s
paper_time_scale = 0.075
trajectory posture target = [0, -0.1, 0.15, -0.05, 0, 0]
trajectory posture kp = 1.0
trajectory posture weight = 0.001
trajectory max posture velocity = 0.05 rad/s
```

The matrix was generated with:

```bash
python3 - <<'PY' ... two-phase recenter matrix and summary aggregation ... PY
```

Each case calls:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --approach-duration-s 4.0 \
  --recenter-duration-s <case duration> \
  --trajectory-duration-s 8.0 \
  --approach-qdot-limit-rad-s 0.25 \
  --recenter-qdot-limit-rad-s 0.15 \
  --trajectory-qdot-limit-rad-s 0.15 \
  --trajectory e2-figure-eight \
  --paper-time-scale 0.075 \
  --approach-orientation-priority-mode weighted \
  --recenter-orientation-priority-mode <weighted|linear-primary|planar-primary> \
  --trajectory-orientation-priority-mode linear-primary \
  --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 \
  --trajectory-posture-kp 1.0 \
  --trajectory-posture-weight 0.001 \
  --trajectory-max-posture-velocity-rad-s 0.05 \
  --setup-max-final-tangential-error-m 0.002
```

## Aggregate Result

- Cases: `10`
- Setup terminal-state passes: `0 / 10`
- Trajectory feasibility passes: `4 / 10`
- Legacy trajectory-after-approach passes: `4 / 10`
- Planned setup-then-trajectory passes: `0 / 10`
- Full staged-feasibility passes: `0 / 10`

| case | setup failed | setup orient | setup x/y err m | recenter force err N | traj pass | traj orient |
|---|---|---:|---:|---:|---:|---:|
| `baseline_no_recenter` | `final_tangential_position_error_m` | `0.0020290714973557108` | `0.008347977658392892` | `None` | `True` | `0.0203545748607252` |
| `weighted_recenter_4s` | `final_tangential_position_error_m` | `0.0019417654495737476` | `0.008360473956959848` | `0.0018400756047352229` | `True` | `0.02025995207705162` |
| `lp_recenter_0p2s` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.006039879488210821` | `0.007569057342219271` | `1.400552924999047` | `True` | `0.02639072763347245` |
| `lp_recenter_0p3s` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.00853105574687911` | `0.0072102171132026795` | `1.55001710834636` | `True` | `0.0292611395207697` |
| `lp_recenter_0p4s` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.01106774413292786` | `0.006869050548521516` | `1.5740320031502257` | `False` | `0.032042070707147687` |
| `lp_recenter_1s` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.025158611518183098` | `0.005138335667478752` | `1.0513662147686107` | `False` | `0.04697943449746931` |
| `lp_recenter_2s` | `final_orientation_error_rad;final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.042531446608710555` | `0.003166655425799055` | `0.41587533900905554` | `False` | `0.06605196016208538` |
| `lp_recenter_4s` | `final_orientation_error_rad` | `0.06144921366675186` | `0.001202027969075075` | `0.07268453631886647` | `False` | `0.08828833304324712` |
| `lp_recenter_4s_pkp0p2` | `final_orientation_error_rad;final_tangential_position_error_m` | `0.036920046275825014` | `0.0038469273903788785` | `0.09516531574555645` | `False` | `0.059178088812845336` |
| `pp_recenter_1s` | `final_tangential_position_error_m;contact_present_fraction;tail_mean_abs_force_error_N` | `0.0002897152712036141` | `0.005069982952668492` | `5.0` | `False` | `0.047597452958071426` |

## Interpretation

The no-recenter baseline and the weighted recenter case keep the Stage B E2
trajectory passing, but they leave the setup x/y error at about `8.35 mm`.
Weighted recentering therefore behaves like another orientation/force hold,
not a useful recenter operation.

Short linear-primary recenter windows (`0.2-0.3 s`) reduce x/y error modestly
to `7.57-7.21 mm` and still allow the E2 trajectory to pass. They are not
acceptable setup phases because the recenter tail force error is
`1.40-1.55 N`, well above the `0.25 N` gate.

Longer linear-primary recenter windows reduce x/y error further. The `4 s`
case reaches `0.001202027969075075 m`, which satisfies the final x/y gate and
keeps tail force error at `0.07268453631886647 N`, but the final setup
orientation error rises to `0.06144921366675186 rad`. The following E2
trajectory then fails the orientation gate.

The planar-primary recenter case preserves orientation, but it loses contact
and force and still leaves `5.07 mm` x/y error. This matches the v34 finding:
prioritizing tangent position without a better normal/contact formulation does
not produce an accepted Stage A setup.

## Conclusion

The two-phase recenter hook is useful diagnostically, but the tested planned
prealignment path is not an accepted Stage A solution. The conflict has moved
from "can we recenter?" to "can recentering preserve force, contact, and
terminal orientation at the same time?"

The next Stage A path should not continue scalar recenter-duration tuning.
Useful next options are:

- add a genuinely force-maintaining recenter formulation with phase-specific
  normal/force authority and the same setup terminal-state gate; or
- explicitly define a relaxed setup budget that accepts the current weighted
  prealignment drift, while keeping it separate from paper-equivalent full
  feasibility.

## Verification

- `python3 -m py_compile src/tase_repro/force_feedback.py src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
- `scripts/run_tests.sh` -> `63 passed in 1.31s`
