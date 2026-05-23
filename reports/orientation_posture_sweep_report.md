# Orientation-Gated Posture Sweep Report

Date: 2026-05-24

Branch: `exp/tase-ur10e-v17-orientation-posture-sweep`

## Scope

This iteration tests whether small simulation-only UR10e initial-posture
changes can recover full-speed E2/E3 feasibility once the v16 orientation gates
are enforced. It also hardens the posture sweep driver so postures that cannot
be calibrated to the target initial contact force are recorded as negative
evidence instead of aborting the whole run.

This remains simulation-only MuJoCo evidence and does not authorize real UR10e
motion.

## Driver Changes

- `scripts/run_posture_feasibility_sweep.py` now accepts the same
  orientation-hold and orientation-gate arguments used by the timing sweep.
- Per-posture calibration failures are written to `summary.json`,
  `summary.yaml`, and `summary.md`, then skipped so later postures can still
  run.
- `tests/test_posture_feasibility_sweep.py` covers the Markdown calibration
  failure reporting path.

## Gates

The v12 force-motion gates are retained and the v16 orientation gates are
enabled:

- max orientation error `<= 0.03 rad`
- max angular velocity slack `<= 0.03 rad/s`

Common run settings:

- trajectories: E2 figure-eight and E3 circle
- `--time-scales 1.0`
- `--qdot-limit-rad-s 0.15`
- `--force-gain 5e-4`
- `--orientation-mode hold`
- `--orientation-kp 1.0`
- `--max-orientation-error-rad 0.03`
- `--max-angular-slack-rad-s 0.03`

## Runs

- `runs/orientation_posture_sweep/20260524T024358`: first attempt, aborted at
  the first uncalibratable larger posture; retained with `ABORTED.md`.
- `runs/orientation_posture_sweep/20260524T041329_calibration_safe`: rerun
  with calibration failures recorded and `--angular-slack-weight 0.1`.
- `runs/orientation_posture_sweep/20260524T041329_weight_0p03`: focused
  angular-priority bracket at `0.03`.
- `runs/orientation_posture_sweep/20260524T041329_weight_0p01`: focused
  angular-priority bracket at `0.01`.
- `runs/orientation_posture_sweep/20260524T041329_weight_0p003`: focused
  angular-priority bracket at `0.003`.

## Calibration Result

| posture | calibration pass | base z offset m | initial force N | note |
| --- | --- | ---: | ---: | --- |
| `bend_0p10` | `True` | `-0.0009710693359375` | `4.995281922830507` | v14/v16 baseline |
| `bend_0p125` | `True` | `-0.0014990234375000001` | `5.005930952900419` | no material improvement |
| `bend_0p15` | `False` | n/a | n/a | best force `0 N` in the default bracket |
| `bend_0p20` | `False` | n/a | n/a | best force `10.404 N` in the default bracket |

## Full-Speed Posture Result

With angular slack weight `0.1`, both calibrated postures satisfy the
orientation gates for E2/E3, but fail the planar force-motion gates at full
paper speed:

| posture | trajectory | pass | failed criteria | max pos err m | max planar slack m/s | max orient err rad | max angular slack rad/s |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `bend_0p10` | E2 | `False` | planar position, planar slack | `0.007298434567067694` | `0.003929059585831822` | `0.010260627469780797` | `0.010467138725926963` |
| `bend_0p10` | E3 | `False` | planar position, planar slack | `0.015476725649078916` | `0.009324376968676102` | `0.022792200960046364` | `0.024703715417836912` |
| `bend_0p125` | E2 | `False` | planar position, planar slack | `0.007286412725588208` | `0.003922910008048283` | `0.010270627122803135` | `0.01047734112092219` |
| `bend_0p125` | E3 | `False` | planar position, planar slack | `0.015470348110780442` | `0.00932163031725057` | `0.02280085805300149` | `0.024712402242088063` |

The posture change from `bend_0p10` to `bend_0p125` does not meaningfully
reduce the limiting E3 planar error or slack.

## Angular Priority Bracket

The additional bracket checks whether an intermediate angular slack weight can
simultaneously satisfy the planar and orientation gates at full speed:

| angular slack weight | outcome at full-speed E2/E3 |
| ---: | --- |
| `0.1` | orientation gates pass, planar position/slack fail |
| `0.03` | planar still fails; E3 also fails both orientation gates |
| `0.01` | planar still fails; E3 fails both orientation gates |
| `0.003` | planar gates pass for E2/E3, but both trajectories fail orientation gates |

No tested posture/weight pair passes the combined full-speed E2/E3 gate set.
Because E2/E3 remain the binding trajectories, no E1/E4 full-speed confirmation
matrix was run in this iteration.

## Interpretation

The v17 evidence rejects the simplest full-speed recovery path: small extra
posture bend plus angular-priority tuning is not enough for the current
velocity-level 6DOF UR10e controller to satisfy force, planar tracking,
velocity limits, and initial-orientation hold at the paper's full timing. The
v16 common `paper_time_scale = 0.075` matrix remains the current
orientation-gated simulation fallback.

The next controller work should be a true task-priority or null-space-aware
formulation, or a paper-specific orientation signal extraction, rather than a
larger ad hoc posture search.

## Limitations

- Simulation only. No real UR10e motion, TCP write, payload write, force
  zeroing, URCap setting, or OnRobot configuration change was performed.
- Calibration uses a MuJoCo `base_link` z offset to create initial contact and
  is not a real approach trajectory.
- Orientation hold uses the initial TCP orientation, not a fully verified
  paper orientation law.
- The calibration bracket is a local search around the current contact model;
  larger postures can be discontinuous in contact force and should not be
  interpreted as hardware infeasibility.
