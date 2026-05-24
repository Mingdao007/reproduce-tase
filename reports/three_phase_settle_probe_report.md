# Three-Phase Setup Settle Probe Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v36-three-phase-setup-settle`

## Scope

This iteration tests a planned Stage A sequence after the v35 two-phase
recenter failure:

1. weighted force-normal prealignment
2. linear-primary recentering toward the original setup x/y reference
3. optional settle phase that targets the same x/y reference while restoring
   force-normal orientation before the E2 Stage B trajectory

The work is simulation-only. No real robot motion, hardware writes, TCP
writes, payload writes, URCap writes, or OnRobot setting changes were
performed.

## Artifacts

- Run root:
  `runs/staged_orientation_three_phase_settle/20260524T110039`
- Aggregate files:
  - `summary.yaml`
  - `summary.md`
- Per-case files:
  - root `metrics.yaml`, `metrics.json`, `summary.md`, `git_state.md`
  - phase `metrics.yaml`, `metrics.json`, force, x/y, orientation, and
    angular-slack plots for `approach`, optional `approach_recenter`,
    optional `approach_settle`, and `trajectory`

Raw per-phase `.npz` arrays are generated for local inspection but remain
ignored by Git.

## Common Setup

All cases use the tilted-plane MuJoCo setup with:

```text
initial_q = [0, -0.1, 0.15, -0.05, 0, 0]
base_z_offset_m = -0.0011631221220595766
approach qdot cap = 0.25 rad/s
recenter qdot cap = 0.15 rad/s
settle qdot cap = 0.15 rad/s
trajectory qdot cap = 0.15 rad/s
trajectory = E2 figure-eight
trajectory duration = 8 s
paper_time_scale = 0.075
trajectory posture target = [0, -0.1, 0.15, -0.05, 0, 0]
trajectory posture kp = 1.0
trajectory posture weight = 0.001
trajectory max posture velocity = 0.05 rad/s
setup final x/y gate = 0.002 m
setup final orientation gate = 0.03 rad
```

The matrix was generated with:

```bash
python3 - <<'PY' ... three-phase settle matrix and summary aggregation ... PY
```

Each case calls:

```bash
python3 scripts/run_staged_orientation_force_motion.py \
  --config configs/mujoco_ur10e_tilted_plane.yaml \
  --approach-duration-s 4.0 \
  --recenter-duration-s <case duration> \
  --settle-duration-s <case duration> \
  --trajectory-duration-s 8.0 \
  --approach-qdot-limit-rad-s 0.25 \
  --recenter-qdot-limit-rad-s 0.15 \
  --settle-qdot-limit-rad-s 0.15 \
  --trajectory-qdot-limit-rad-s 0.15 \
  --trajectory e2-figure-eight \
  --paper-time-scale 0.075 \
  --approach-orientation-priority-mode weighted \
  --recenter-orientation-priority-mode linear-primary \
  --settle-orientation-priority-mode <weighted|linear-primary> \
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
- Trajectory feasibility passes: `8 / 10`
- Legacy trajectory-after-approach passes: `8 / 10`
- Planned setup-then-trajectory passes: `0 / 10`
- Full staged-feasibility passes: `0 / 10`

| case | setup failed | setup orient | setup x/y err m | settle force err N | traj pass | traj orient |
|---|---|---:|---:|---:|---:|---:|
| `baseline_no_recenter` | `final_tangential_position_error_m` | `0.0020290714973557108` | `0.008347977658392892` | `None` | `True` | `0.0203545748607252` |
| `lp4_no_settle` | `final_orientation_error_rad` | `0.06144921366675186` | `0.001202027969075075` | `None` | `False` | `0.08828833304324712` |
| `lp1_settle_w0p5` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.011139549031039307` | `0.007193845624799021` | `0.8225791490908131` | `True` | `0.02939550767657929` |
| `lp1_settle_w1` | `final_tangential_position_error_m` | `0.005558417503337856` | `0.007869579772205084` | `0.1393121211793803` | `True` | `0.02403096466832988` |
| `lp1_settle_w2` | `final_tangential_position_error_m` | `0.0025125657280091578` | `0.00828135120454356` | `0.003310079622609865` | `True` | `0.020860331353265302` |
| `lp2_settle_w1` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.008147569423222185` | `0.007543673110517419` | `0.4460386510159919` | `True` | `0.02659356165501424` |
| `lp2_settle_w2` | `final_tangential_position_error_m` | `0.002914947767721797` | `0.008224360494180138` | `0.010563335509174326` | `True` | `0.021294571846744433` |
| `lp4_settle_w1` | `final_tangential_position_error_m;tail_mean_abs_force_error_N` | `0.010909888730768584` | `0.00721962222129202` | `0.9675117552611987` | `True` | `0.02918723865860162` |
| `lp4_settle_w2` | `final_tangential_position_error_m` | `0.0033403693502681454` | `0.008165765238665546` | `0.026269070988793494` | `True` | `0.02174260279275125` |
| `lp4_settle_lp4` | `final_orientation_error_rad` | `0.07228244179626259` | `0.00017396214319096055` | `0.0019523730245144177` | `False` | `0.10197948276546515` |

## Interpretation

The settle phase closes one side of the v35 tradeoff but reopens the other.
Weighted settling restores terminal orientation and force well enough for the
following E2 trajectory in most cases, but it gives back almost all x/y
recenter progress: final setup x/y error returns to about `7.2-8.3 mm`.

The linear-primary settle reference keeps x/y error very small
(`0.00017396214319096055 m` in the `lp4_settle_lp4` row), but terminal
orientation rises to `0.07228244179626259 rad`, and the following E2 trajectory
fails orientation. This is the same structural conflict as v34 and v35, now
shown across an explicit align -> recenter -> settle plan.

The legacy trajectory-after-approach count improves to `8 / 10`, but that
metric only confirms that the final orientation and Stage B gates can be made
compatible when setup drift is allowed. The stricter planned setup gate remains
the deciding metric, and it passes `0 / 10`.

## Conclusion

The three-phase settle path is not an accepted Stage A solution. The current
velocity-level task formulation cannot simultaneously satisfy the terminal
setup x/y, force/contact, orientation, and full staged gates for the tested E2
tilted-plane setup.

The next useful step is not another scalar phase-duration bracket. The project
should either:

- define and decision-record a relaxed setup budget that explicitly accepts the
  current weighted-prealignment drift as a setup maneuver outside
  paper-equivalent full feasibility; or
- change the mathematical Stage A formulation beyond instantaneous weighted or
  two-level velocity allocation.

## Verification

- `python3 -m py_compile src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
- `scripts/run_tests.sh` -> `64 passed in 1.38s`
