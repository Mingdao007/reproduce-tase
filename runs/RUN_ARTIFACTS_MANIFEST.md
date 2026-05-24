# Run Artifacts Manifest

This repo tracks lightweight migrated run metadata and plots. Large raw arrays
and large nested worktrees remain in the legacy source unless Git LFS is later
configured.

Legacy source root:

`/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/`

## Migrated Lightweight Runs

### Fig.5 scalar sweep

- Run: `runs/fig5_r_sweep/20260523T113301`
- Migrated: `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260523T113301.png`
- Omitted raw: `fig5_r-sweep_raw.npz`
- Status: legacy run, not yet re-run from this repo.

### Article-level synthetic E1-E4

- Run: `runs/full_article_experiments/20260523T114332`
- Migrated: metrics, CSV, summary Markdown, and PNG plots.
- Omitted raw: `article_experiments_raw.npz`
- Status: synthetic simulation reference, not PDF-verified paper truth.

### UR10e smoke

- Runs:
  - `runs/ur10e_smoke/20260523T113313`
  - `runs/ur10e_smoke/20260523T113341`
  - `runs/ur10e_smoke/20260523T113420`
- Migrated: metrics and PNG plots.
- Omitted raw: `ur10e-smoke_raw-state.npz`
- Status: legacy smoke runs, not yet re-run from this repo.

## New Repo Verification Runs

### Fig.5 scalar sweep

- Run: `runs/fig5_r_sweep/20260524T011145`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, no initial commit yet, dirty tree
  with untracked migrated files.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260524T011145.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with expected `pending_pdf_verify` warning.

### Fig.5 scalar sweep after initial PDF extraction

- Run: `runs/fig5_r_sweep/20260524T011603`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, starting commit
  `fe8681582e5e28243c62042f41d91c9c16f107b6`, dirty tree with PDF extraction
  edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `fig5_r-sweep_20260524T011603.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with remaining warnings for orientation signal dimension and `z0`
  source.

### UR10e MuJoCo smoke

- Run: `runs/ur10e_smoke/20260524T011145`
- Command:
  `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v0-paper-audit`, no initial commit yet, dirty tree
  with untracked migrated files.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `ur10e-smoke_contact-force_20260524T011145.png`,
  `ur10e-smoke_tcp-z_20260524T011145.png`
- Ignored raw artifact:
  `ur10e-smoke_raw-state.npz`
- Result:
  completed as approximate MJCF smoke only, not controller validation.

## V1 Math-Contract Branch Verification Runs

### Fig.5 smoke

- Run: `runs/fig5_r_sweep/20260524T012004`
- Command:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v1-math-contracts`, starting commit
  `3ca7fe22ca70dab22368523cf5066b2dd30f9e84`, dirty tree with v1
  math-contract edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `fig5_r-sweep_20260524T012004.png`
- Ignored raw artifact:
  `fig5_r-sweep_raw.npz`
- Result:
  completed with expected remaining warnings for orientation signal dimension
  and `z0` source.

### UR10e MuJoCo smoke

- Run: `runs/ur10e_smoke/20260524T012004`
- Command:
  `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
- Git state at run time:
  branch `exp/tase-ur10e-v1-math-contracts`, starting commit
  `3ca7fe22ca70dab22368523cf5066b2dd30f9e84`, dirty tree with v1
  math-contract edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `ur10e-smoke_contact-force_20260524T012004.png`,
  `ur10e-smoke_tcp-z_20260524T012004.png`
- Ignored raw artifact:
  `ur10e-smoke_raw-state.npz`
- Result:
  completed as approximate MJCF smoke only, not controller validation.

## V2 Controller Smoke Runs

### Simulation-only velocity controller smoke

- Run: `runs/controller_smoke/20260524T012218`
- Command:
  `python3 scripts/run_controller_smoke.py --config configs/mujoco_ur10e.yaml --duration-s 1.0`
- Git state at run time:
  branch `exp/tase-ur10e-v2-controller-smoke`, starting commit
  `17093c62c255b27e981b7244477e8c0d7057031e`, dirty tree with v2 controller
  smoke source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `controller-smoke_qdot_20260524T012218.png`,
  `controller-smoke_tracking-error_20260524T012218.png`
- Ignored raw artifact:
  `controller-smoke_raw.npz`
- Result:
  completed. Solver success fraction `1.0`; maximum velocity-bound violation
  `0.0`; maximum joint-limit violation `0.0`.

## V3 Contact Force Ladder Runs

### Static contact-model force ladder

- Run: `runs/contact_force_ladder/20260524T012524`
- Command:
  `python3 scripts/run_contact_force_ladder.py --config configs/mujoco_ur10e.yaml --steps 500 --tail-steps 100 --tolerance-N 0.01`
- Git state at run time:
  branch `exp/tase-ur10e-v3-contact-force-ladder`, starting commit
  `ab94671f472a6043955dfdea5d605edc55c6dc33`, dirty tree with v3 contact
  ladder source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `contact-force-ladder_offsets_20260524T012524.png`,
  `contact-force-ladder_target-vs-measured_20260524T012524.png`
- Result:
  completed. Targets `[0.5, 1.0, 2.0, 5.0] N` were matched with maximum
  absolute force error `0.0088706346160502 N`.
- Limit:
  This is a static model-offset calibration, not closed-loop force control.

## V4 Stationary Force Feedback Runs

### Stationary 5 N normal-force feedback

- Run: `runs/stationary_force_feedback/20260524T013040`
- Command:
  `python3 scripts/run_stationary_force_feedback.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5`
- Git state at run time:
  branch `exp/tase-ur10e-v4-stationary-force-feedback`, starting commit
  `082ab4e063b57bdd1cc23a4f436967a63d8497a0`, dirty tree with v4 stationary
  force-feedback source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `stationary-force-feedback_force_20260524T013040.png`,
  `stationary-force-feedback_vz_20260524T013040.png`
- Ignored raw artifact:
  `stationary-force-feedback_raw.npz`
- Result:
  completed. Initial force `5.886648180968636 N`, final force
  `5.000002800044511 N`, tail mean absolute force error
  `2.8000475610912012e-06 N`, solver success fraction `1.0`, no qdot or
  joint-limit violation.
- Limit:
  This is stationary simulation-only normal-force feedback, not tangential
  force-motion trajectory tracking and not hardware validation.

## V5 Tangential Force-Motion Runs

### Low-speed x tangential motion with 5 N normal force

- Run: `runs/tangential_force_motion/20260524T013342`
- Command:
  `python3 scripts/run_tangential_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --tangential-velocity 0.0005,0.0 --tangential-kp 0.5`
- Git state at run time:
  branch `exp/tase-ur10e-v5-tangential-force-motion`, starting commit
  `387ad1dce8b83c0ba5e897a9683e6883661aaca6`, dirty tree with v5 tangential
  force-motion source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `tangential-force-motion_force_20260524T013342.png`,
  `tangential-force-motion_xy_20260524T013342.png`
- Ignored raw artifact:
  `tangential-force-motion_raw.npz`
- Result:
  completed. Final x displacement `0.0019989989469737 m`, desired x
  displacement `0.0019990000000000008 m`, tail mean absolute force error
  `1.775978411200585e-05 N`, solver success fraction `1.0`, contact present
  fraction `1.0`, no qdot or joint-limit violation.
- Limit:
  This is low-speed simulation-only force-motion smoke. It still lacks
  orientation compliance and does not validate hardware.

## V6 Paper Trajectory Force-Motion Runs

### Paper E1 cycloid path with 5 N normal force

- Run: `runs/paper_trajectory_force_motion/20260524T013829`
- Command:
  `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5`
- Git state at run time:
  branch `exp/tase-ur10e-v6-paper-trajectory-force-motion`, starting commit
  `e47c2fe6d3ec1b17904623dcab1d787441d0183b`, dirty tree with v6 paper
  trajectory force-motion source edits.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`,
  `paper-trajectory-force-motion_force_20260524T013829.png`,
  `paper-trajectory-force-motion_xy_20260524T013829.png`
- Ignored raw artifact:
  `paper-trajectory-force-motion_raw.npz`
- Result:
  completed. Final tangential displacement
  `[0.0012394851720925958, 0.004549066283786667] m`, desired displacement
  `[0.0012387489718280922, 0.00454724750054618] m`, tail mean absolute force
  error `0.00898488092600231 N`, solver success fraction `1.0`, contact
  present fraction `1.0`, and no qdot or joint-limit violation.
- Limit:
  This is the paper E1 planar trajectory shape only. It is still
  simulation-only and lacks orientation compliance, torque dynamics, calibrated
  TCP, and hardware force source validation.

## V7 Paper Trajectory Matrix Runs

### Full-speed matrix under conservative qdot cap

- Run root: `runs/paper_trajectory_matrix/20260524T014139`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 1.0`, config default
  `0.05 rad/s` qdot cap.
- Tracked lightweight artifacts:
  per-trajectory `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-trajectory `paper-trajectory-force-motion_raw.npz`.
- Result:
  E2 and E3 lost contact; retained as negative evidence.

### Full-speed matrix under 0.15 rad/s qdot cap

- Run root: `runs/paper_trajectory_matrix/20260524T014244`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 1.0`,
  `--qdot-limit-rad-s 0.15`, plus E2/E3 high-force-gain probes.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  E2 and E3 still lost contact; high-force-gain probes saturated near the qdot
  cap and did not recover contact.

### Low-speed matrix accepted as v7 baseline

- Run root: `runs/paper_trajectory_matrix/20260524T014344`
- Scope:
  E1-E4 paper trajectory shapes, `paper_time_scale = 0.25`, config default
  `0.05 rad/s` qdot cap.
- Tracked lightweight artifacts:
  per-trajectory `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-trajectory `paper-trajectory-force-motion_raw.npz`.
- Result:
  all four trajectories maintained contact, solver success, and hard-limit
  compliance. Tail mean absolute force errors were `2.7377314706467093e-06 N`
  for E1, `0.22110301894575918 N` for E2, `0.07713928700031802 N` for E3, and
  `2.7477968988542934e-06 N` for E4.
- Limit:
  This is a low-speed trajectory-shape baseline, not full-speed Section VI
  reproduction.

## V8 Weighted Normal Force-Motion Runs

### Full-speed weighted normal-force diagnostic

- Run root: `runs/weighted_normal_force_motion/20260524T014811`
- Scope:
  Full-speed E2/E3 probes and complete E1-E4 weighted matrix using
  `--normal-axis-weight 100`, `--planar-axis-weight 1`,
  `--force-gain 5e-4`, and `--qdot-limit-rad-s 0.15`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Contact and force regulation were recovered for E1-E4 at full paper time
  scale. E2 and E3 still showed large planar tracking errors:
  `0.02114519099848796 m` and `0.016169767707432416 m` max error.
- Limit:
  This is diagnostic evidence for task-priority design. It is not a final
  full-speed paper trajectory reproduction.

## V9 Normal Guard Force-Motion Runs

### Full-speed scalar normal guard diagnostic

- Run root: `runs/normal_guard_force_motion/20260524T015341`
- Scope:
  Full-speed E2/E3 scalar guard probes plus a guarded E1-E4 matrix using
  `normal_axis_weight = 50`, `force_gain = 5e-4`,
  `--qdot-limit-rad-s 0.15`, and `normal_guard_force_fraction = 0.9`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Equal-axis guarding did not preserve E2/E3 force. Guarded
  `normal_axis_weight = 50` maintained contact, but E2/E3 retained max planar
  errors `0.020166709027307318 m` and `0.015963081975681002 m`.
- Limit:
  The scalar guard is diagnostic only. It does not solve the full-speed E2/E3
  controller tradeoff.

## V10 Residual Metrics Runs

### Full-speed E2/E3 residual comparison

- Run root: `runs/residual_metrics_force_motion/20260524T015831`
- Scope:
  Equal-axis and high-normal-weight full-speed E2/E3 cases with explicit
  normal and planar velocity residual metrics.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Equal-axis cases showed small planar residual and large normal residual with
  contact loss. High-normal-weight cases showed reduced normal residual with
  large planar residual and centimeter-scale path error.
- Limit:
  This is instrumentation and diagnostic evidence. It is not a controller fix.

## V11 Slack-Aware Force-Motion Runs

### Full-speed E2/E3 slack allocation probes

- Run root: `runs/slack_aware_force_motion/20260524T020245`
- Scope:
  E2/E3 full-speed probes using `--use-slack-solve`, planar slack weight `1`,
  normal slack weights `100`, `400`, and `10000`, and qdot cap `0.15 rad/s`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, and root
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Slack metrics expose the infeasibility tradeoff: reducing normal slack
  recovers force/contact but creates large planar slack and path error.
- Limit:
  This is a feasibility diagnostic, not full-speed paper trajectory
  reproduction.

## V12 Timing Feasibility Gate Runs

### E2/E3 paper-time-scale feasibility sweep

- Run root: `runs/timing_feasibility_sweep/20260524T021322`
- Scope:
  E2/E3 slack-aware force-motion sweeps with `paper_time_scale` values
  `1.0`, `0.75`, `0.5`, `0.35`, `0.25`, `0.2`, `0.15`, and `0.1`,
  qdot cap `0.15 rad/s`, force gain `5e-4`, planar slack weight `1`, normal
  slack weight `10000`, and explicit feasibility gates.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, root
  `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Full-speed E2/E3 remain rejected. The fastest tested passing scale for both
  E2 and E3 is `paper_time_scale = 0.2`. The `0.25` cases pass force, contact,
  position, and slack gates but fail sustained qdot saturation gates.
- Limit:
  This is a slowed simulation-only feasibility baseline, not full-speed paper
  reproduction and not hardware validation.

## V13 Posture Feasibility Gate Runs

### E2/E3 calibrated posture sweep

- Run root: `runs/posture_feasibility_sweep/20260524T022145`
- Scope:
  E2/E3 slack-aware force-motion sweeps over small initial postures
  `baseline`, `bend_0p03`, `bend_0p05`, `bend_0p075`, and `bend_0p10`.
  Each posture was calibrated to about `5 N` initial contact force using a
  MuJoCo `base_link` z offset, then tested at paper time scales `1.0`, `0.75`,
  `0.6`, `0.5`, `0.35`, `0.25`, and `0.2` with the v12 gates.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, root
  `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  The `bend_0p10` simulation posture passes full-speed E2 and E3 under the
  current gates. Smaller bends move the fastest passing scale progressively:
  `bend_0p03 -> 0.25`, `bend_0p05 -> 0.5`, `bend_0p075 -> 0.75`.
- Limit:
  This is posture-conditioning evidence in simulation only. It is not a real
  robot motion command or hardware validation.

## V14 Full-Speed Posture Matrix Runs

### E1-E4 calibrated bend_0p10 full-speed matrix

- Run root: `runs/fullspeed_posture_matrix/20260524T022724`
- Scope:
  Full-speed E1-E4 slack-aware force-motion matrix using the calibrated
  `bend_0p10` MuJoCo posture from v13, `paper_time_scale = 1.0`,
  `initial_q = [0, -0.1, 0.15, -0.05, 0, 0]`,
  `base_z_offset_m = -0.0009710693359375`, qdot cap `0.15 rad/s`, force
  gain `5e-4`, planar slack weight `1`, normal slack weight `10000`, and
  slack constraint weight `1000`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, root
  `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  E1, E2, E3, and E4 all pass the v12 feasibility gates at full paper time
  scale. Tail mean absolute force errors are below `0.001 N`, contact
  fraction is `1.0` for all cases, and qdot saturation fraction is `0.0` for
  all cases.
- Limit:
  This is a calibrated MuJoCo posture baseline, not real robot motion or
  hardware validation. Orientation compliance and planned approach behavior
  remain open.

## V15 Orientation-Hold Force-Motion Runs

### E1-E4 orientation-hold priority sweep

- Run roots:
  - `runs/orientation_hold_matrix/20260524T030000`
  - `runs/orientation_hold_matrix/20260524T023404`
  - `runs/orientation_hold_matrix/20260524T023429`
- Scope:
  Full-speed E1-E4 slack-aware force-motion matrix using the calibrated
  `bend_0p10` MuJoCo posture, with `--orientation-mode hold` and angular
  slack weights `0.1`, `0.001`, and `0.0001`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation
  plot, angular-slack plot, root `summary.csv`, `summary.json`,
  `summary.yaml`, `summary.md`, and `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Angular slack weight `0.1` fails all four existing force-motion gates due
  planar error/slack. Angular slack weight `0.001` passes E1/E3/E4 and fails
  E2 only on sustained tail qdot utilization. Angular slack weight `0.0001`
  passes the v12 force-motion gates for E1-E4 while reporting maximum
  orientation error `0.08108796381776726 rad` and maximum angular slack
  `0.08895566203803207 rad/s`.
- Limit:
  Orientation hold is measured but not paper-faithful orientation compliance.
  Orientation error is not yet a hard gate.

## V16 Orientation-Gated Timing Runs

### E1-E4 orientation-hold timing sweep with explicit gates

- Run roots:
  - `runs/orientation_gate_timing_sweep/20260524T023847`
  - `runs/orientation_gate_timing_sweep/20260524T023938_e2e3_slow`
  - `runs/orientation_gate_timing_sweep/20260524T024000_e3_slowest`
  - `runs/orientation_gate_timing_sweep/20260524T024026_common_0p075`
- Scope:
  Full-speed-to-slowed orientation-hold timing sweeps using the calibrated
  `bend_0p10` MuJoCo posture, angular slack weight `0.1`, provisional max
  orientation error gate `0.03 rad`, and provisional max angular slack gate
  `0.03 rad/s`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation
  plot, angular-slack plot, root `summary.csv`, `summary.json`,
  `summary.yaml`, `summary.md`, and `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Fastest tested passing scales are E1 `0.5`, E2 `0.1`, E3 `0.075`, and E4
  `0.5`. The common E1-E4 matrix at `paper_time_scale = 0.075` passes all
  combined force-motion and orientation gates.
- Limit:
  This is a slowed orientation-gated simulation baseline, not full-speed paper
  reproduction and not hardware validation.

## V17 Orientation-Gated Posture Runs

### Full-speed E2/E3 posture and angular-priority bracket

- Run roots:
  - `runs/orientation_posture_sweep/20260524T024358`
  - `runs/orientation_posture_sweep/20260524T041329_calibration_safe`
  - `runs/orientation_posture_sweep/20260524T041329_weight_0p03`
  - `runs/orientation_posture_sweep/20260524T041329_weight_0p01`
  - `runs/orientation_posture_sweep/20260524T041329_weight_0p003`
- Scope:
  Full-speed E2/E3 orientation-hold posture checks with provisional v16
  orientation gates, `qdot_limit = 0.15 rad/s`, `force_gain = 5e-4`, and
  angular slack weights `0.1`, `0.03`, `0.01`, and `0.003`.
- Tracked lightweight artifacts:
  per-case `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation
  plot, and angular-slack plot. Completed roots also include `summary.csv`,
  `summary.json`, `summary.yaml`, `summary.md`, and `git_state.md`. The first
  aborted root includes `ABORTED.md` instead of a root summary.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  The corrected calibration-safe sweep records uncalibratable postures instead
  of aborting. `bend_0p10` and `bend_0p125` calibrate but fail full-speed E2/E3
  planar gates when orientation gates pass. Lower angular priority restores
  planar tracking only by failing orientation gates. No tested full-speed E2/E3
  posture/weight pair passes the combined gate set.
- Limit:
  This is negative simulation-only evidence. It does not validate hardware,
  and calibration uses MuJoCo base-offset setup rather than a real approach
  trajectory.

## V18 Linear-Primary Orientation Runs

### E2/E3 timing and E1-E4 common fallback

- Run roots:
  - `runs/nullspace_orientation_timing_sweep/20260524T042206`
  - `runs/nullspace_orientation_timing_sweep/20260524T042206_common_0p075`
- Scope:
  Orientation-hold timing sweeps using the v18 `linear-primary` orientation
  priority mode. The primary solve preserves TCP linear force-motion behavior;
  the secondary solve optimizes orientation hold while preserving the primary
  TCP linear velocity.
- Tracked lightweight artifacts:
  per-case `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation
  plot, angular-slack plot, root `summary.csv`, `summary.json`,
  `summary.yaml`, `summary.md`, and `git_state.md`.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  E2 and E3 both pass the combined force-motion and orientation gates only at
  `paper_time_scale = 0.075`; higher scales are rejected by qdot saturation
  and/or orientation gates. The E1-E4 common `0.075` matrix passes all gates.
- Limit:
  This is a velocity-level simulation hierarchy, not torque-level control or
  hardware validation. It improves the controller baseline at `0.075` but does
  not recover full-speed orientation-gated reproduction.

## V21 Force-Normal Orientation Smoke

### First Section III force-normal wiring check

- Run root:
  - `runs/force_normal_orientation_smoke/20260524T045559`
- Scope:
  One-second E1 cycloid smoke at `paper_time_scale = 0.075` using
  `orientation_mode = force-normal`, `orientation_priority_mode =
  linear-primary`, `orientation_kp = 5.0`, `qdot_limit = 0.15 rad/s`, and the
  calibrated `bend_0p10` MuJoCo contact setup.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `git_state.md`, force plot, xy plot,
  orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  `paper-trajectory-force-motion_raw.npz`.
- Result:
  Solver success fraction `1.0`, contact present fraction `1.0`, tail mean
  absolute force error `0.0002761445994167211 N`, max orientation error
  `1.589167539872212e-06 rad`, max angular slack
  `1.1092273136082997e-05 rad/s`, qdot saturation fraction `0.0`, and no
  joint or velocity limit violation.
- Limit:
  The current MuJoCo surface normal is `[0, 0, 1]`, so this validates wiring
  and metadata rather than nontrivial curved-surface alignment.

## V22 Tilted Force-Normal Orientation Smokes

### First nontrivial tilted-plane normal checks

- Run roots:
  - `runs/tilted_force_normal_orientation_smoke/20260524T050139`
  - `runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1`
- Scope:
  E1 cycloid smokes at `paper_time_scale = 0.075` on a 10 degree tilted
  analytic plane using `orientation_mode = force-normal`,
  `orientation_priority_mode = linear-primary`, and `normal_velocity_mode =
  contact-normal`.
- Tracked lightweight artifacts:
  per-run `metrics.yaml`, `metrics.json`, `git_state.md`, force plot, xy plot,
  orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-run `paper-trajectory-force-motion_raw.npz`.
- Result:
  Both runs maintained solver success fraction `1.0` and contact present
  fraction `1.0`. The `kp = 5.0` run reached tail mean absolute force error
  `0.003091381344228328 N` and tail mean orientation error
  `0.07593713278249946 rad`, but qdot saturation fraction was `1.0`. The
  `kp = 0.1` comparison avoided qdot saturation and reached tail mean absolute
  force error `0.00017028171203874897 N`, but tail mean orientation error
  remained `0.14577470816672422 rad`.
- Limit:
  This validates nontrivial tilted-plane normal plumbing, not curved-surface
  adaptation or a full orientation-gated pass.

## V23 Tilted Orientation Gain/Timing Sweep

### Scalar gain/time-scale check on tilted plane

- Run root:
  - `runs/tilted_orientation_gain_timing_sweep/20260524T091826`
- Scope:
  E1 cycloid tilted-plane force-normal orientation sweeps using
  `normal_velocity_mode = contact-normal`, `orientation_mode = force-normal`,
  `orientation_priority_mode = linear-primary`, orientation gains `0.1`,
  `0.25`, `0.5`, `1.0`, `2.0`, and `5.0`, and paper time scales `0.05`,
  `0.075`, and `0.1`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-gain summaries and `git_state.md`; per-case
  `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation plot, and
  angular-slack plot.
- Ignored raw artifacts:
  per-case `paper-trajectory-force-motion_raw.npz`.
- Result:
  No case passed the existing gates. Low gains avoided qdot saturation but
  failed max orientation error at about `0.174 rad`; gains at or above `0.5`
  also failed qdot saturation and angular-slack gates.
- Limit:
  This is negative E1-only simulation evidence. It does not cover curved
  surfaces, E2-E4, torque dynamics, or hardware.

## V24 Staged Orientation Approach

### Tilted prealignment before E1 trajectory

- Run root:
  - `runs/staged_orientation_force_motion/20260524T092927`
- Scope:
  Two-phase tilted-plane check. Stage A uses a weighted force-normal
  orientation approach with zero planar trajectory. Stage B runs E1 cycloid at
  `paper_time_scale = 0.075` from the prealigned q using
  `linear-primary` force-normal orientation.
- Tracked lightweight artifacts:
  root `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  per-phase `metrics.yaml`, `metrics.json`, force plot, xy plot, orientation
  plot, and angular-slack plot.
- Ignored raw artifacts:
  `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  The approach reaches final orientation error `0.0020237968932491765 rad` and
  crosses `0.03 rad` at `0.912 s`. The trajectory phase passes all current
  gates with max orientation error `0.0020303573682621625 rad`, qdot
  saturation fraction `0.003`, and no failed criteria.
- Limit:
  The full staged maneuver is not a feasibility pass because the approach
  phase has qdot saturation fraction `0.961`, max planar drift
  `0.009738544642078033 m`, and max angular slack
  `0.06085033484246333 rad/s`.

## V25 Staged Approach Bracket

### Tilted Stage A gain/slack/priority bracket

- Run root:
  - `runs/staged_orientation_approach_bracket/20260524T093536`
- Scope:
  Seven E1 tilted-plane staged runs varying Stage A priority mode, orientation
  gain, planar slack weight, and angular slack weight while keeping the Stage B
  E1 trajectory settings from v24.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `5 / 7`, approach full-feasibility
  pass count `0 / 7`, trajectory-after-approach pass count `3 / 7`, and full
  staged-feasibility pass count `0 / 7`.
- Limit:
  This is negative E1-only tilted-plane simulation evidence. It rules out
  simple scalar gain/slack bracketing for Stage A under the current gates, but
  it does not cover curved surfaces, E2-E4 staged trajectories, torque
  dynamics, or hardware.

## V26 Long Approach Probe

### Longer low-gain tilted Stage A probe

- Run root:
  - `runs/staged_orientation_long_approach_probe/20260524T094156`
- Scope:
  Six E1 tilted-plane staged runs varying Stage A duration and orientation
  gain, including one long `linear-primary` reference, while keeping the Stage
  B E1 trajectory settings from v24/v25.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `3 / 6`, terminal approach-budget
  pass count `0 / 6`, approach ordinary-feasibility pass count `0 / 6`,
  trajectory-after-approach pass count `0 / 6`, and full staged-feasibility
  pass count `0 / 6`.
- Limit:
  This is negative E1-only tilted-plane simulation evidence. It does not cover
  curved surfaces, E2-E4 staged trajectories, torque dynamics, or hardware.

## V27 Approach Rate Cap Probe

### Tilted Stage A angular-command cap probe

- Run root:
  - `runs/staged_orientation_rate_cap_probe/20260524T094752`
- Scope:
  Six E1 tilted-plane staged runs testing the new Stage A
  `approach_max_angular_command_rad_s` option across weighted and
  `linear-primary` approach modes.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Command cap respected count `6 / 6`, approach terminal-orientation pass
  count `5 / 6`, approach terminal-budget pass count `0 / 6`,
  trajectory-after-approach pass count `3 / 6`, and full staged-feasibility
  pass count `0 / 6`.
- Limit:
  This is negative E1-only tilted-plane simulation evidence for command
  capping as a Stage A fix. It does not cover curved surfaces, E2-E4 staged
  trajectories, torque dynamics, or hardware.

## V28 Approach Qdot Budget Probe

### Separate Stage A and Stage B qdot-cap probe

- Run root:
  - `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305`
- Scope:
  Seven E1 tilted-plane staged runs testing separate approach and trajectory
  qdot caps. Stage A caps vary from `0.15` to `0.50 rad/s`; Stage B remains at
  `0.15 rad/s`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `4 / 7`, approach terminal-budget
  pass count `0 / 7`, trajectory-after-approach pass count `3 / 7`, and full
  staged-feasibility pass count `0 / 7`.
- Limit:
  This is negative E1-only tilted-plane simulation evidence for qdot
  relaxation as a Stage A fix. It does not cover curved surfaces, E2-E4 staged
  trajectories, torque dynamics, or hardware.

## V29 Staged E1-E4 After Prealignment Matrix

### Tilted-plane Section VI trajectory family after weighted prealignment

- Run root:
  - `runs/staged_orientation_e1e4_after_prealign/20260524T095804`
- Scope:
  Four staged tilted-plane runs. Stage A repeats the weighted prealignment
  setup with `approach_qdot_limit_rad_s = 0.25`; Stage B runs E1-E4 for `8 s`
  at `paper_time_scale = 0.075` with `trajectory_qdot_limit_rad_s = 0.15`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `4 / 4`, approach
  ordinary-feasibility pass count `0 / 4`, trajectory-after-approach pass
  count `3 / 4`, trajectory-feasibility pass count `3 / 4`, and full
  staged-feasibility pass count `0 / 4`. E2 fails Stage B due qdot saturation
  fraction `0.9935` and tail qdot utilization `1.0`.
- Limit:
  This is partial tilted-plane simulation evidence at slowed timing. It does
  not accept Stage A and does not establish full staged E1-E4 feasibility.

## V30 E2 After Prealignment Bracket

### E2 timing and trajectory orientation-gain isolation

- Run root:
  - `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429`
- Scope:
  Twelve E2 staged tilted-plane runs. Stage A repeats the v29 weighted
  prealignment setup. Stage B crosses `paper_time_scale` values `0.075`,
  `0.05`, and `0.025` with trajectory orientation gains `0.10`, `0.05`,
  `0.02`, and `0.00`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `12 / 12`, approach
  ordinary-feasibility pass count `0 / 12`, trajectory-after-approach pass
  count `0 / 12`, trajectory-feasibility pass count `0 / 12`, and full
  staged-feasibility pass count `0 / 12`. All Stage B failures are qdot
  saturation and tail qdot utilization only.
- Limit:
  This is E2-only negative simulation evidence under the same
  post-prealignment posture. It does not test posture redesign.

## V31 E2 Short Approach Bracket

### E2 after shorter weighted prealignment durations

- Run root:
  - `runs/staged_orientation_e2_short_approach_bracket/20260524T101113`
- Scope:
  Five E2 staged tilted-plane runs. Stage A uses the same weighted
  prealignment setup as v29/v30 but varies duration across `0.94`, `1.00`,
  `1.20`, `2.00`, and `4.00 s`. Stage B is fixed to E2 at
  `paper_time_scale = 0.075`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, `summary.md`, and
  `git_state.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `5 / 5`, approach
  ordinary-feasibility pass count `0 / 5`, trajectory-after-approach pass
  count `0 / 5`, trajectory-feasibility pass count `0 / 5`, and full
  staged-feasibility pass count `0 / 5`.
- Limit:
  This is E2-only negative simulation evidence for duration-only Stage A
  stopping. It does not test a posture objective or task-structure change.

## V32 E2 Posture Regularization

### E2 after posture-conditioned trajectory secondary objective

- Run root:
  - `runs/staged_orientation_e2_posture_regularization/20260524T102224`
- Scope:
  Ten E2 staged tilted-plane runs. Stage A uses the same weighted
  prealignment setup as v29-v31. Stage B is fixed to E2 at
  `paper_time_scale = 0.075`, while posture targets toward
  `q = [0, -0.1, 0.15, -0.05, 0, 0]` are applied to trajectory-only,
  approach-only, or both phases with weights `0.001`, `0.01`, and `0.1`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, and `summary.md`;
  per-case root `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `10 / 10`, approach
  ordinary-feasibility pass count `0 / 10`, trajectory-after-approach pass
  count `4 / 10`, trajectory-feasibility pass count `4 / 10`, and full
  staged-feasibility pass count `0 / 10`. Moderate trajectory posture
  weighting removes the E2 qdot saturation failure; strong approach posture
  weighting breaks contact/force tracking.
- Limit:
  This is an E2 Stage B fix candidate after the current relaxed weighted
  prealignment. It does not establish an accepted Stage A approach or full
  staged feasibility.

## V33 Staged E1-E4 With Trajectory Posture Regularization

### Slowed Section VI trajectory family after posture-conditioned Stage B

- Run root:
  - `runs/staged_orientation_e1e4_posture_regularized/20260524T102747`
- Scope:
  Four staged tilted-plane runs. Stage A repeats the weighted prealignment
  setup. Stage B runs E1-E4 for `8 s` at `paper_time_scale = 0.075`, with the
  v32 trajectory posture objective set to target
  `q = [0, -0.1, 0.15, -0.05, 0, 0]`, `kp = 1.0`, weight `0.001`, and max
  posture velocity `0.05 rad/s`.
- Tracked lightweight artifacts:
  root `summary.csv`, `summary.json`, `summary.yaml`, and `summary.md`;
  per-case root `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Approach terminal-orientation pass count `4 / 4`, approach
  ordinary-feasibility pass count `0 / 4`, trajectory-after-approach pass
  count `4 / 4`, trajectory-feasibility pass count `4 / 4`, and full
  staged-feasibility pass count `0 / 4`. All four Stage B trajectories have
  no failed criteria and qdot saturation fraction `0.0`.
- Limit:
  This confirms the slowed Stage B family after the current weighted
  prealignment. It does not establish an accepted Stage A approach or full
  staged feasibility.

## V34 Planar-Primary Approach Priority

### Stage A x/y-primary diagnostic controller

- Run roots:
  - `runs/staged_orientation_planar_primary_approach/20260524T103539`
  - `runs/staged_orientation_planar_primary_normal_weight/20260524T103646`
- Scope:
  Simulation-only E1 staged runs testing `planar-primary` approach priority.
  The first run compares a weighted reference with planar-primary qdot/gain
  and angular-cap variants. The second run increases normal secondary weights
  to test whether force/contact can be restored without losing terminal
  orientation.
- Tracked lightweight artifacts:
  each root has `summary.csv`, `summary.json`, `summary.yaml`, and
  `summary.md`; per-case root `metrics.yaml`, `metrics.json`, `summary.md`,
  and `git_state.md`; per-phase `metrics.yaml`, `metrics.json`, force plot,
  xy plot, orientation plot, and angular-slack plot.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz` and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  The first bracket has `0 / 6` terminal-budget passes and `1 / 6`
  trajectory-after-approach passes. The normal-weight follow-up has `0 / 5`
  terminal-budget passes and `0 / 5` trajectory-after-approach passes.
  Planar-primary priority controls x/y drift but either loses contact/force
  or stalls terminal orientation when normal weighting is increased.
- Limit:
  This is E1-only tilted-plane Stage A evidence. It does not establish a full
  approach solution or hardware readiness.

## V35 Two-Phase Approach Recenter Probe

### Planned setup terminal-state diagnostic

- Run root:
  - `runs/staged_orientation_two_phase_recenter/20260524T104957`
- Scope:
  Ten E2 staged tilted-plane runs. Stage A1 repeats weighted force-normal
  prealignment. Stage A2 is optional recentering to the original setup x/y
  reference with weighted, linear-primary, or planar-primary priority. Stage B
  uses the v32 moderate trajectory posture objective.
- Tracked lightweight artifacts:
  root `summary.yaml` and `summary.md`; per-case root `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; per-phase `metrics.yaml`,
  `metrics.json`, force plot, xy plot, orientation plot, and angular-slack
  plot for `approach`, optional `approach_recenter`, and `trajectory`.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz`,
  `approach_recenter/staged-approach_recenter_raw.npz`, and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Setup terminal-state pass count `0 / 10`, trajectory feasibility pass count
  `4 / 10`, legacy trajectory-after-approach pass count `4 / 10`, planned
  setup-then-trajectory pass count `0 / 10`, and full staged-feasibility pass
  count `0 / 10`.
- Limit:
  This is E2-only tilted-plane simulation evidence. It does not establish a
  full E1-E4 planned setup solution or hardware readiness.

## V36 Three-Phase Setup Settle Probe

### Planned align/recenter/settle diagnostic

- Run root:
  - `runs/staged_orientation_three_phase_settle/20260524T110039`
- Scope:
  Ten E2 staged tilted-plane runs. Stage A1 repeats weighted force-normal
  prealignment. Stage A2 optionally recenters to the original setup x/y
  reference with linear-primary priority. Stage A3 optionally settles against
  the same x/y reference before Stage B. Stage B uses the v32 moderate
  trajectory posture objective.
- Tracked lightweight artifacts:
  root `summary.yaml` and `summary.md`; per-case root `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; per-phase `metrics.yaml`,
  `metrics.json`, force plot, xy plot, orientation plot, and angular-slack
  plot for `approach`, optional `approach_recenter`, optional
  `approach_settle`, and `trajectory`.
- Ignored raw artifacts:
  per-case `approach/staged-approach_raw.npz`,
  `approach_recenter/staged-approach_recenter_raw.npz`,
  `approach_settle/staged-approach_settle_raw.npz`, and
  `trajectory/staged-trajectory_raw.npz`.
- Result:
  Setup terminal-state pass count `0 / 10`, trajectory feasibility pass count
  `8 / 10`, legacy trajectory-after-approach pass count `8 / 10`, planned
  setup-then-trajectory pass count `0 / 10`, and full staged-feasibility pass
  count `0 / 10`.
- Limit:
  This is E2-only tilted-plane simulation evidence. It does not establish a
  full E1-E4 planned setup solution or hardware readiness.

## V37 Setup Terminal IK Audit

### Terminal setup configuration diagnostic

- Run root:
  - `runs/setup_terminal_ik_audit/20260524T111150`
- Scope:
  Terminal nonlinear least-squares audit over the tilted-plane setup. The probe
  searches joint configurations against the explicit x/y, force, contact, and
  force-normal orientation setup gate without simulating a Stage A path.
- Tracked lightweight artifacts:
  root `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Ignored raw artifacts:
  none.
- Result:
  Terminal setup pass count `0 / 65`. Best candidate has force error
  `0.004835673570861232 N`, x/y error `0.002178947478445584 m`, and
  orientation error `0.05199834145021794 rad`.
- Limit:
  This is a local terminal IK audit, not a global infeasibility proof, not a
  path/controller solution, and not hardware readiness evidence.

## V38 Relaxed Setup Budget Evaluation

### UR10e adapted acceptance-label evaluation

- Run root:
  - `runs/relaxed_setup_budget_eval/20260524T111859`
- Source run:
  - `runs/staged_orientation_e1e4_posture_regularized/20260524T102747`
- Scope:
  Applies `configs/ur10e_adapted_acceptance.yaml` to the v33 slowed
  tilted-plane E1-E4 matrix. The relaxed setup budget accepts up to `0.010 m`
  setup drift while keeping force/contact, final orientation, hard limits, and
  strict Stage B trajectory gates.
- Tracked lightweight artifacts:
  root `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Ignored raw artifacts:
  none.
- Result:
  Relaxed setup pass count `4 / 4`, trajectory feasibility pass count `4 / 4`,
  UR10e adapted trajectory-after-relaxed-setup pass count `4 / 4`, and strict
  full staged feasibility pass count `0 / 4`.
- Limit:
  This is acceptance bookkeeping for simulation evidence. It is not
  paper-equivalent full staged feasibility and not hardware readiness evidence.

## V39 Completion Audit

### Prompt-to-artifact audit

- Artifact:
  - `reports/completion_audit.md`
- Scope:
  Maps the long-form goal requirements to repo artifacts, run metrics,
  commands, and remaining gaps.
- Result:
  Confirms the repository has an accepted UR10e adapted simulation claim under
  the v38 relaxed setup budget, but the overall goal is not complete because
  strict paper-equivalent full staged feasibility, hardware readiness, and a
  separate paper-faithful 7DOF executable line remain incomplete.
- Limit:
  Documentation-only audit. No new simulation run and no hardware work.

## V40 Section V z0 Audit

### PDF truth extraction cleanup

- Artifact:
  - `reports/section_v_z0_audit.md`
- Scope:
  Uses layout and raw `pdftotext` extraction to determine whether Section V
  defines the `z0` in `xpd = [0.2 cos(0.2t); 0.2 sin(0.2t); z0]`.
- Result:
  Section V uses `z0` without defining it. Section VI defines experiment `z0`
  separately. `configs/paper_truth.yaml` now has no `pending_pdf_verify`
  fields.
- Limit:
  Documentation-only paper-truth audit. No new simulation run and no hardware
  work.

## V41 Paper 7DOF Executable Diagnostic

### Separate paper-platform Section V line

- Run:
  - `runs/paper_7dof_section_v/20260524T113608`
- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc`
- Git state at run time:
  branch `exp/tase-ur10e-v41-paper-7dof-line`, code commit
  `bf7209d52476d951e99f6ed7cbce1c7acc3db0e8`, clean before output creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  The separate 7DOF diagnostic executed successfully with no q or qdot bound
  violations. It did not maintain force/contact in the tail:
  `contact_force_tail_success = false`, `tail_contact_fraction = 0.0`, and
  `tail_force_error_mean_N = 5.0`.
- Limit:
  This is a paper-platform executable diagnostic, not paper-faithful numerical
  parity, not a UR10e adapted result, and not hardware readiness evidence.

## V42 Paper 7DOF Contact Loop Diagnostic

### Contact-stabilized paper-platform Section V line

- Run:
  - `runs/paper_7dof_section_v/20260524T114244`
- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode pinv_bounded --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Git state at run time:
  branch `exp/tase-ur10e-v42-paper-7dof-contact-loop`, code commit
  `16ba42368f81145f2970c8d8d295f6ed238e7be4`, clean before output creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  The contact-stabilized diagnostic passed tail force/contact:
  `contact_force_tail_success = true`, `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.013764149103712913`, and no q or qdot bound
  violations.
- Limit:
  This is a diagnostic paper-platform run using `pinv_bounded` and a capped
  force integral. It is not the paper-faithful KKT-projection result, not
  Fig.5/Fig.6 parity, not a UR10e adapted result, and not hardware readiness
  evidence.

## V43 Paper 7DOF KKT Contact Recovery

### Capped-integral KKT paper-platform Section V line

- Run:
  - `runs/paper_7dof_section_v/20260524T114736`
- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Git state at run time:
  branch `exp/tase-ur10e-v43-paper-7dof-kkt-sweep`, code commit
  `38216bba5e08af8fbf0f078583f438c044990d68`, clean before output creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  The capped-integral KKT diagnostic passed tail force/contact:
  `contact_force_tail_success = true`, `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.06720487008205062`, and no q or qdot bound
  violations.
- Limit:
  This is KKT-contact recovery evidence for the Python 7DOF diagnostic line,
  not paper-equivalent numerical parity, because the force-integral cap is an
  explicit anti-windup choice and the Panda DH/orientation assumptions remain
  unverified.

## V44 Paper Platform Parity Gate

### Strict gate against legacy MATLAB/RNN Section V outputs

- Run:
  - `runs/paper_platform_parity_eval/20260524T115641`
- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Config:
  `configs/paper_platform_parity.yaml`
- Candidate:
  `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`
- Legacy references:
  - `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_formula_faithful/paper_method_formula_faithful_verification.md`
  - `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/paper_method_figure_match/paper_method_figure_match_verification.md`
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Result:
  `paper_platform_parity_pass = false`. The v43 Python candidate passes
  execution/contact/bounds and agrees with the formula-faithful tail
  convergence reference under configured tolerances, but strict parity fails
  on duration coverage, Fig.6 q7-at-22 s, missing Python Fig.5 r-sweep
  coverage, and the finite force-integral cap.
- Limit:
  This artifact defines and applies the gate. It is not a paper-equivalent
  numerical parity pass.

## V45 Paper 7DOF 30 s Candidate

### Full-duration capped-integral KKT paper-platform diagnostic

- Run:
  - `runs/paper_7dof_section_v/20260524T120439`
- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Git state at run time:
  code commit `51f76512449051d278abe8f8a75cd96ed45480c8`, clean before
  output creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  The 30 s candidate passed execution/contact/bounds and recorded
  `fig6_q7_at_22s_rad = 1.6755097668200787`.

### Parity gate on the 30 s candidate

- Run:
  - `runs/paper_platform_parity_eval/20260524T120503`
- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Git state at run time:
  commit `2f40029bc7b320359582ae464b70b0610741c523`, clean before output
  creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Result:
  `paper_platform_parity_pass = false`. Duration coverage and
  formula-faithful tail convergence checks pass. Remaining failures are
  Fig.6 q7-at-22 s mismatch, missing Python Fig.5 r-sweep coverage, and the
  finite force-integral cap.

## V46 Paper 7DOF Fig.5 r Sweep

### Python-side Fig.5 coverage for strict parity gate

- Run:
  - `runs/paper_7dof_fig5_r_sweep/20260524T121033`
- Command:
  `scripts/run_paper_7dof_fig5_r_sweep.py --duration-s 2.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Git state at run time:
  code commit `43f71fd79988f4f28549e213f542a3fa2fd30d28`, clean before
  output creation.
- Tracked lightweight artifacts:
  top-level `summary.yaml`, `summary.json`, `summary.md`, plus per-r
  `metrics.yaml`, `metrics.json`, and `summary.md` under `r_0p2`, `r_0p4`,
  `r_0p6`, `r_0p8`, and `r_1p0`.
- Result:
  All five r rows executed successfully and are now wired into
  `configs/paper_platform_parity.yaml`.

### Parity gate after Fig.5 coverage

- Run:
  - `runs/paper_platform_parity_eval/20260524T121116`
- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Git state at run time:
  commit `b0059d8ece3bb140a5a27b8aa9efebba927b1679`, clean before output
  creation.
- Result:
  `paper_platform_parity_pass = false`. The gate now passes Fig.5 r-sweep
  coverage. Remaining failures are Fig.6 q7-at-22 s mismatch and the finite
  force-integral cap.

## V47 Paper 7DOF Uncapped KKT Candidate

### Uncapped full-duration paper-platform candidate

- Run:
  - `runs/paper_7dof_section_v/20260524T121503`
- Command:
  `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-leak 0.0`
- Git state at run time:
  commit `d4884d79c3e0702228e11205976bb8dc506e4472`, clean before output
  creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  The uncapped KKT candidate passes execution/contact/bounds:
  `contact_force_tail_success = true`, `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.023282898803479644`, and no q/qdot bound
  violations. It records `fig6_q7_at_22s_rad = 1.6680622878116045`.

### Strict parity gate after removing integral cap

- Run:
  - `runs/paper_platform_parity_eval/20260524T121542`
- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Git state at run time:
  commit `60c430179aff31400ae115a9a4f3fb61725e5dd5`, clean before output
  creation.
- Result:
  `paper_platform_parity_pass = false`. The gate now passes
  `paper_assumption_compatibility`; the only remaining strict-gate failure is
  `fig6_q7_22s_landmark`.

## V48 Paper 7DOF q7 Mismatch Probe

### Supported Python variant matrix for q7 at 22 s

- Run:
  - `runs/paper_7dof_q7_variant_probe/20260524T122345`
- Command:
  `scripts/run_paper_7dof_q7_variant_probe.py --duration-s 30.0 --dt-s 0.002 --communication-delay-s 0.032 --force-integral-leak 0.0`
- Git state at run time:
  commit `48683797d62c4bbee0d8e1dbaeaacd5a4c545b68`, clean before output
  creation.
- Tracked lightweight artifacts:
  top-level `summary.yaml`, `summary.json`, `summary.md`, plus per-variant
  `metrics.yaml`, `metrics.json`, and `summary.md` under
  `kkt_force_uncapped`, `kkt_force_cap0p1`, `kkt_normal_uncapped`,
  `kkt_normal_cap0p1`, `pinv_force_uncapped`, `pinv_force_cap0p1`,
  `pinv_normal_uncapped`, and `pinv_normal_cap0p1`.
- Result:
  All eight variants execute successfully and expose q7 at 22 s. q7 ranges
  from `1.661263839866546` to `1.6835894792145727 rad`; none are within the
  `0.05 rad` tolerance of the `2.5 rad` figure-match reference.

## V49 Paper Fig.6 Raw Provenance Audit

### Legacy raw Fig.6 and Python candidate comparison

- Run:
  - `runs/paper_7dof_fig6_raw_provenance/20260524T123130`
- Command:
  `scripts/compare_paper_7dof_fig6_raw_provenance.py`
- Git state at run time:
  commit `b5941061881fd5962e4b2504b40d1f0f61575704`, clean before output
  creation.
- External raw inputs:
  ignored local `.mat` files under
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/`,
  plus ignored Python raw `.npz` at
  `runs/paper_7dof_section_v/20260524T121503/paper_7dof_section_v_raw.npz`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Result:
  Python Panda FK and Jacobian conditioning match sampled legacy raw states to
  numerical precision. The legacy figure-match q7 target comes from a
  `pinv_bounded`/`normal_only`/`admittance_proxy` line with `landmark`
  acceptance and q7 pinned at the upper limit for `17829` samples, not from
  the formula-faithful `paper_literal` line.

## V50 Legacy Figure-Match Source Audit

### Static source and raw-output audit of figure-match tuning

- Run:
  - `runs/legacy_figure_match_source_audit/20260524T123651`
- Command:
  `scripts/audit_legacy_figure_match_source.py`
- Git state at run time:
  commit `deaf21d52abb86e52ed146ddafe7a80e147dd773`, clean before output
  creation.
- External source inputs:
  MATLAB/RNN files under
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Result:
  The source audit identifies eight non-paper-faithful `figure_match` tuning
  knobs and confirms `q7NullspaceSpeed = 0.35` is wired into the
  pseudoinverse nullspace branch. The q7 landmark should be treated as tuned
  figure-match evidence, not a formula-faithful parity requirement.

## V51 Split Paper-Platform Parity Claims

### Split claim-level paper-platform evaluation

- Run:
  - `runs/paper_platform_parity_eval/20260524T124200`
- Command:
  `scripts/evaluate_paper_platform_parity.py`
- Git state at run time:
  commit `bddf1dad1645199de92458616162291b6881aa4c`, clean before output
  creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Result:
  `paper_platform_formula_convergence_pass = true`,
  `paper_platform_figure_match_landmark_pass = false`, and
  `paper_platform_parity_pass = false`. The old strict aggregate remains
  failed, while formula-convergence evidence is now separately reportable.

## V52 Python Tuned Figure-Match Candidate

### Tuned paper-platform Fig.6 q7 landmark candidate

- Run:
  - `runs/paper_7dof_section_v/20260524T134441`
- Command:
  `scripts/run_paper_7dof_section_v.py --figure-match-preset --duration-s 30 --dt-s 0.001`
- Git state at run time:
  commit `2f65a5908528670868ed5d9e4ffab9f8443b77a2`, clean before output
  creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- Ignored raw artifact:
  `paper_7dof_section_v_raw.npz`.
- Result:
  Python tuned figure-match candidate reproduced the q7 landmark with
  `fig6_q7_at_22s_rad = 2.4999999999331863` and
  `fig6_q7_abs_error_to_2p5_rad = 6.681366571115177e-11`, while explicitly
  labeling the non-paper-faithful tuning knobs.

### Raw provenance comparison for tuned candidate

- Run:
  - `runs/paper_7dof_fig6_raw_provenance/20260524T134549`
- Command:
  `scripts/compare_paper_7dof_fig6_raw_provenance.py --python-label python_v52_tuned_figure_match --python-raw-npz runs/paper_7dof_section_v/20260524T134441/paper_7dof_section_v_raw.npz --python-metrics-yaml runs/paper_7dof_section_v/20260524T134441/metrics.yaml`
- Git state at run time:
  commit `e52d3885e5e4db76be8d0c36f1358e489279d8a7`, clean before output
  creation.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, and `summary.md`.
- External or ignored raw inputs:
  ignored legacy `.mat` files plus ignored Python
  `paper_7dof_section_v_raw.npz`.
- Result:
  The Python v52 tuned candidate matches legacy `figure_match` with
  q7@22 s delta `2.6201263381153694e-12 rad`, q7 RMSE
  `2.337566316043061e-11 rad`, and joint RMSE
  `6.081574510252252e-09 rad`.

### Split evidence claim contract

- Report:
  - `reports/paper_platform_split_evidence_report.md`
- Result:
  The project now has an explicit paper-platform reporting contract:
  formula-convergence evidence and tuned figure-match landmark reproduction
  are both available, but full paper-equivalent numerical parity remains
  unclaimed.

## V53 UR10e TCP/Contact Model Audit

### TCP/contact convention audit

- Run:
  - `runs/tcp_contact_model_audit/20260524T135607`
- Command:
  `scripts/audit_tcp_contact_model.py`
- Git state at run time:
  commit `d8d9c26d36bf9b08169aee333b39d26460b5803c`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The config TCP guess and MJCF body offset both encode the EOAT note distance
  of `0.085 m`, but the `tcp_site_unverified_85mm` site is coincident with the
  center of the `contact_tip` sphere. The simulated plane-contact surface is
  one sphere radius away from the site:
  `site_to_sphere_surface_projection_on_normal_m = 0.04500000000000001` and
  `parent_to_sphere_surface_distance_m = 0.12955222618906498`.

### Terminal IK rerun after TCP/contact audit

- Run:
  - `runs/setup_terminal_ik_audit/20260524T135619`
- Command:
  `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001`
- Git state at run time:
  commit `d8d9c26d36bf9b08169aee333b39d26460b5803c`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The strict terminal setup gate remains failed with `0 / 65` passing
  candidates. The best candidate still fails x/y and orientation gates while
  keeping force error low.

## V54 TCP Contact-Point Model Variant

### TCP/contact audit for contact-point variant

- Run:
  - `runs/tcp_contact_model_audit/20260524T140535`
- Command:
  `scripts/audit_tcp_contact_model.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
- Git state at run time:
  commit `1725f4c28796fc844dc1d350236755e6c4d59c28`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The contact-point model separates the 85 mm TCP site from the sphere center:
  `site_coincident_with_contact_geom_center = false`,
  `contact_surface_offset_requires_model_decision = false`, and
  `contact_tip` local center is `[0.0, 0.0, 0.045]`. At the audited posture
  the site-to-sphere-surface projection on the plane normal is
  `0.0006836511144550518 m`.

### Terminal IK rerun on contact-point variant

- Run:
  - `runs/setup_terminal_ik_audit/20260524T140539`
- Command:
  `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001`
- Git state at run time:
  commit `1725f4c28796fc844dc1d350236755e6c4d59c28`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The strict terminal setup gate remains failed with `0 / 65` passing
  candidates. The best candidate fails x/y and orientation gates with force
  error `0.0050975519688662985 N`, x/y error `0.0030075788240061675 m`, and
  orientation error `0.07240603253666981 rad`.

## V55 Broad Terminal Feasibility Audit

### Broad target-contact terminal IK audit

- Run:
  - `runs/setup_terminal_ik_audit/20260524T141321`
- Command:
  `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count 512 --random-seed-std-rad 2.0 --random-seed 541 --max-nfev 800 --posture-weight 0.0`
- Git state at run time:
  commit `8da8828ac9182816459bcb54e129d33413fcfa98`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The terminal setup audit now uses only the intended `contact_plane` /
  `contact_tip` target-pair force for the setup force gate. With `513` broad
  candidates, the strict setup pass count remains `0 / 513`. The best target
  contact candidate fails x/y and orientation gates.

## V56 Contact-Manifold Gate Audit

### Gate-combination audit from target-contact neighborhoods

- Run:
  - `runs/contact_manifold_gate_audit/20260524T142404`
- Command:
  `scripts/audit_contact_manifold_setup_gate.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count-per-std 40 --random-seed-stds-rad 0.03,0.1,0.3,0.8 --random-seed 761 --max-nfev 800`
- Git state at run time:
  commit `1d83e8f99ca29c75b1392d16033327df0d340d99`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The strict `xy_force_orientation` case remains failed with `0 / 161`
  passes. Relaxed cases show the gate conflict: `xy_force` leaves orientation
  error, `xy_orientation` loses target contact/force, and `force_orientation`
  requires centimeter-scale x/y drift.

## V57 Adapted Terminal Setup Diagnostic Gate

### Diagnostic terminal setup gate evaluation

- Run:
  - `runs/terminal_setup_gate_eval/20260524T143019`
- Command:
  `scripts/evaluate_terminal_setup_gate.py --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --acceptance-config configs/ur10e_adapted_acceptance.yaml`
- Git state at run time:
  commit `167ca325dd71c2d25281ebe1c86a7e7e27c85d94`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The v57 diagnostic terminal setup gate reports `1 / 513` passing candidates
  from the v55 broad terminal run. This is a diagnostic setup label only, not
  path feasibility, trajectory feasibility, paper-equivalent feasibility, or
  hardware readiness.

## V58 Stage A Target Selection

### Selected diagnostic terminal setup target

- Config:
  - `configs/ur10e_adapted_stage_a_target.yaml`
- Report:
  - `reports/stage_a_target_selection_report.md`
- Source evidence:
  - `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml`
  - `runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml`
- Result:
  The next Stage A simulation prototype target label is explicitly selected as
  `ur10e_adapted_terminal_setup_diagnostic`. The selected q target is recorded
  in the config. This is a target-selection artifact only, not a controller or
  feasibility run.

## V59 Diagnostic Target Handoff Audit

### Stage B handoff from selected diagnostic terminal target

- Run:
  - `runs/stage_a_target_handoff_eval/20260524T144654`
- Command:
  `scripts/evaluate_stage_a_target_handoff.py`
- Git state at run time:
  commit `7763394662bebd9376994d39ebdf7be524f1f04c`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The handoff audit starts directly from the v58 selected diagnostic terminal
  q and evaluates E1-E4 with target-pair force/contact accounting. It reports
  `0 / 4` passes. All rows keep target contact and satisfy force, x/y, and
  diagnostic orientation thresholds, but all rows fail qdot saturation gates.
  This is not a Stage A path or trajectory-feasibility claim.

## V60 Qdot-Aware Diagnostic Handoff

### Slowed low-gain handoff from selected diagnostic terminal target

- Run:
  - `runs/stage_a_target_handoff_eval/20260524T145433`
- Command:
  `scripts/evaluate_stage_a_target_handoff.py --orientation-kp 0.0 --paper-time-scale 0.01 --force-gain 1e-4`
- Git state at run time:
  commit `67b0f053f525cfbcf23db872ccc994d100ecca7f`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The qdot-aware diagnostic handoff reports `4 / 4` passes from the selected
  target. It uses slowed timing, lower force gain, diagnostic-orientation hold,
  and target-pair force/contact accounting. This is direct-target handoff
  evidence only, not a Stage A path or paper-equivalent trajectory claim.

## V61 Stage A Contact Path Audit

### Offline quasi-static contact path to selected diagnostic target

- Run:
  - `runs/stage_a_contact_path_audit/20260524T151201`
- Command:
  `scripts/audit_stage_a_contact_path.py`
- Git state at run time:
  commit `878bb1649f876344f703a3a4d8156ece32847c12`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, `path.csv`, and
  `git_state.md`.
- Result:
  The audit finds a 128-knot offline quasi-static contact path from the
  ordinary initial q to the v58 selected diagnostic target. The path gate and
  terminal diagnostic gate pass with target contact present throughout. The
  qdot-limited minimum duration for `0.15 rad/s` is
  `14.332635022800167 s`.
- Limit:
  This is offline path evidence only. It is not an online Stage A controller,
  strict trajectory-feasibility claim, paper-equivalent claim, or hardware
  claim.

## V62 Stage A Contact Path Tracking

### Qdot-limited replay of the selected diagnostic contact path

- Run:
  - `runs/stage_a_contact_path_tracking/20260524T152346`
- Command:
  `scripts/track_stage_a_contact_path.py`
- Git state at run time:
  commit `6edddf4a05fae2671ee91f62bc653ec11d2f6058`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, `tracking_trace.csv`, and
  `git_state.md`.
- Result:
  The tracker follows the v61 path over `15.0 s`. The tracking gate and
  terminal diagnostic gate pass with max qdot `0.14332635022814824 rad/s`,
  qdot saturation `0.0`, final tracking error `0.0`, and target contact present
  throughout.
- Limit:
  This is a qdot-limited joint-path tracking prototype only. It is not a
  connected Stage A plus Stage B trajectory claim, paper-equivalent claim, or
  hardware claim.

## V63 Stitched Stage A Handoff

### Diagnostic Stage A tracker plus Stage B handoff in one run

- Run:
  - `runs/stitched_stage_a_handoff_eval/20260524T152807`
- Command:
  `scripts/evaluate_stitched_stage_a_handoff.py`
- Git state at run time:
  commit `748c4d46730d6f7044c8056fb6babc6c0804f1d2`.
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The stitched gate passes. Stage A tracking passes, and Stage B reports `4 / 4`
  E1-E4 handoff passes with target-pair force/contact accounting. Stage A max
  qdot is `0.14332635022814824 rad/s`, and qdot saturation is `0.0`.
- Limit:
  This is nominal diagnostic-label simulation evidence only. It is not strict
  paper-equivalent feasibility, perturbation robustness evidence, or hardware
  evidence.

## V64 Stitched Handoff Sensitivity Audit

### Sensitivity matrix around the v63 diagnostic staged policy

- Run:
  - `runs/stitched_stage_a_handoff_sensitivity/20260524T161111`
- Command:
  `scripts/audit_stitched_stage_a_handoff_sensitivity.py`
- Git state at run time:
  commit `1e15d9828145cc30b93c274d77eb99d2206a670f`.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-case metrics, summaries, git state, and command stdout/stderr under
  `cases/*`.
- Result:
  The sensitivity matrix reports a stitched pass count of `4 / 9`. Passing
  cases are nominal, `stage_a_16s`, `force_gain_5e-5`, and `force_gain_2e-4`.
  Failing cases are `base_z_minus_1mm`, `base_z_plus_1mm`, `stage_a_14s`,
  `qdot_limit_0p12`, and `paper_time_scale_0p02`.
- Limit:
  This is a sensitivity boundary for diagnostic-label simulation only. It is
  not a strict paper-equivalent claim, a robustness proof, or hardware
  evidence.

## V65 Stitched Timing Margin Audit

### Timing-margin case set around the v63 diagnostic staged policy

- Run:
  - `runs/stitched_stage_a_handoff_timing_margin/20260524T162005`
- Command:
  `scripts/audit_stitched_stage_a_handoff_sensitivity.py --case-set timing-margin`
- Git state at run time:
  commit `c071469132a2d39336f9e8727f51fed88d5334a1`.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-case metrics, summaries, git state, and command stdout/stderr under
  `cases/*`.
- Result:
  The timing-margin matrix reports a stitched pass count of `4 / 7`. Passing
  cases are nominal, `stage_a_14p5_recovery`,
  `qdot012_stage_a_18p0_recovery`, and `paper_time_scale_0p012_recovery`.
  Failing boundary cases are `stage_a_14s_reference_fail`,
  `qdot012_stage_a_17p5_reference_fail`, and
  `paper_time_scale_0p0125_reference_fail`.
- Limit:
  This is a diagnostic-label timing-margin audit only. It does not recover the
  1 mm base-z/contact perturbation failures and is not a strict
  paper-equivalent claim, a robustness proof, or hardware evidence.

## Full Paper MATLAB/RNN Run

### Selected migrated evidence

- Legacy run: `runs/full_paper_matlab/20260523T114034`
- Migrated:
  selected Markdown reports and PNG verification figures under
  `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/`, plus the
  artifact README.
- Reason:
  These files are lightweight enough for the initial ordinary Git commit and
  preserve the report links for Fig.5/Fig.6 evidence.
- Omitted:
  MATLAB source worktree files, `.mat` raw data, tarball snapshots, logs, and
  archive payloads.
- Current documentation:
  `reports/full_article_reproduction_report.md` summarizes the result and
  legacy paths.
- Future action:
  Decide whether to migrate selected MATLAB source, use Git LFS for raw
  artifacts, or preserve the legacy path as external provenance.
