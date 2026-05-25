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

## V66 Stage A Base-Z Recovery Audit

### Perturbation-aware start/target/path recovery for base-z cases

- Run:
  - `runs/stage_a_base_z_recovery/20260524T163746`
- Command:
  `scripts/audit_stage_a_base_z_recovery.py`
- Git state at run time:
  base commit `a50628bb7351b12d59320e69ec85bce0acca1e96` with dirty v66
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-case start, terminal, path, and stitched metrics/summaries/commands
  under `cases/*`.
- Result:
  The recovery matrix reports `1 / 3` recovered cases. The recovered case is
  `base_z_minus_1mm_stage_a_16s_recovery`. The exact `15.0 s`
  `base_z_minus_1mm` reference remains qdot-limited, and `base_z_plus_1mm`
  remains unresolved with no passing start plus terminal target pair under this
  diagnostic search.
- Limit:
  This is a diagnostic-label base-z recovery audit only. It is not a strict
  paper-equivalent claim, a robustness proof, contact-model calibration, or
  hardware evidence.

## V67 Stage A Base-Z Bracket Audit

### Compact perturbation bracket around the v66 positive-side gap

- Run:
  - `runs/stage_a_base_z_bracket/20260524T165411`
- Command:
  `scripts/audit_stage_a_base_z_bracket.py`
- Git state at run time:
  parent commit `3f280e2d35ea2d87abc9769a81c1ff0cf377415e` with dirty v67
  bracket code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  compact start/terminal summaries for every delta, and path/stitched artifacts
  only for feasible endpoint cases.
- Result:
  The compact bracket evaluates `13` deltas. Nominal, `-0.25 mm`, and
  `-0.5 mm` recover at `15.0 s`; `-1.0 mm` recovers only at `16.0 s`;
  `-0.75 mm` has a path-geometry failure; and no tested positive delta from
  `+0.05 mm` through `+1.0 mm` has both start and terminal feasibility.
- Limit:
  This is diagnostic-label simulation bracket evidence only. It is not a
  strict paper-equivalent claim, a robustness proof, contact-model calibration,
  or hardware evidence.

## V68 Positive Base-Z Start Contact Audit

### Positive-side start-contact recovery and terminal-orientation split

- Run:
  - `runs/positive_base_z_start_contact/20260524T170350`
- Command:
  `scripts/audit_positive_base_z_start_contact.py`
- Git state at run time:
  parent commit `df2790d834c4cb2b4fabc8c549444b28304a9d26` with dirty v68
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus compact start-search and terminal summaries for each positive delta.
- Result:
  The audit evaluates `8` positive base-z deltas from `+0.05 mm` through
  `+1.0 mm`. Broader start-contact seed sweeps recover start contact for
  `8 / 8` cases. The terminal diagnostic gate passes `0 / 8`; every positive
  terminal row still fails orientation.
- Limit:
  This is diagnostic-label simulation start-contact evidence only. It is not a
  strict paper-equivalent claim, terminal recovery, path or stitched recovery,
  a robustness proof, contact-model calibration, or hardware evidence.

## V69 Positive Terminal Orientation Audit

### Orientation margin under current contact-point model

- Run:
  - `runs/positive_terminal_orientation/20260524T171705`
- Command:
  `scripts/audit_positive_terminal_orientation.py`
- Git state at run time:
  parent commit `cb2f85805ce32945fc91775bdfadc85552023dc1` with dirty v69
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-variant/per-delta compact terminal-orientation metrics.
- Result:
  In the current contact-point model, force/x-y/contact passes all `8 / 8`
  positive terminal cases, while the `0.08 rad` diagnostic orientation gate
  passes `0 / 8`. Full-rotation and force-normal-only errors are numerically
  identical, so yaw handling is not the limiting convention. The legacy
  sphere-center model passes `6 / 8` through `+0.5 mm`, but remains a known
  flawed comparison model.
- Limit:
  This is terminal-state diagnostic simulation evidence only. It is not a
  strict paper-equivalent claim, path or stitched recovery, a robustness proof,
  contact-model calibration, or hardware evidence.

## V70 Positive Relaxed Orientation Recovery Audit

### Positive-side recovery with a run-local `0.12 rad` orientation gate

- Run:
  - `runs/positive_relaxed_orientation_recovery/20260524T172909`
- Command:
  `scripts/audit_positive_relaxed_orientation_recovery.py`
- Git state at run time:
  parent commit `d8232b91a3c6e2a00c7e5a8432928f5ba3fc6d43` with dirty v70
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, `git_state.md`, and
  the run-local `relaxed_stage_a_target_config.yaml`, plus per-case start,
  terminal, path, and stitched metrics/summaries/commands under `cases/*`.
- Result:
  The relaxed-orientation audit evaluates `8` positive base-z deltas from
  `+0.05 mm` through `+1.0 mm`. With the run-local `0.12 rad` diagnostic
  orientation gate, start contact passes `8 / 8`, terminal feasibility passes
  `8 / 8`, and path geometry passes `8 / 8`. Stitched recovery remains `0 / 8`;
  Stage A passes at `15.0 s` and `16.0 s`, but Stage B handoff is `3 / 4`
  because `e2-figure-eight` fails qdot utilization criteria.
- Limit:
  This is diagnostic-label simulation evidence with a run-local relaxed target
  config only. It is not a canonical-config change, strict paper-equivalent
  claim, robustness proof, contact-model calibration, or hardware evidence.

## V71 Positive Stage B E2 Margin Audit

### E2 timing and qdot margin after v70 positive path recovery

- Run:
  - `runs/positive_stage_b_e2_margin/20260524T192129`
- Command:
  `scripts/audit_positive_stage_b_e2_margin.py`
- Git state at run time:
  parent commit `0c03cf3ff25c7945efff2ad2d74a0b3d3967ad74` with dirty v71
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-delta E2 timing-sweep metrics/summaries/commands under `cases/*`
  and qdot-only probe artifacts under `qdot_probe/*`.
- Result:
  The audit reuses the v70 run-local `0.12 rad` relaxed target config and
  positive path CSV artifacts. E2 passes `0 / 8` positive deltas at
  `paper_time_scale = 0.01`, `7 / 8` at `0.0075`, and `8 / 8` at `0.005` and
  `0.0025`. At original `0.01` timing, the `+1.0 mm` qdot-limit-only probe
  still fails up to `0.25 rad/s` because max orientation error remains just
  above `0.12 rad`.
- Limit:
  This is diagnostic-label E2 Stage B margin evidence only. It is not a full
  E1-E4 stitched recovery claim, canonical-config change, strict
  paper-equivalent claim, robustness proof, contact-model calibration, or
  hardware evidence.

## V72 Positive Full Stitched Recovery Audit

### Full E1-E4 stitched positive recovery at the E2-safe timing

- Run:
  - `runs/positive_full_stitched_recovery/20260524T192854`
- Command:
  `scripts/audit_positive_full_stitched_recovery.py`
- Git state at run time:
  parent commit `121ad38c0268faeafe8e1daded8015de8f25639c` with dirty v72
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-delta full E1-E4 stitched metrics/summaries/commands under
  `cases/*`.
- Result:
  The audit reuses the v70 run-local `0.12 rad` relaxed target config and
  positive path CSV artifacts, then evaluates all E1-E4 trajectories at
  `paper_time_scale = 0.005`. Stitched recovery passes `8 / 8` positive deltas
  through `+1.0 mm`; every row has Stage A passing and Stage B handoff
  `4 / 4`. Max Stage B qdot saturation fraction is `0.006`, and max Stage B
  orientation error is `0.1199788204275829 rad`.
- Limit:
  This is diagnostic-label full positive stitched evidence only. It depends on
  a run-local relaxed orientation gate and slowed Stage B timing, and is not a
  canonical-config change, strict paper-equivalent claim, robustness proof,
  contact-model calibration, or hardware evidence.

## V73 Positive Stitched Sensitivity Audit

### Compact sensitivity around the recovered v72 positive stitched policy

- Run:
  - `runs/positive_stitched_sensitivity/20260524T193845`
- Command:
  `scripts/audit_positive_stitched_sensitivity.py`
- Git state at run time:
  parent commit `02a2e7ebd473cb05e0fd960df7bb38783e78b11a` with dirty v73
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, `git_state.md`, a
  run-local tightened orientation config under `configs/`, and per-scenario
  E1-E4 stitched metrics/summaries/commands under `scenarios/*/cases/*`.
- Result:
  The audit reuses the v70 run-local relaxed target config and positive path
  CSV artifacts unless a scenario explicitly writes a run-local config copy.
  The compact matrix passes `37 / 40` stitched cells. `nominal_v72` and
  `stage_a_14p5s` pass all eight positive deltas. `qdot012_stage_a18s` fails
  `+0.2 mm` on Stage A final tracking, `paper_time_scale_0p0075` fails
  `+1.0 mm` on E2 qdot/orientation, and `orientation_gate_0p119` fails
  `+1.0 mm` on orientation gates.
- Limit:
  This is diagnostic-label positive stitched sensitivity evidence only. It is
  not a canonical-config change, strict paper-equivalent claim, robustness
  proof, contact-model calibration, or hardware evidence.

## V74 Qdot012 Stage A Margin Audit

### Focused duration margin for the v73 qdot012 +0.2 mm failure

- Run:
  - `runs/qdot012_stage_a_margin/20260524T194817`
- Command:
  `scripts/audit_qdot012_stage_a_margin.py`
- Git state at run time:
  parent commit `b0da94bddc277914dd4f7d58639327522ae6bfa5` with dirty v74
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-duration E1-E4 stitched metrics/summaries/commands under `cases/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, `qdot_limit_rad_s = 0.12`,
  `paper_time_scale = 0.005`, and the `0.12 rad` orientation gate fixed for
  the `+0.2 mm` cell. Stage B passes `4 / 4` for every tested duration. Stage A
  final tracking fails through `18.03 s` and first passes at `18.035 s`.
- Limit:
  This is diagnostic-label qdot012 Stage A duration margin evidence only. It
  does not recover the v73 faster-timing or tighter-orientation `+1.0 mm`
  sensitivity failures and is not a canonical-config change, strict
  paper-equivalent claim, robustness proof, contact-model calibration, or
  hardware evidence.

## V75 Qdot012 Positive Stitched Matrix

### Full positive matrix with qdot012 and the v74 duration margin

- Run:
  - `runs/positive_full_stitched_recovery/20260524T195501`
- Command:
  `scripts/audit_positive_full_stitched_recovery.py --stage-a-duration-s 18.035 --qdot-limit-rad-s 0.12 --paper-time-scale 0.005 --max-orientation-error-rad 0.12`
- Git state at run time:
  parent commit `d904e0f2ec38d116f0a8103a9014d6283fde8a1e` with dirty v75
  report/docs/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-delta full E1-E4 stitched metrics/summaries/commands under
  `cases/*`.
- Result:
  The audit folds the v74 `18.035 s` Stage A duration into all positive deltas
  with `qdot_limit_rad_s = 0.12`. Stitched recovery passes `8 / 8` through
  `+1.0 mm`; every row has Stage B handoff `4 / 4`. Max Stage B qdot
  saturation fraction is `0.001`, and max Stage B orientation error is
  `0.11997895388586574 rad`.
- Limit:
  This is diagnostic-label qdot012 positive stitched evidence only. It does not
  recover the v73 faster-timing or tighter-orientation `+1.0 mm` sensitivity
  failures and is not a canonical-config change, strict paper-equivalent claim,
  robustness proof, contact-model calibration, or hardware evidence.

## V76 Positive Timing Boundary Audit

### Focused timing boundary for the v73 `+1.0 mm` faster-timing failure

- Run:
  - `runs/positive_timing_boundary/20260524T200236`
- Command:
  `scripts/audit_positive_timing_boundary.py`
- Git state at run time:
  parent commit `ee8a5199e22b009c1e8d82901444cb22c148e692` with dirty v76
  report/code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  plus per-timing stitched metrics/summaries/commands under `cases/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `qdot_limit_rad_s = 0.15`, and the `0.12 rad` diagnostic orientation
  gate fixed for the `+1.0 mm` cell. Stage A passes all nine timing cases.
  Stitched recovery passes at `paper_time_scale = 0.005` and `0.0052`, then
  first fails at `0.0054` on E2 orientation just above the gate. At `0.007`
  and `0.0075`, the same E2 row also has severe qdot saturation and tail qdot
  utilization failures.
- Limit:
  This is diagnostic-label timing-boundary evidence only. It bounds, but does
  not recover, the v73 faster-timing `+1.0 mm` failure under the same
  diagnostic orientation gate. It does not address the separate
  `orientation_gate_0p119` `+1.0 mm` limit and is not a canonical-config
  change, strict paper-equivalent claim, robustness proof, contact-model
  calibration, or hardware evidence.

## V77 Positive Orientation Gate Boundary Audit

### Focused orientation-gate boundary for the v73 `+1.0 mm` tightened-gate failure

- Run:
  - `runs/positive_orientation_gate_boundary/20260524T221842`
- Command:
  `scripts/audit_positive_orientation_gate_boundary.py`
- Git state at run time:
  parent commit `05a84809099e6a526d52e89c939a79b587ca9503` with dirty v77
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  run-local copied Stage A target configs under `configs/`, plus per-gate
  stitched metrics/summaries/commands under `cases/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `paper_time_scale = 0.005`, and `qdot_limit_rad_s = 0.15` fixed for
  the `+1.0 mm` cell. Stage A first passes at orientation gate `0.1195 rad`.
  Full stitched recovery still fails through `0.11997` and first passes at
  `0.11998`, because E2 has the maximum Stage B orientation error
  `0.1199788204275829 rad`.
- Limit:
  This is diagnostic-label orientation-boundary evidence only. It localizes,
  but does not remove, the tightened-orientation sensitivity margin. It is not
  a canonical-config change, strict paper-equivalent claim, robustness proof,
  contact-model calibration, or hardware evidence.

## V78 Stage B Orientation Kp Probe

### E2 orientation-feedback probe at the tightened gate

- Run:
  - `runs/stage_b_orientation_kp_probe/20260524T222953`
- Command:
  `scripts/audit_stage_b_orientation_kp_probe.py`
- Git state at run time:
  parent commit `31e3dfdcced6807232931d2e94e7a6383befac7a` with dirty v78
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  a run-local copied Stage A target config under `configs/`, plus per-qdot and
  per-`orientation_kp` E2 stitched metrics/summaries/commands under `cases/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, the `+1.0 mm` positive
  cell, `stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`, and a
  `0.11995 rad` Stage A/Stage B orientation gate fixed. Stage A passes
  `30 / 30` E2 probe cells, but stitched recovery passes `0 / 30`. Low
  `orientation_kp` values preserve qdot while failing orientation; gains that
  satisfy orientation fail qdot saturation and/or tail qdot utilization even
  with qdot limits up to `0.25 rad/s`.
- Limit:
  This is diagnostic-label E2 Stage B probe evidence only. It is not a
  canonical-config change, full E1-E4 stitched recovery, strict
  paper-equivalent claim, robustness proof, contact-model calibration, or
  hardware evidence.

## V79 Stage B Priority Recovery

### Localized tightened-gate recovery with planar-primary priority

- Run:
  - `runs/stage_b_priority_recovery/20260524T224404`
- Command:
  `scripts/audit_stage_b_priority_recovery.py`
- Git state at run time:
  parent commit `de2c2a8d024458a50099cc6fdc4024ed97a229fe` with dirty v79
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  a run-local copied Stage A target config under `configs/`, plus per-scenario
  E1-E4 stitched metrics/summaries/commands under `scenarios/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, the `+1.0 mm` positive
  cell, `stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`,
  `qdot_limit_rad_s = 0.15`, and a `0.11995 rad` Stage A/Stage B orientation
  gate fixed while comparing seven Stage B priority scenarios. Stage A passes
  every scenario. Stitched recovery passes `2 / 7` scenarios:
  `planar_normal30_kp0p001` and `planar_normal30_kp0p002`, each with Stage B
  handoff `4 / 4`. Linear-primary controls still fail, and neighboring
  planar-primary controls expose either E2 force loss or a return to the E2
  qdot/orientation boundary.
- Limit:
  This is localized diagnostic Stage B priority-formulation recovery evidence
  only. It is not a canonical-config change, full positive-delta matrix
  recovery, strict paper-equivalent claim, robustness proof, contact-model
  calibration, or hardware evidence.

## V80 Positive Planar-Priority Matrix

### Full positive-delta matrix with the recovered planar-primary formulation

- Run:
  - `runs/positive_planar_priority_matrix/20260524T225138`
- Command:
  `scripts/audit_positive_planar_priority_matrix.py`
- Git state at run time:
  parent commit `5a11a2505a2d864abbf6db8e2ded33c0c921a12b` with dirty v80
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  a run-local copied Stage A target config under `configs/`, plus per-scenario
  and per-delta E1-E4 stitched metrics/summaries/commands under
  `scenarios/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `paper_time_scale = 0.005`, `qdot_limit_rad_s = 0.15`, and a
  `0.11995 rad` Stage A/Stage B orientation gate fixed. Both v79 passing
  planar-primary scenarios pass all eight positive deltas through `+1.0 mm`;
  total stitched pass count is `16 / 16`.
- Limit:
  This is diagnostic-label full positive-delta matrix evidence for the
  planar-primary Stage B priority formulation only. It is not a canonical
  config change, faster-timing recovery, qdot012 tightened-gate recovery,
  strict paper-equivalent claim, robustness proof, contact-model calibration,
  or hardware evidence.

## V81 Planar-Priority Stress

### Timing and tightened-gate stress for the recovered planar-primary formulation

- Run:
  - `runs/planar_priority_stress/20260524T230109`
- Command:
  `scripts/audit_planar_priority_stress.py`
- Git state at run time:
  parent commit `44a8c70c61e07dd5f3e48beb55fc0043032adca5` with dirty v81
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  run-local copied Stage A target configs under `configs/`, plus per-group,
  per-scenario, and per-delta E1-E4 stitched metrics/summaries/commands under
  `groups/*`.
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, and `qdot_limit_rad_s = 0.15` fixed while testing the two v80
  planar-primary candidates. Total stitched pass count is `35 / 66`. Both
  candidates pass the focused `+1.0 mm` timing sweep through
  `paper_time_scale = 0.0065` and first fail at `0.007`. The full
  `paper_time_scale = 0.0075` stress fails `0 / 16` across both candidates.
  The `0.119 rad` gate stress passes through `+0.75 mm` but still fails
  `+1.0 mm` for both candidates.
- Limit:
  This is diagnostic-label stress evidence only. It is not a canonical config
  change, faster-timing recovery at `0.0075`, recovery of the `+1.0 mm`,
  `0.119 rad` gate, strict paper-equivalent claim, robustness proof,
  contact-model calibration, or hardware evidence.

## V82 Weighted Timing Recovery

### Faster-timing recovery with weighted zero-angular-command priority

- Run:
  - `runs/weighted_timing_recovery/20260524T231454`
- Command:
  `scripts/audit_weighted_timing_recovery.py`
- Git state at run time:
  parent commit `8f4a94ca9729a5eb626b0e73960a1e14f9dea608` with dirty v82
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  a run-local copied Stage A target config under `configs/`, plus per-scenario
  and per-delta E1-E4 stitched metrics/summaries/commands under
  `full_delta/*` and focused timing-sweep artifacts under `timing_sweep/*`.
- Result:
  Linear-primary passes `7 / 8` and still fails `+1.0 mm` on the
  `paper_time_scale = 0.0075`, `orientation_gate = 0.11995 rad` stress face.
  The two v80 planar-primary candidates each pass `0 / 8`. Both weighted
  zero-angular-command candidates, `weighted_kp0_normal1` and
  `weighted_kp0_normal30`, pass `8 / 8` through `+1.0 mm`. The focused
  `+1.0 mm` `weighted_kp0_normal1` timing sweep passes all tested values
  through `paper_time_scale = 0.01`.
- Limit:
  This is diagnostic-label faster-timing recovery evidence only. It is not a
  canonical controller default, recovery of the `0.119 rad` gate, proof of a
  full positive-delta `paper_time_scale = 0.01` matrix, strict
  paper-equivalent claim, robustness proof, contact-model calibration, or
  hardware evidence.

## V83 Weighted Gate/Time Matrix

### Full `0.01` timing matrix and tightened-gate boundary

- Run:
  - `runs/weighted_gate_time_matrix/20260524T232637`
- Command:
  `scripts/audit_weighted_gate_time_matrix.py`
- Git state at run time:
  parent commit `b72ecec06468cf527889d176fc553be764206307` with dirty v83
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`,
  run-local copied Stage A target configs under `configs/`, plus full-matrix
  stitched metrics/summaries/commands under `full_matrix/*` and focused
  gate-boundary artifacts under `gate_boundary/*`.
- Result:
  Both weighted zero-angular-command scenarios pass the full positive-delta
  `paper_time_scale = 0.01`, `orientation_gate = 0.11995 rad` matrix `8 / 8`
  through `+1.0 mm`. At `orientation_gate = 0.119 rad`, both tested timings
  pass through `+0.75 mm` but fail `+1.0 mm`. The focused `+1.0 mm` gate
  boundary first passes at `0.11955 rad` for `paper_time_scale = 0.0075` and
  `0.1196 rad` for `paper_time_scale = 0.01`.
- Limit:
  This is diagnostic-label timing/gate matrix evidence only. It is not a
  canonical controller default, recovery of the `+1.0 mm`, `0.119 rad` gate,
  strict paper-equivalent claim, robustness proof, contact-model calibration,
  or hardware evidence.

## V84 Weighted Orientation Model Sensitivity

### Attribute the remaining `0.119 rad` row

- Run:
  - `runs/weighted_orientation_model_sensitivity/20260524T233945`
- Command:
  `python3 scripts/audit_weighted_orientation_model_sensitivity.py`
- Git state at run time:
  parent commit `79c2dd7fae6f16532fa269a2eb75235cbf4f81a1` with dirty v84
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The audit reads the v83 weighted gate/time matrix and the v69 positive
  terminal orientation audit. Critical weighted rows exceed the `0.119 rad`
  gate by less than `0.00057 rad` with `0.0` qdot saturation. The
  contact-point versus legacy sphere-center geometry convention changes the
  +1.0 mm terminal orientation by `0.024227219479550713 rad`.
- Limit:
  This is diagnostic sensitivity evidence only. It is not a recovery of the
  `+1.0 mm`, `0.119 rad` gate, calibrated contact model, canonical controller
  default, strict paper-equivalent claim, robustness proof, or hardware
  evidence.

## V85 Contact Orientation Calibration Margin

### Physical/modeling correction size for the remaining orientation row

- Run:
  - `runs/contact_orientation_calibration_margin/20260524T235723`
- Command:
  `python3 scripts/audit_contact_orientation_calibration_margin.py`
- Git state at run time:
  parent commit `49083e145d0ff5b3741c40139527b772cd9345a7` with dirty v85
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The audit reads v84, v83, v69, and v77 source metrics plus the current
  contact/acceptance configs. The hardest remaining weighted `+1.0 mm`,
  `0.119 rad` row needs `0.0005664520369604714 rad`
  (`0.03245531101442353 deg`) of normal-orientation margin, equivalent to
  `0.014963398168061883 mm` (`14.963398168061882 um`) under the v84 terminal
  slope proxy. Existing metrics show scoped recovery at `0.11955`, `0.1196`,
  and `0.11995 rad`, but v85 does not accept any as replacement diagnostic
  gates. Branch push was verified at
  `e9603612a47fed63e19d9aa0f90bd925d2015991`.
- Limit:
  This is diagnostic calibration/definition margin evidence only. It is not a
  recovery of the `+1.0 mm`, `0.119 rad` gate, accepted gate relaxation,
  calibrated contact model, canonical controller default, strict
  paper-equivalent claim, robustness proof, or hardware evidence.

## V86 Measured Geometry Readiness

### Read-only local-record audit for the v85 calibration margin

- Run:
  - `runs/measured_geometry_readiness/20260525T000739`
- Command:
  `python3 scripts/audit_measured_geometry_readiness.py`
- Git state at run time:
  parent commit `3a97eac42688c09c1d26d253c6fa8630163716c9` with dirty v86
  audit code/artifacts under test.
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Source records inspected read-only:
  local lab-vault hardware state, EOAT TCP note, v13 EOAT verification JSON,
  contact-point config/MJCF, and v85 metrics.
- Result:
  Existing records do not support accepting the v85 `0.03246 deg` /
  `14.96 um` correction as calibrated evidence. The `85.0 mm` contact point is
  design metadata, the current UR TCP readback is temporary and not
  contact-validated, the KSM contact patch convention is unverified, the plane
  normal is analytic simulation geometry, and direct TCP DAQ force values still
  disagree with RTDE/PolyScope by about `32 N`. Branch push was verified at
  `70a1b35cf6436b284ed8bc8d1fcf936f9b0724a1`.
- Limit:
  This is read-only local-record readiness evidence only. It is not a recovery
  of the `+1.0 mm`, `0.119 rad` row, accepted gate relaxation, calibrated
  contact model, canonical controller default, strict paper-equivalent claim,
  robustness proof, hardware evidence, or hardware authorization.

## V87 Read-Only Calibration Measurement SOP

### Safety and evidence gates for future calibration measurements

- Artifact:
  - `reports/read_only_calibration_measurement_sop.md`
- Command:
  no live hardware command; documentation/SOP update only.
- Result:
  The SOP defines required artifacts, pass/fail gates, and abort conditions for
  mounted-stack TCP/contact point, KSM contact patch convention, plane normal
  in robot base frame, force-source/frame reconciliation, and orientation-gate
  semantics. It compares the required evidence directly to the v85
  `14.963398168061882 um` geometry margin and `0.03245531101442353 deg`
  normal-orientation margin.
- Limit:
  This is a planning/SOP artifact only. It is not an executed measurement,
  recovery, gate relaxation, calibrated contact model, canonical controller
  default, strict paper-equivalent claim, robustness proof, hardware evidence,
  or authorization for motion, writes, zeroing, or force control. Branch push
  was verified at `e60a90cfb112e4f5962c67efc2abbbcc3db313d0`.

## V88 Read-Only Calibration Measurement Templates

### Non-executed scaffold for future SOP evidence collection

- Template:
  - `templates/read_only_calibration_measurement/`
- Script:
  - `scripts/create_read_only_calibration_measurement_run.py`
- Run:
  - `runs/read_only_calibration_measurement/20260525T012234`
- Command:
  `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T012234`
- Tracked lightweight artifacts:
  `README.md`, `measurement_plan.md`, `operator_checklist.md`,
  `tcp_contact_measurements.csv`, `plane_normal_measurements.csv`,
  `force_source_comparison.csv`, `orientation_gate_decision.md`,
  `photos_manifest.md`, `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`.
- Result:
  The run is a template-only scaffold with status
  `scaffold_created_not_executed`. It records no live hardware access, no
  robot motion, no configuration writes, no zeroing/biasing, no force control,
  no gate relaxation, and no hardware-readiness claim. Branch push was
  verified at `67b486ef5b7b42c14ecf30e22dc1bb89014ec4c9`.
- Limit:
  This is not collected measurement evidence, not a calibrated contact model,
  not an accepted replacement orientation gate, not a strict paper-equivalent
  claim, and not hardware authorization.

## V89 Read-Only Calibration Measurement Run Audit

### Offline claim-boundary verifier for measurement run folders

- Script:
  - `scripts/audit_read_only_calibration_measurement_run.py`
- Run:
  - `runs/read_only_calibration_measurement_run_audit/20260525T012835`
- Command:
  `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --run-id 20260525T012835`
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The v88 scaffold run passed the offline audit with `audit_passed = true` and
  `violations = []`. The audit confirms no live hardware access, robot motion,
  configuration writes, zeroing/biasing, force control, gate relaxation, or
  hardware-readiness claim is present in the audited run. Branch push was
  verified at `ec3490654c6555f3d9713392edc0f7ebe76cdc36`.
- Limit:
  This is not collected measurement evidence, not a calibrated contact model,
  not an accepted replacement orientation gate, not a strict paper-equivalent
  claim, and not hardware authorization.

## V90 Read-Only Calibration Measurement Audit Modes

### Scaffold and approved-read-only audit profiles

- Script:
  - `scripts/audit_read_only_calibration_measurement_run.py`
- Run:
  - `runs/read_only_calibration_measurement_run_audit/20260525T013421`
- Command:
  `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --audit-mode scaffold --run-id 20260525T013421`
- Tracked lightweight artifacts:
  `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`.
- Result:
  The audit script now has explicit `scaffold` and `approved-read-only` modes.
  The v88 scaffold run passed in scaffold mode with `audit_passed = true` and
  `violations = []`. The approved-read-only path is covered by tests and still
  forbids robot motion, configuration writes, zeroing/biasing, force control,
  gate relaxation, and hardware-readiness claims. Branch push was verified at
  `aa4f48f8cb87d5af1f0051f65768fbc09e3c06ab`.
- Limit:
  This is not collected measurement evidence, not a calibrated contact model,
  not an accepted replacement orientation gate, not a strict paper-equivalent
  claim, and not hardware authorization.

## V91 Read-Only Calibration Measurement Evidence Finalizer

### Offline approval gate for worksheet-filled read-only runs

- Script:
  - `scripts/finalize_read_only_calibration_measurement_evidence.py`
- Report:
  - `reports/read_only_calibration_measurement_evidence_finalizer_report.md`
- Tests:
  - `tests/test_read_only_calibration_measurement_template.py`
- Command:
  `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
- Validation:
  Full tests passed with `121 passed in 4.01s`; `git diff --check` passed.
  Branch push was verified at
  `0121ea3c6815eacdddcad6c0f877d44f2dc7fe73`.
- Tracked lightweight artifacts:
  script, report, tests, updated decision/iteration/completion documentation,
  and `docs/goal_handoff_v92.md`.
- Result:
  The finalizer requires an exact approval phrase, approved step ID, operator,
  explicit `live_hardware_accessed` metadata, matching metrics YAML/JSON,
  default scaffold safety state, and worksheet CSV rows before converting a
  scaffold to `approved_read_only_evidence`. It derives evidence statuses from
  worksheet rows and self-checks with the v90 `approved-read-only` audit mode.
- Limit:
  No new live or physical measurement run was created. This is not collected
  measurement evidence, not a calibrated contact model, not an accepted
  replacement orientation gate, not a strict paper-equivalent claim, and not
  hardware authorization.

## V92 Read-Only Calibration Measurement Worksheet Coverage

### KSM contact patch and orientation semantics worksheets

- Template files:
  - `templates/read_only_calibration_measurement/ksm_contact_patch_convention.csv`
  - `templates/read_only_calibration_measurement/orientation_gate_semantics.csv`
- Scripts:
  - `scripts/audit_read_only_calibration_measurement_run.py`
  - `scripts/finalize_read_only_calibration_measurement_evidence.py`
- Runs:
  - `runs/read_only_calibration_measurement/20260525T014755`
  - `runs/read_only_calibration_measurement_run_audit/20260525T014756`
- Command:
  `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T014755`
- Audit command:
  `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T014755 --audit-mode scaffold --run-id 20260525T014756`
- Tracked lightweight artifacts:
  updated template files, scaffold run files, audit metrics/summary/git state,
  updated scripts/tests/docs, and
  `reports/read_only_calibration_measurement_worksheet_coverage_report.md`.
- Result:
  The updated scaffold includes explicit KSM and orientation semantics
  worksheets. The scaffold audit passed with `audit_passed = true`,
  `violations = []`, 14 lightweight files, and no heavy payloads.
- Validation:
  Full tests passed with `122 passed in 4.26s`; `git diff --check` passed.
  Branch push was verified at
  `11bfa3ac02a06cf184343e119739e2392ae9cfbf`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, and not hardware authorization.

## V93 Read-Only Calibration Measurement Orientation Acceptance Boundary

### Evidence-only orientation semantics and not-accepted gate state

- Template files:
  - `templates/read_only_calibration_measurement/metrics.yaml`
  - `templates/read_only_calibration_measurement/orientation_gate_decision.md`
- Scripts:
  - `scripts/audit_read_only_calibration_measurement_run.py`
  - `scripts/finalize_read_only_calibration_measurement_evidence.py`
- Runs:
  - `runs/read_only_calibration_measurement/20260525T015400`
  - `runs/read_only_calibration_measurement_run_audit/20260525T015401`
- Command:
  `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T015400`
- Audit command:
  `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T015400 --audit-mode scaffold --run-id 20260525T015401`
- Tracked lightweight artifacts:
  updated metrics template, orientation decision artifact, scaffold run files,
  audit metrics/summary/git state, updated scripts/tests/docs, and
  `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`.
- Result:
  The updated scaffold includes `orientation_gate_acceptance` with
  `decision = not_accepted`, `evidence_only = true`, and accepted-gate fields
  null. The scaffold audit passed with `audit_passed = true`,
  `violations = []`, 14 lightweight files, and no heavy payloads.
- Validation:
  Full tests passed with `123 passed in 4.43s`; `git diff --check` passed.
  Branch push was verified at
  `b8246d247734c5df5a3d0c3f056d4ac60b25729c`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, and not hardware authorization.

## V94 Orientation Gate-Acceptance Review Template

### Separate non-default review path for future gate decisions

- Template:
  - `templates/orientation_gate_acceptance_review/`
- Scripts:
  - `scripts/create_orientation_gate_acceptance_review.py`
  - `scripts/audit_orientation_gate_acceptance_review.py`
- Runs:
  - `runs/orientation_gate_acceptance_review/20260525T020054`
  - `runs/orientation_gate_acceptance_review_audit/20260525T020055`
- Command:
  `python3 scripts/create_orientation_gate_acceptance_review.py --review-id 20260525T020054`
- Audit command:
  `python3 scripts/audit_orientation_gate_acceptance_review.py runs/orientation_gate_acceptance_review/20260525T020054 --run-id 20260525T020055`
- Tracked lightweight artifacts:
  review template files, scaffold review files, audit metrics/summary/git
  state, scripts/tests/docs, and
  `reports/orientation_gate_acceptance_review_template_report.md`.
- Result:
  The review scaffold is separate from read-only evidence finalization,
  defaults to `review_scaffold_not_executed`, keeps source evidence null, keeps
  `orientation_gate_acceptance.decision = not_accepted`, and preserves gate
  relaxation and hardware readiness false. The audit passed with
  `audit_passed = true`, `violations = []`, 7 lightweight files, and no heavy
  payloads.
- Validation:
  Full tests passed with `126 passed in 4.72s`; `git diff --check` passed.
  Branch push was verified at
  `777e3b2c86ca51394c03aea74220cca0f3be284a`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, and not hardware authorization.

## V95 Offline Completion Blockers

### Structured classification of remaining requirements

- Script:
  - `scripts/audit_offline_completion_blockers.py`
- Run:
  - `runs/offline_completion_blockers/20260525T020734`
- Report:
  - `reports/offline_completion_blockers_report.md`
- Tests:
  - `tests/test_offline_completion_blockers.py`
- Command:
  `python3 scripts/audit_offline_completion_blockers.py --run-id 20260525T020734`
- Tracked lightweight artifacts:
  metrics, JSON mirror, summary, git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The audit reports `overall_goal_complete = false`,
  `completion_blocked = true`, and `do_not_mark_goal_complete = true`. It marks
  strict paper-equivalent full staged feasibility and robustness as non-final
  offline-actionable, while approved read-only evidence, calibrated contact
  geometry, orientation-gate acceptance, and hardware readiness remain blocked
  on explicit approval/evidence.
- Validation:
  Full tests passed with `128 passed in 4.80s`; `git diff --check` passed.
  Branch push was verified at
  `af1fa3f793219afefcf4b0c97bc825ef473adda4`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V96 Strict Feasibility Blockers

### Strict setup terminal tradeoff audit

- Script:
  - `scripts/audit_strict_feasibility_blockers.py`
- Run:
  - `runs/strict_feasibility_blockers/20260525T051640`
- Report:
  - `reports/strict_feasibility_blockers_report.md`
- Tests:
  - `tests/test_strict_feasibility_blockers.py`
- Command:
  `python3 scripts/audit_strict_feasibility_blockers.py --run-id 20260525T051640`
- Tracked lightweight artifacts:
  metrics, JSON mirror, summary, git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The audit reports `strict_feasibility_complete = false`,
  `strict_setup_gate_complete = false`, strict full staged feasibility
  `0 / 4`, three-phase setup terminal state `0 / 10`, three-phase trajectory
  feasibility `8 / 10`, `primary_blocker =
  strict_setup_terminal_tradeoff`, and `do_not_mark_goal_complete = true`.
- Validation:
  Full tests passed with `130 passed in 5.04s`; `git diff --check` passed.
  Branch push was verified at
  `31bcca912b2623bd4f29850077ab86a76ec1ec4e`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V97 Robustness Blockers

### Accepted-model robustness gap audit

- Script:
  - `scripts/audit_robustness_blockers.py`
- Run:
  - `runs/robustness_blockers/20260525T052457`
- Report:
  - `reports/robustness_blockers_report.md`
- Tests:
  - `tests/test_robustness_blockers.py`
- Command:
  `python3 scripts/audit_robustness_blockers.py --run-id 20260525T052457`
- Tracked lightweight artifacts:
  metrics, JSON mirror, summary, git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The audit reports `robustness_complete = false`, baseline diagnostic
  stitched sensitivity `4 / 9`, positive stitched sensitivity `37 / 40`,
  `primary_blocker = accepted_model_robustness_not_closed`, and
  `do_not_mark_goal_complete = true`.
- Validation:
  Full tests passed with `132 passed in 5.44s`; `git diff --check` passed.
  Branch push was verified at
  `f74c3719d4770e21604ae0087d8b27cc22e4b7d9`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V98 Diagnostic Robustness Matrix Candidate

### Candidate matrix over current diagnostic robustness evidence

- Script:
  - `scripts/audit_diagnostic_robustness_matrix_candidate.py`
- Run:
  - `runs/diagnostic_robustness_matrix_candidate/20260525T053101`
- Report:
  - `reports/diagnostic_robustness_matrix_candidate_report.md`
- Tests:
  - `tests/test_diagnostic_robustness_matrix_candidate.py`
- Command:
  `python3 scripts/audit_diagnostic_robustness_matrix_candidate.py --run-id 20260525T053101`
- Tracked lightweight artifacts:
  metrics, JSON mirror, summary, git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The audit reports `candidate_matrix_complete = false`,
  `accepted_as_robustness_proof = false`, 12 cells total, 7 diagnostic passes,
  1 non-final diagnostic recovery, 4 failed cells, and
  `do_not_mark_goal_complete = true`.
- Validation:
  Full tests passed with `134 passed in 5.59s`; `git diff --check` passed.
  Branch push was verified at
  `9d284be82583ba88cb76fbc3a21cfabf29c8ca50`.
- Limit:
  No live or physical measurement was collected. This is not a calibrated
  contact model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V99 Failed Diagnostic Robustness Experiment Matrix

### Planned offline commands for failed v98 cells

- Script:
  - `scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
- Run:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909`
- Report:
  - `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- Tests:
  - `tests/test_failed_diagnostic_robustness_experiment_matrix.py`
- Command:
  `python3 scripts/create_failed_diagnostic_robustness_experiment_matrix.py --run-id 20260525T053909`
- Tracked lightweight artifacts:
  metrics, JSON mirror, summary, executable `commands.sh`, git state, report,
  tests, and updated planning/decision/manifest documentation.
- Result:
  The run reports `status = planned_not_executed`, `experiment_count = 4`,
  and `planned_not_executed_count = 4`. It maps the four failed v98 cells to
  focused offline commands and preserves `do_not_mark_goal_complete = true`.
- Validation:
  Full tests passed with `136 passed in 5.75s`; YAML anchor check found no
  anchors in the generated metrics; `git diff --check` passed. Branch push
  was verified at `f81df802cede561528849dc886b303ad3d5e63dc`.
- Limit:
  No live or physical measurement was collected. No planned experiment command
  was executed. This is not a calibrated contact model, not an accepted
  replacement orientation gate, not a strict paper-equivalent claim, not a
  robustness proof, and not hardware authorization.

## V100 Base-Z Failed-Cell Execution Audit

### Executed `base_z_plus1mm` planned command and comparison audit

- Scripts:
  - `scripts/audit_stage_a_base_z_bracket.py`
  - `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T054646`
- Report:
  - `reports/failed_diagnostic_robustness_experiment_execution_report.md`
- Tests:
  - `tests/test_failed_diagnostic_robustness_experiment_execution.py`
- Executed command:
  `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_base_z_bracket.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm --base-z-deltas-mm 1.0 --stage-a-durations-s 15.0,16.0,18.0`
- Audit command:
  `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T054646`
- Tracked lightweight artifacts:
  experiment metrics/summary/git state, audit metrics/summary/git state,
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The executed `base_z_plus1mm` cell remains unresolved. The audit reports
  `executed_cell_count = 1`, `closed_cell_count = 0`,
  `not_executed_cell_count = 3`, `all_failed_cells_closed = false`,
  start pass count `0`, terminal pass count `0`, path geometry pass count `0`,
  and duration recovery count `0`.
- Validation:
  Full tests passed with `138 passed in 5.87s`; YAML anchor check found no
  anchors in the generated metrics; `git diff --check` passed. Branch push
  was verified at `ce48bcef63a1fa5f3c3969530774cfe59c6275b9`.
- Limit:
  No live or physical measurement was collected. Only one planned experiment
  command was executed. This is not a calibrated contact model, not an accepted
  replacement orientation gate, not a strict paper-equivalent claim, not a
  robustness proof, and not hardware authorization.

## V101 Positive Fast-Timing Failed-Cell Execution

### Executed `positive_fast_timing_0p0075` planned command and audit update

- Scripts:
  - `scripts/audit_positive_stitched_sensitivity.py`
  - `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T055322`
- Report:
  - `reports/positive_fast_timing_failed_cell_execution_report.md`
- Tests:
  - `tests/test_failed_diagnostic_robustness_experiment_execution.py`
- Executed command:
  `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_stitched_sensitivity.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075 --base-z-deltas-mm 1.0 --scenarios paper_time_scale_0p0075`
- Audit command:
  `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T055322`
- Tracked lightweight artifacts:
  experiment metrics/summary/git state, audit metrics/summary/git state,
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The executed `positive_fast_timing_0p0075` cell remains unresolved. The
  audit reports `executed_cell_count = 2`, `closed_cell_count = 0`,
  `not_executed_cell_count = 2`, `all_failed_cells_closed = false`; the fast
  timing row has Stage A pass true, stitched pass false, and E2 fails qdot
  saturation, tail qdot utilization, and orientation.
- Validation:
  Focused execution-audit tests passed with `3 passed in 0.20s`; YAML anchor
  check found no anchors in the generated metrics; full tests passed with
  `139 passed in 5.89s`; `git diff --check` passed. Branch push was verified
  at `7bd28a07a3eb4fe9a1122b9397b156a25401d33f`.
- Limit:
  No live or physical measurement was collected. Two planned experiment
  commands have now been executed. This is not a calibrated contact model, not
  an accepted replacement orientation gate, not a strict paper-equivalent
  claim, not a robustness proof, and not hardware authorization.

## V102 Positive Orientation-Gate Failed-Cell Execution

### Executed `positive_orientation_gate_0p119` planned command and audit update

- Scripts:
  - `scripts/audit_positive_orientation_gate_boundary.py`
  - `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T060119`
- Report:
  - `reports/positive_orientation_gate_failed_cell_execution_report.md`
- Tests:
  - `tests/test_positive_orientation_gate_boundary.py`
  - `tests/test_failed_diagnostic_robustness_experiment_execution.py`
- Executed command:
  `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_orientation_gate_boundary.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119 --base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12`
- Audit command:
  `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T060119`
- Tracked lightweight artifacts:
  experiment metrics/summary/configs/git state, audit metrics/summary/git
  state, report, tests, and updated planning/decision/manifest documentation.
- Result:
  The executed `positive_orientation_gate_0p119` cell remains unresolved. The
  audit reports `executed_cell_count = 3`, `closed_cell_count = 0`,
  `not_executed_cell_count = 1`, `all_failed_cells_closed = false`; the
  current `0.119 rad` gate fails, while the diagnostic boundary first passes
  at `0.11998 rad`, which is not an accepted replacement gate.
- Validation:
  Focused execution-audit tests passed with `6 passed in 0.48s`; YAML anchor
  check found no anchors in the generated metrics; full tests passed with
  `142 passed in 6.06s`; `git diff --check` passed. Branch push was verified
  at `5f7b30e7009296ca8153a020bd1475fec0b6dabd`.
- Limit:
  No live or physical measurement was collected. Three planned experiment
  commands have now been executed. This is not a calibrated contact model, not
  an accepted replacement orientation gate, not a strict paper-equivalent
  claim, not a robustness proof, and not hardware authorization.

## V103 Weighted +1.0 mm Gate Failed-Cell Execution

### Executed `weighted_plus1mm_0p119_gate` planned command and audit update

- Scripts:
  - `scripts/audit_weighted_gate_time_matrix.py`
  - `scripts/audit_weighted_timing_recovery.py`
  - `scripts/audit_stage_b_priority_recovery.py`
  - `scripts/audit_positive_stitched_sensitivity.py`
  - `scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328`
- Report:
  - `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- Tests:
  - `tests/test_weighted_gate_time_matrix.py`
  - `tests/test_failed_diagnostic_robustness_experiment_execution.py`
- Executed command:
  `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_weighted_gate_time_matrix.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate --base-z-deltas-mm 1.0 --boundary-base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995`
- Audit command:
  `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T061328`
- Tracked lightweight artifacts:
  experiment metrics/summary/configs/git state, audit metrics/summary/git
  state, report, tests, and updated planning/decision/manifest documentation.
- Result:
  The executed `weighted_plus1mm_0p119_gate` cell remains unresolved. The
  audit reports `executed_cell_count = 4`, `closed_cell_count = 0`,
  `not_executed_cell_count = 0`, `all_failed_cells_closed = false`; the
  current `0.119 rad` weighted rows fail, while diagnostic boundaries first
  pass at `0.11955 rad` and `0.1196 rad`, neither accepted as a replacement
  gate.
- Validation:
  Focused execution-audit tests passed with `6 passed in 0.96s`; YAML anchor
  check found no anchors in the generated metrics; full tests passed with
  `144 passed in 6.60s`; `git diff --check` passed. Branch push was verified
  at `ce266165b9ec3e47dbe6fdcce3cb0c717b8dda15`.
- Limit:
  No live or physical measurement was collected. All four planned experiment
  commands have now been executed. This is not a calibrated contact model, not
  an accepted replacement orientation gate, not a strict paper-equivalent
  claim, not a robustness proof, and not hardware authorization.

## V104 Plus1mm Unresolved Diagnostic Probe

### Classified remaining `+1.0 mm` blocker signatures

- Scripts:
  - `scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
- Runs:
  - `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`
- Report:
  - `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- Tests:
  - `tests/test_plus1mm_unresolved_diagnostic_probe.py`
- Command:
  `python3 scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
- Tracked lightweight artifacts:
  probe metrics/summary/git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The probe reads the v103 execution audit and all four executed failed-cell
  experiment metrics. It reports planned failed cells `4`, executed cells `4`,
  closed cells `0`, not-executed cells `0`, unresolved cells `4`, and
  `probe_closes_failed_cells = false`. The only qdot-limited cell is
  `positive_fast_timing_0p0075`; weighted current-gate rows have max qdot
  saturation `0.0` and remain orientation-margin/gate-acceptance blocked.
- Validation:
  Focused tests passed with `2 passed in 0.22s`; YAML anchor check found no
  anchors in the generated metrics; full tests passed with
  `146 passed in 6.74s`; `git diff --check` passed. Branch push was verified
  at `b412ddf5bbec20682ce021b754aa0efc845a3372`.
- Limit:
  No live or physical measurement was collected. This is a post-hoc offline
  audit over existing metrics only. It is not a calibrated contact model, not
  an accepted replacement orientation gate, not a strict paper-equivalent
  claim, not a robustness proof, and not hardware authorization.

## V105 Positive Fast-Timing E2 Qdot Isolation

### Isolated qdot-limit effects on the `+1.0 mm` fast E2 row

- Scripts:
  - `scripts/audit_positive_stage_b_e2_margin.py`
- Runs:
  - `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019`
- Report:
  - `reports/positive_fast_timing_e2_qdot_isolation_report.md`
- Tests:
  - `tests/test_positive_stage_b_e2_margin.py`
- Command:
  `python3 scripts/audit_positive_stage_b_e2_margin.py --output-dir runs/positive_fast_timing_e2_qdot_isolation/20260525T063019 --base-z-deltas-mm 1.0 --paper-time-scales 0.0075,0.007,0.0065,0.006,0.0055,0.0052,0.005 --qdot-probe-limits-rad-s 0.15,0.18,0.2,0.25,0.3`
- Tracked lightweight artifacts:
  probe metrics/summary/git state, report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The first tested E2 timing pass is `paper_time_scale = 0.0052`. Qdot-only
  probes at `paper_time_scale = 0.0075` fail `0 / 5` through `0.3 rad/s`:
  qdot saturation can be reduced to `0.0`, but orientation remains above the
  run-local `0.12 rad` gate.
- Validation:
  Focused tests passed with `1 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; full tests passed with
  `147 passed in 6.86s`; `git diff --check` passed. Branch push was verified
  at `6cc6733a3ac78b93090d4079b62480ade57e82a7`.
- Limit:
  No live or physical measurement was collected. This is E2-only diagnostic
  simulation and does not close the v99 `positive_fast_timing_0p0075` failed
  cell. It is not a calibrated contact model, not an accepted replacement
  orientation gate, not a strict paper-equivalent claim, not a robustness
  proof, and not hardware authorization.

## V106 Positive Fast E2 Orientation-Margin Probe

### Probed fixed-gate priority recovery on the `+1.0 mm` fast E2 row

- Scripts:
  - `scripts/audit_positive_fast_e2_orientation_margin.py`
- Runs:
  - `runs/positive_fast_e2_orientation_margin/20260525T063817`
- Report:
  - `reports/positive_fast_e2_orientation_margin_report.md`
- Tests:
  - `tests/test_positive_fast_e2_orientation_margin.py`
- Command:
  `python3 scripts/audit_positive_fast_e2_orientation_margin.py --output-dir runs/positive_fast_e2_orientation_margin/20260525T063817`
- Tracked lightweight artifacts:
  probe metrics/summary/git state, per-scenario lightweight metrics and
  command logs, report, tests, and updated planning/decision/manifest
  documentation.
- Result:
  The E2-only matrix keeps `paper_time_scale = 0.0075`, `qdot_limit = 0.15
  rad/s`, and the `0.12 rad` orientation gate fixed. Weighted rows pass E2
  (`2 / 6` scenarios) with `max_orientation_error_rad =
  0.11954627160547111`, qdot saturation `0.0`, tail qdot utilization
  `0.5177926211135458`, and tail mean absolute force error
  `0.0008094383419582085 N`.
- Validation:
  Focused tests passed with `1 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `148 passed in 6.81s`; `git diff --check` passed.
  Branch push was verified at
  `716ecde74a428c15ce17445018ca7028b1db9527`.
- Limit:
  No live or physical measurement was collected. This is E2-only diagnostic
  simulation and does not close the v99 `positive_fast_timing_0p0075` failed
  cell. It is not a canonical controller change, not a calibrated contact
  model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V107 Positive Fast Weighted Full-Cell Probe

### Ran exact fixed-gate E1-E4 fast face with weighted priority

- Scripts:
  - `scripts/audit_positive_fast_weighted_full_cell.py`
- Runs:
  - `runs/positive_fast_weighted_full_cell/20260525T064719`
- Report:
  - `reports/positive_fast_weighted_full_cell_report.md`
- Tests:
  - `tests/test_positive_fast_weighted_full_cell.py`
- Command:
  `python3 scripts/audit_positive_fast_weighted_full_cell.py --output-dir runs/positive_fast_weighted_full_cell/20260525T064719`
- Tracked lightweight artifacts:
  probe metrics/summary/git state, per-scenario lightweight metrics and
  command logs, report, tests, and updated planning/decision/manifest
  documentation.
- Result:
  The full E1-E4 matrix keeps `paper_time_scale = 0.0075`, `qdot_limit =
  0.15 rad/s`, and the `0.12 rad` orientation gate fixed. The linear-primary
  baseline still fails E2 with orientation `0.12020305872871904`, qdot
  saturation `0.999`, and tail qdot utilization `1.0`. Both weighted scenarios
  pass `4 / 4` with maximum Stage B orientation `0.11954627160547111`, qdot
  saturation `0.0`, tail qdot utilization `0.5177926211135458`, and tail mean
  absolute force error `0.0008422275835027282 N`.
- Validation:
  Focused tests passed with `2 passed in 0.12s`; YAML anchor check found no
  anchors in the root summary metrics; raw/heavy artifact scan found no
  payloads; full tests passed with `150 passed in 6.79s`; `git diff --check`
  passed.
  Branch push was verified at
  `2e94f4bbd9ac25228c819bdc789eb6bc1f75f719`.
- Limit:
  No live or physical measurement was collected. This is full-cell diagnostic
  simulation for one face and does not close the original v99
  `positive_fast_timing_0p0075` failed cell because `weighted` has not been
  accepted as a canonical controller default. It is not a calibrated contact
  model, not an accepted replacement orientation gate, not a strict
  paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V108 Base-Z Plus1mm Split Audit

### Split start-contact, terminal-orientation, path, and handoff blockers

- Scripts:
  - `scripts/audit_base_z_plus1mm_split.py`
- Runs:
  - `runs/base_z_plus1mm_split/20260525T071440`
- Report:
  - `reports/base_z_plus1mm_split_report.md`
- Tests:
  - `tests/test_base_z_plus1mm_split.py`
- Command:
  `python3 scripts/audit_base_z_plus1mm_split.py --output-dir runs/base_z_plus1mm_split/20260525T071440`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The exact v99 `base_z_plus1mm` command remains `executed_unresolved`, but
  the post-hoc split narrows the blockers. Broader seeds recover start contact
  at `+1.0 mm`; terminal force/x-y/contact passes; terminal orientation
  `0.11948560786548146 rad` exceeds the current `0.08 rad` diagnostic gate;
  the run-local `0.12 rad` gate recovers terminal/path with minimum path
  duration `10.018584837157274 s`; stitched Stage B remains unrecovered with
  handoff counts `3 / 4` at both tested durations.
- Validation:
  Focused tests passed with `3 passed in 0.09s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `153 passed in 7.22s`; `git diff --check` passed.
  Branch push was verified at
  `987e360d9244bf8c98ce549c21c7787ab163868a`.
- Limit:
  No live or physical measurement was collected. This is post-hoc diagnostic
  simulation bookkeeping over existing metrics and does not close the v99
  `base_z_plus1mm` failed cell. It is not a calibrated contact model, not an
  accepted replacement orientation gate, not a canonical config change, not a
  strict paper-equivalent claim, not a robustness proof, and not hardware
  authorization.

## V109 Relaxed Base-Z Weighted Handoff Probe

### Tested weighted priority on the relaxed `base_z_plus1mm` handoff blocker

- Scripts:
  - `scripts/audit_relaxed_base_z_weighted_handoff.py`
- Runs:
  - `runs/relaxed_base_z_weighted_handoff/20260525T073012`
- Report:
  - `reports/relaxed_base_z_weighted_handoff_report.md`
- Tests:
  - `tests/test_relaxed_base_z_weighted_handoff.py`
- Command:
  `python3 scripts/audit_relaxed_base_z_weighted_handoff.py --output-dir runs/relaxed_base_z_weighted_handoff/20260525T073012`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  per-scenario lightweight metrics and command logs; report, tests, and
  updated planning/decision/manifest documentation.
- Result:
  The relaxed `base_z_plus1mm` handoff matrix keeps the v70 run-local
  `0.12 rad` orientation gate, `paper_time_scale = 0.01`, and
  `qdot_limit = 0.15 rad/s` fixed. The linear-primary baseline fails E2 at
  both tested Stage A durations with max orientation `0.12043140848858806`,
  qdot saturation `0.997`, and tail qdot utilization `1.0`. Both weighted
  scenarios pass `4 / 4` at both durations with maximum Stage B orientation
  `0.11956645203696047`, qdot saturation `0.0`, tail qdot utilization
  `0.520987929048311`, and tail mean absolute force error
  `0.0008424456782388923 N`.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `156 passed in 6.93s`; `git diff --check` passed.
  Branch push was verified at
  `3a766ae641d7d4cda70864da4cfad366786e6515`.
- Limit:
  No live or physical measurement was collected. This is diagnostic simulation
  using the run-local relaxed gate and does not close the v99
  `base_z_plus1mm` failed cell. It is not a calibrated contact model, not an
  accepted replacement orientation gate, not a canonical controller/config
  change, not a strict paper-equivalent claim, not a robustness proof, and not
  hardware authorization.

## V110 Weighted Priority Profile-Boundary Audit

### Named weighted priority as a diagnostic profile without canonical changes

- Scripts:
  - `scripts/audit_weighted_priority_profile_boundary.py`
- Runs:
  - `runs/weighted_priority_profile_boundary/20260525T074100`
- Report:
  - `reports/weighted_priority_profile_boundary_report.md`
- Tests:
  - `tests/test_weighted_priority_profile_boundary.py`
- Command:
  `python3 scripts/audit_weighted_priority_profile_boundary.py --output-dir runs/weighted_priority_profile_boundary/20260525T074100`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The post-hoc audit reads the verified v107 and v109 metrics and supports
  naming `weighted_zero_angular_stage_b_diagnostic` as a diagnostic profile for
  the covered faces. Across those faces, weighted rows recover all covered rows
  and baseline failures are reproduced. The boundary keeps
  `canonical_controller_change`, `canonical_orientation_gate_change`,
  `failed_cell_closed`, `robustness_claim`, and `hardware_readiness` false.
- Validation:
  Focused tests passed with `3 passed in 0.04s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `159 passed in 6.93s`; `git diff --check` passed.
  Branch push was verified at
  `f48240c72188e8d4fd4e18bd69fe37c38e1e1d90`.
- Limit:
  No live or physical measurement was collected. This is post-hoc diagnostic
  bookkeeping over existing metrics and does not change the canonical
  controller default, accept the `0.12 rad` orientation gate, close any
  original v99 failed cell, prove robustness, prove strict paper-equivalent
  feasibility, calibrate contact geometry, or authorize hardware work.

## V111 Weighted Profile Matrix Restatement

### Restated the v98/v99 matrix with the named weighted profile

- Scripts:
  - `scripts/audit_weighted_profile_matrix_restatement.py`
- Runs:
  - `runs/weighted_profile_matrix_restatement/20260525T075040`
- Report:
  - `reports/weighted_profile_matrix_restatement_report.md`
- Tests:
  - `tests/test_weighted_profile_matrix_restatement.py`
- Command:
  `python3 scripts/audit_weighted_profile_matrix_restatement.py --output-dir runs/weighted_profile_matrix_restatement/20260525T075040`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The post-hoc audit reads the v98 matrix, v99 failed-cell plan, v100-v103
  execution audit, and v110 profile boundary. It restates the matrix with
  `weighted_zero_angular_stage_b_diagnostic` as a non-canonical overlay:
  `base_z_plus1mm` and `positive_fast_timing_0p0075` have overlay support,
  while `positive_orientation_gate_0p119` and `weighted_plus1mm_0p119_gate`
  remain gate-acceptance blocked. Closed cells remain `0`, candidate matrix
  complete remains `false`, and accepted-as-robustness-proof remains `false`.
- Validation:
  Focused tests passed with `3 passed in 0.04s`; YAML anchor check found no
  anchors in the generated metrics after the no-alias YAML writer update;
  raw/heavy artifact scan found no payloads; full tests passed with
  `162 passed in 7.00s`; `git diff --check` passed.
  Branch push was verified at
  `7900d441e3d072026bdf0f874da98b322cf9628d`.
- Limit:
  No live or physical measurement was collected. This is post-hoc diagnostic
  bookkeeping over existing metrics and does not change the canonical
  controller default, accept the `0.12 rad` orientation gate, close any
  original v99 failed cell, prove robustness, prove strict paper-equivalent
  feasibility, calibrate contact geometry, or authorize hardware work.

## V112 Remaining Blocker Prioritization

### Ranked the remaining blockers using existing offline evidence

- Scripts:
  - `scripts/audit_remaining_blocker_prioritization.py`
- Runs:
  - `runs/remaining_blocker_prioritization/20260525T072557`
- Report:
  - `reports/remaining_blocker_prioritization_report.md`
- Tests:
  - `tests/test_remaining_blocker_prioritization.py`
- Command:
  `python3 scripts/audit_remaining_blocker_prioritization.py --output-dir runs/remaining_blocker_prioritization/20260525T072557`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The post-hoc audit reads existing v95-v111 metrics and ranks the six
  remaining blockers. The top blocker is
  `approved_read_only_calibration_evidence`. Four blockers require approval or
  live evidence, two blockers can advance offline only as non-final evidence,
  profile-overlay supported cells remain `2`, gate-acceptance blocked cells
  remain `2`, closed cells remain `0`, and `do_not_mark_goal_complete` remains
  `true`.
- Validation:
  Focused tests passed with `3 passed in 0.16s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `165 passed in 7.13s`; `git diff --check` passed.
  Branch push was verified at
  `8ed1b881fae6d27e815feecf0b59724f64cb2a9a`.
- Limit:
  No live or physical measurement was collected. This is post-hoc bookkeeping
  over existing metrics and does not accept a replacement orientation gate,
  change the canonical controller, close failed cells, prove robustness, prove
  strict paper-equivalent feasibility, calibrate contact geometry, or authorize
  hardware work.

## V113 Strict Feasibility Policy Probe

### Probed compact Stage A policies for the strict setup blocker

- Scripts:
  - `scripts/audit_strict_feasibility_policy_probe.py`
- Runs:
  - `runs/strict_feasibility_policy_probe/20260525T073519`
- Report:
  - `reports/strict_feasibility_policy_probe_report.md`
- Tests:
  - `tests/test_strict_feasibility_policy_probe.py`
- Command:
  `python3 scripts/audit_strict_feasibility_policy_probe.py --output-dir runs/strict_feasibility_policy_probe/20260525T073519`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The offline E2 policy probe tests eight Stage A policies and reports setup
  terminal-state pass `0 / 8`, trajectory feasibility pass `4 / 8`, planned
  setup-then-trajectory pass `0 / 8`, and full staged feasibility pass
  `0 / 8`. All eight setup rows violate qdot saturation and tail qdot
  utilization. The best x/y row still fails orientation, and the best
  orientation rows still fail x/y and setup qdot criteria.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `168 passed in 7.11s`; `git diff --check` passed.
  Branch push was verified at
  `98a6b3400901680ae2aeb51f9348963504606d9f`.
- Limit:
  No live or physical measurement was collected. This is offline simulation
  evidence and does not prove strict paper-equivalent feasibility, accept a
  replacement orientation gate, change the canonical controller, close failed
  cells, prove robustness, calibrate contact geometry, or authorize hardware
  work.

## V114 Strict Command-Limited Stage A Probe

### Tested command-limited Stage A before velocity allocation

- Scripts:
  - `scripts/audit_strict_command_limited_stage_a.py`
- Runs:
  - `runs/strict_command_limited_stage_a/20260525T074557`
- Report:
  - `reports/strict_command_limited_stage_a_report.md`
- Tests:
  - `tests/test_strict_command_limited_stage_a.py`
- Command:
  `python3 scripts/audit_strict_command_limited_stage_a.py --output-dir runs/strict_command_limited_stage_a/20260525T074557`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The offline command-limited probe changes Stage A command generation before
  allocation by lowering finite-time force gain, capping force-normal angular
  commands, and extending setup durations. It reports strict setup-chain pass
  `0 / 4`, trajectory feasibility pass `2 / 4`, planned
  setup-then-trajectory pass `0 / 4`, final x/y failures `4 / 4`, setup qdot
  saturation failures `4 / 4`, and setup tail qdot utilization failures
  `4 / 4`.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `171 passed in 7.16s`; `git diff --check`
  passed. Branch push was verified at `aaa42097f6778cc0b2c8617c9ffc21f57b5fbfb4`.
- Limit:
  No live or physical measurement was collected. This is offline simulation
  evidence and does not prove strict paper-equivalent feasibility, accept a
  replacement orientation gate, change the canonical controller, close failed
  cells, prove robustness, calibrate contact geometry, or authorize hardware
  work.

## V115 Explicit Stage A Constraint Probe

### Tested terminal/path constraints with qdot-timed setup paths

- Scripts:
  - `scripts/audit_explicit_stage_a_constraint_probe.py`
- Runs:
  - `runs/explicit_stage_a_constraint_probe/20260525T082500`
- Report:
  - `reports/explicit_stage_a_constraint_probe_report.md`
- Tests:
  - `tests/test_explicit_stage_a_constraint_probe.py`
- Command:
  `python3 scripts/audit_explicit_stage_a_constraint_probe.py --output-dir runs/explicit_stage_a_constraint_probe/20260525T082500`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The offline explicit-constraint probe uses the v56 contact-manifold terminal
  cases plus the v62 diagnostic contact-path tracking reference. It reports
  strict setup-path pass `0 / 5`, terminal strict-criteria pass `0 / 5`,
  qdot-criteria pass `5 / 5`, planned setup-then-trajectory pass `0 / 5`,
  terminal orientation failures `3 / 5`, terminal x/y failures `3 / 5`,
  terminal force/contact failures `1 / 5`, and strict paper-equivalent
  feasibility `false`.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `174 passed in 7.12s`; `git diff --check`
  passed. Branch push was verified at `315052286c42300dc9cf1665aec8a7b9279587bf`.
- Limit:
  No live or physical measurement was collected. This is offline simulation
  evidence and does not prove strict paper-equivalent feasibility, accept a
  replacement orientation gate, change the canonical controller, close failed
  cells, prove robustness, calibrate contact geometry, or authorize hardware
  work.

## V116 Strict Terminal Constrained Optimization

### Tested stronger terminal minimax optimization over the accepted contact model

- Scripts:
  - `scripts/audit_strict_terminal_constrained_optimization.py`
- Runs:
  - `runs/strict_terminal_constrained_optimization/20260525T085000`
- Report:
  - `reports/strict_terminal_constrained_optimization_report.md`
- Tests:
  - `tests/test_strict_terminal_constrained_optimization.py`
- Command:
  `python3 scripts/audit_strict_terminal_constrained_optimization.py --output-dir runs/strict_terminal_constrained_optimization/20260525T085000`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The offline strict terminal optimization audit seeds from the v56
  contact-manifold candidates and runs bounded smooth-minimax SLSQP/L-BFGS-B
  optimizers over normalized force, x/y, and orientation errors. It reports
  strict terminal pass `0 / 12`, optimizer success `10 / 12`, best max-gate
  ratio `2.11994927622362`, v56 strict best max-gate ratio
  `2.413534442118322`, and strict paper-equivalent feasibility `false`.
- Validation:
  Focused tests passed with `4 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `178 passed in 7.16s`; `git diff --check`
  passed. Branch push was verified at `b956ee36c659fb01bc23fc7d3db3e66bed9e8077`.
- Limit:
  No live or physical measurement was collected. This is offline simulation
  evidence and does not prove strict paper-equivalent feasibility, accept a
  replacement orientation gate, change the canonical controller, close failed
  cells, prove robustness, calibrate contact geometry, or authorize hardware
  work.

## V117 Contact Setup Target Acceptance Review Scaffold

### Added a non-default review path for contact/setup-target changes

- Templates:
  - `templates/contact_setup_target_acceptance_review/`
- Scripts:
  - `scripts/create_contact_setup_target_acceptance_review.py`
  - `scripts/audit_contact_setup_target_acceptance_review.py`
- Runs:
  - `runs/contact_setup_target_acceptance_review/20260525T091500`
  - `runs/contact_setup_target_acceptance_review_audit/20260525T091501`
- Report:
  - `reports/contact_setup_target_acceptance_review_template_report.md`
- Tests:
  - `tests/test_contact_setup_target_acceptance_review_template.py`
- Commands:
  - `python3 scripts/create_contact_setup_target_acceptance_review.py --review-id 20260525T091500`
  - `python3 scripts/audit_contact_setup_target_acceptance_review.py runs/contact_setup_target_acceptance_review/20260525T091500 --run-id 20260525T091501`
- Tracked lightweight artifacts:
  template files, scaffold top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; audit top-level `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The generated review records `review_scaffold_not_executed`, cites the v116
  terminal compatibility boundary, preserves `strict_terminal_pass_count = 0`,
  keeps `contact_setup_target_acceptance.decision = not_accepted`, and keeps
  support for contact-model update, setup-target update, force-source update,
  gate relaxation, hardware claim, contact calibration, hardware readiness, and
  goal completion false. The audit passed with `violations = []`.
- Validation:
  Focused tests passed with `3 passed in 0.35s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `181 passed in 7.50s`; `git diff --check`
  passed. Branch push was verified at
  `f89b1dc4be31b213a28b493a277137c14e1977a0`.
- Limit:
  No live or physical measurement was collected. This is offline scaffold and
  audit evidence only; it does not accept a contact model, accept a setup
  target, prove strict paper-equivalent feasibility, calibrate contact
  geometry, establish hardware readiness, or authorize hardware work.

## V118 Post-V117 Evidence Readiness Audit

### Scanned current evidence before any completion claim

- Scripts:
  - `scripts/audit_post_v117_evidence_readiness.py`
- Runs:
  - `runs/post_v117_evidence_readiness/20260525T092500`
- Report:
  - `reports/post_v117_evidence_readiness_report.md`
- Tests:
  - `tests/test_post_v117_evidence_readiness.py`
- Command:
  `python3 scripts/audit_post_v117_evidence_readiness.py --run-id 20260525T092500`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, and updated planning/decision/manifest documentation.
- Result:
  The audit scans current read-only measurement runs, read-only run audits,
  orientation-gate reviews, contact/setup-target reviews, strict terminal
  metrics, robustness restatement metrics, and the hardware gate report path.
  It reports `overall_goal_complete = false`, `completion_claim_allowed =
  false`, approved read-only runs `0`, passed approved-read-only audits `0`,
  accepted orientation reviews `0`, accepted contact/setup-target reviews `0`,
  strict terminal pass `0`, closed robustness cells `0`, no hardware gate
  report, and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.24s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `184 passed in 7.74s`; `git diff --check`
  passed. Branch push was verified at
  `a11668032fb01accde9ed55aaaf95c04b5465075`.
- Limit:
  No live or physical measurement was collected. This is offline bookkeeping
  only; it does not accept a contact model, accept a setup target, prove
  strict paper-equivalent feasibility, calibrate contact geometry, establish
  hardware readiness, or authorize hardware work.

## V119 Read-Only SOP Step Registry Finalizer Guard

### Added exact-step registry checks before approved-read-only finalization

- Config:
  - `configs/read_only_sop_step_registry.yaml`
- Scripts:
  - `scripts/audit_read_only_sop_step_registry.py`
  - `scripts/finalize_read_only_calibration_measurement_evidence.py`
  - `scripts/audit_read_only_calibration_measurement_run.py`
- Runs:
  - `runs/read_only_sop_step_registry_audit/20260525T094000`
- Report:
  - `reports/read_only_sop_step_registry_guard_report.md`
- Tests:
  - `tests/test_read_only_calibration_measurement_template.py`
- Command:
  `python3 scripts/audit_read_only_sop_step_registry.py --run-id 20260525T094000`
- Tracked lightweight artifacts:
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  report, tests, registry config, and updated planning/decision/manifest
  documentation.
- Result:
  The registry audit passes with `violations = []`, `6` exact step IDs, and `5`
  finalizer-eligible evidence steps. The finalizer and approved-read-only audit
  now require a registered finalizer-eligible step ID and reject worksheet rows
  outside that step's allowed worksheet scope.
- Validation:
  Focused tests passed with `12 passed in 2.34s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `188 passed in 8.24s`; `git diff --check`
  passed. Branch push was verified at
  `c1c8febca4a41009d1fb8b55e19cfbe64931c17b`.
- Limit:
  No live or physical measurement was collected. This is offline
  approval-scoping evidence only; it does not accept a contact model, accept a
  setup target, prove strict paper-equivalent feasibility, calibrate contact
  geometry, establish hardware readiness, or authorize hardware work.

## V120 Read-Only Step Approval Packet

### Added a not-approved exact-step approval packet for phase1

- Scripts:
  - `scripts/create_read_only_step_approval_packet.py`
  - `scripts/audit_read_only_step_approval_packet.py`
- Runs:
  - `runs/read_only_step_approval_packet/20260525T095500`
  - `runs/read_only_step_approval_packet_audit/20260525T095501`
- Report:
  - `reports/read_only_step_approval_packet_report.md`
- Tests:
  - `tests/test_read_only_step_approval_packet.py`
- Commands:
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase1_mounted_stack_tcp_contact_measurement --packet-id 20260525T095500`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T095500 --run-id 20260525T095501`
- Tracked lightweight artifacts:
  packet top-level `metrics.yaml`, `metrics.json`, `approval_packet.md`,
  `summary.md`, and `git_state.md`; audit top-level `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; report, tests, and updated
  planning/decision/manifest documentation.
- Result:
  The packet is for `phase1_mounted_stack_tcp_contact_measurement`, allows only
  `tcp_contact_measurements.csv`, is explicitly `not_approved`, and keeps
  packet/execution/live-access/readiness/goal-completion authorization false.
  The audit passed with `violations = []`.
- Validation:
  Focused tests passed with `4 passed in 0.32s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `192 passed in 8.56s`; `git diff --check`
  passed. Branch push was verified at
  `c897dfa467b823c8cf6fc68b54f290a29942a704`.
- Limit:
  No live or physical measurement was collected. This is offline
  approval-scoping evidence only; it does not approve the packet, accept a
  contact model, accept a setup target, prove strict paper-equivalent
  feasibility, calibrate contact geometry, establish hardware readiness, or
  authorize hardware work.

## V121 Read-Only Approval Packet Coverage

### Covered all finalizer-eligible steps with audited not-approved packets

- Implementation commit:
  `5cd3b3d8d4bb8672a8c74ba5832439c3faba7c7a`
- Scripts:
  - `scripts/audit_read_only_step_approval_packet_coverage.py`
- Runs:
  - `runs/read_only_step_approval_packet/20260525T100000`
  - `runs/read_only_step_approval_packet/20260525T100100`
  - `runs/read_only_step_approval_packet/20260525T100200`
  - `runs/read_only_step_approval_packet/20260525T100300`
  - `runs/read_only_step_approval_packet_audit/20260525T100001`
  - `runs/read_only_step_approval_packet_audit/20260525T100101`
  - `runs/read_only_step_approval_packet_audit/20260525T100201`
  - `runs/read_only_step_approval_packet_audit/20260525T100301`
  - `runs/read_only_step_approval_packet_coverage/20260525T100500`
- Report:
  - `reports/read_only_step_approval_packet_coverage_report.md`
- Tests:
  - `tests/test_read_only_step_approval_packet_coverage.py`
- Command:
  `python3 scripts/audit_read_only_step_approval_packet_coverage.py --run-id 20260525T100500`
- Tracked lightweight artifacts:
  each packet top-level `metrics.yaml`, `metrics.json`,
  `approval_packet.md`, `summary.md`, and `git_state.md`; each packet audit
  top-level `metrics.yaml`, `metrics.json`, `summary.md`, and `git_state.md`;
  coverage audit top-level `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`; report, tests, and updated planning/decision/manifest
  documentation.
- Result:
  The coverage audit passes with `violations = []`, finalizer step coverage
  `5 / 5`, approved packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`, heavy payloads `[]`, and
  `do_not_mark_goal_complete = true`.
- Validation:
  Focused packet tests passed with `7 passed in 1.60s`; YAML anchor check
  found no anchors in the generated metrics; raw/heavy artifact scan found no
  payloads; full tests passed with `195 passed in 9.83s`; `git diff --check`
  passed.
- Limit:
  No live or physical measurement was collected. This is offline
  approval-scoping evidence only; it does not approve any packet, accept a
  contact model, accept a setup target, prove strict paper-equivalent
  feasibility, calibrate contact geometry, establish hardware readiness, or
  authorize hardware work.

## V122 Read-Only Step Execution Preflight

### Verified the offline packet-to-finalizer command path

- Implementation commit:
  `8e3008f5c723444ce95716cd968012d6150d122e`
- Scripts:
  - `scripts/audit_read_only_step_execution_preflight.py`
- Runs:
  - `runs/read_only_step_execution_preflight/20260525T101000`
- Report:
  - `reports/read_only_step_execution_preflight_report.md`
- Tests:
  - `tests/test_read_only_step_execution_preflight.py`
- Command:
  `python3 scripts/audit_read_only_step_execution_preflight.py --run-id 20260525T101000`
- Tracked lightweight artifacts:
  preflight audit top-level `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`; report, tests, script, and updated planning/decision/
  manifest documentation.
- Result:
  The preflight audit passes with `violations = []`, finalizer step readiness
  `5 / 5`, approved packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`, `preflight_authorizes_live_access =
  false`, `preflight_authorizes_execution = false`,
  `approved_read_only_evidence_created = false`, heavy payloads `[]`, and
  `do_not_mark_goal_complete = true`.
- Validation:
  Focused coverage/preflight tests passed with `6 passed in 2.02s`; YAML
  anchor check found no anchors in the generated metrics; raw/heavy artifact
  scan found no payloads; full tests passed with `198 passed in 10.52s`;
  `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline command-path
  readiness only; it does not approve any packet, accept a contact model,
  accept a setup target, prove strict paper-equivalent feasibility, calibrate
  contact geometry, establish hardware readiness, or authorize hardware work.

## V123 Post-V122 Completion Gate

### Recorded readiness artifacts as non-evidence

- Implementation commit:
  `ae2abb566b12dbc348a0675babe8f33f08c608bc`
- Scripts:
  - `scripts/audit_post_v122_completion_gate.py`
- Runs:
  - `runs/post_v122_completion_gate/20260525T102000`
- Report:
  - `reports/post_v122_completion_gate_report.md`
- Tests:
  - `tests/test_post_v122_completion_gate.py`
- Command:
  `python3 scripts/audit_post_v122_completion_gate.py --run-id 20260525T102000`
- Tracked lightweight artifacts:
  completion gate top-level `metrics.yaml`, `metrics.json`, `summary.md`, and
  `git_state.md`; report, tests, script, and updated planning/decision/
  manifest documentation.
- Result:
  The completion gate passes as an audit while keeping the goal incomplete:
  `overall_goal_complete = false`, `completion_claim_allowed = false`,
  approved read-only evidence runs `0`, passed approved-read-only audits `0`,
  accepted orientation reviews `0`, accepted contact/setup-target reviews `0`,
  strict terminal pass count `0`, closed robustness cells `0`, no hardware
  gate report, and `readiness_artifacts_are_non_evidence = true`.
- Validation:
  Focused tests passed with `3 passed in 0.28s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `201 passed in 10.89s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline completion
  bookkeeping only; it does not approve any packet, accept a contact model,
  accept a setup target, prove strict paper-equivalent feasibility, calibrate
  contact geometry, establish hardware readiness, or authorize hardware work.

## V124 Paper-Platform Claim Boundary Regression

### Guarded split paper-platform evidence lines

- Implementation commit:
  `e7e1f89849dfd8827123bf74cc02201f7cd1332c`
- Scripts:
  - `scripts/audit_paper_platform_claim_boundary.py`
- Runs:
  - `runs/paper_platform_claim_boundary/20260525T103000`
- Report:
  - `reports/paper_platform_claim_boundary_report.md`
- Tests:
  - `tests/test_paper_platform_claim_boundary.py`
- Command:
  `python3 scripts/audit_paper_platform_claim_boundary.py --run-id 20260525T103000`
- Tracked lightweight artifacts:
  claim-boundary audit top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; report, tests, script, and updated
  planning/decision/manifest documentation.
- Result:
  The claim-boundary audit passes while preserving split paper-platform
  reporting: `formula_convergence_claim_allowed = true`,
  `tuned_figure_match_claim_allowed = true`,
  `strict_paper_equivalent_claim_allowed = false`,
  `claim_lines_collapsed = false`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `4 passed in 0.17s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `205 passed in 10.96s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline
  paper-platform bookkeeping only; it does not approve any packet, accept a
  contact model, accept a setup target, prove strict paper-equivalent
  feasibility, prove robustness, establish hardware readiness, or authorize
  hardware work.

## V125 Strict Terminal Tradeoff Boundary

### Recorded existing strict-terminal tradeoff structure

- Implementation commit:
  `a41aada3a50bd59d57652b1ec7dffe2a81d4bde7`
- Scripts:
  - `scripts/audit_strict_terminal_tradeoff_boundary.py`
- Runs:
  - `runs/strict_terminal_tradeoff_boundary/20260525T104000`
- Report:
  - `reports/strict_terminal_tradeoff_boundary_report.md`
- Tests:
  - `tests/test_strict_terminal_tradeoff_boundary.py`
- Command:
  `python3 scripts/audit_strict_terminal_tradeoff_boundary.py --run-id 20260525T104000`
- Tracked lightweight artifacts:
  tradeoff-boundary audit top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; report, tests, script, and updated
  planning/decision/manifest documentation.
- Result:
  The tradeoff-boundary audit passes while keeping strict feasibility open:
  `strict_terminal_pass_count = 0`,
  `best_combined_max_gate_ratio = 2.11994927622362`,
  `best_combined_failed_all_three_scalar_gates = true`,
  `force_xy_without_orientation_count = 1`,
  `xy_orientation_without_force_or_contact_count = 2`,
  `tradeoff_boundary_preserved = true`, `new_optimization_run = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.24s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `208 passed in 11.32s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline bookkeeping
  over existing v116 rows only; it does not run a new optimizer, approve any
  packet, accept a contact model, accept a setup target, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.

## V126 Strict Terminal Relaxation Budget

### Quantified non-accepted strict gate relaxation budgets

- Implementation commit:
  `7ba52057c82f19037916879880af322e8a7132ba`
- Scripts:
  - `scripts/audit_strict_terminal_relaxation_budget.py`
- Runs:
  - `runs/strict_terminal_relaxation_budget/20260525T105000`
- Report:
  - `reports/strict_terminal_relaxation_budget_report.md`
- Tests:
  - `tests/test_strict_terminal_relaxation_budget.py`
- Command:
  `python3 scripts/audit_strict_terminal_relaxation_budget.py --run-id 20260525T105000`
- Tracked lightweight artifacts:
  relaxation-budget audit top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; report, tests, script, and updated
  planning/decision/manifest documentation.
- Result:
  The relaxation-budget audit passes while accepting no relaxation:
  `strict_terminal_pass_count = 0`,
  `minimum_uniform_multiplier = 2.11994927622362`,
  `minimum_uniform_requires_all_three_scalar_gates = true`,
  `orientation_only_multiplier = 4.899002392744376`,
  `contactless_xy_orientation_row_count = 2`,
  `relaxation_budget_acceptance_allowed = false`,
  `new_optimization_run = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.28s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `211 passed in 11.65s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline bookkeeping
  over existing rows only; it does not run a new optimizer, approve any packet,
  accept a contact model, accept a setup target, relax a gate, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.

## V127 Read-Only Evidence Dependency Map

### Mapped unresolved readiness checks to exact read-only evidence steps

- Implementation commit:
  `9b494221728e1ff461fc5f6d6c13381a5f3c12f4`
- Scripts:
  - `scripts/audit_read_only_evidence_dependency_map.py`
- Runs:
  - `runs/read_only_evidence_dependency_map/20260525T110000`
- Report:
  - `reports/read_only_evidence_dependency_map_report.md`
- Tests:
  - `tests/test_read_only_evidence_dependency_map.py`
- Command:
  `python3 scripts/audit_read_only_evidence_dependency_map.py --run-id 20260525T110000`
- Tracked lightweight artifacts:
  dependency-map audit top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; report, tests, script, and updated
  planning/decision/manifest documentation.
- Result:
  The dependency-map audit passes while creating no evidence:
  `dependency_map_complete = true`, mapped readiness/finalizer counts `5 / 5`,
  packet-covered steps `5 / 5`, preflight-ready steps `5 / 5`, approved
  packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`,
  `approved_read_only_evidence_created = false`,
  `explicit_user_approval_required = true`, `completion_claim_allowed = false`,
  and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.21s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `214 passed in 11.67s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline dependency
  bookkeeping only; it does not approve any packet, authorize live access,
  authorize execution, create approved calibration evidence, accept a contact
  model, accept a setup target, relax a gate, prove strict paper-equivalent
  feasibility, prove robustness, establish hardware readiness, or authorize
  hardware work.

## V128 Read-Only Next-Step Selection

### Selected the first exact read-only approval candidate without authorization

- Implementation commit:
  `51793eae7f878f9e6bb721216e2c1820ea178375`
- Scripts:
  - `scripts/audit_read_only_next_step_selection.py`
- Runs:
  - `runs/read_only_next_step_selection/20260525T111000`
- Report:
  - `reports/read_only_next_step_selection_report.md`
- Tests:
  - `tests/test_read_only_next_step_selection.py`
- Command:
  `python3 scripts/audit_read_only_next_step_selection.py --run-id 20260525T111000`
- Tracked lightweight artifacts:
  next-step selection audit top-level `metrics.yaml`, `metrics.json`,
  `summary.md`, and `git_state.md`; report, tests, script, and updated
  planning/decision/manifest documentation.
- Result:
  The selector audit passes while authorizing nothing:
  `selection_plan_complete = true`, candidate steps `5`,
  `first_candidate_step_id = phase1_mounted_stack_tcp_contact_measurement`,
  `first_candidate_worksheet = tcp_contact_measurements.csv`, exact step ID
  required true, approved packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`,
  `approved_read_only_evidence_created = false`,
  `selection_authorizes_execution = false`, `completion_claim_allowed = false`,
  and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.13s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `217 passed in 11.80s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline selection
  bookkeeping only; it does not approve any packet, authorize live access,
  authorize execution, create approved calibration evidence, accept a contact
  model, accept a setup target, relax a gate, prove strict paper-equivalent
  feasibility, prove robustness, establish hardware readiness, or authorize
  hardware work.

## V129 Read-Only Phase1 Approval Request Freeze

### Frozen the selected phase1 packet request without approval

- Implementation commit:
  `4bf07b2373af781eb35b20d13862afd9c5330907`
- Scripts:
  - `scripts/audit_read_only_phase1_approval_request_freeze.py`
- Runs:
  - `runs/read_only_phase1_approval_request_freeze/20260525T112000`
- Report:
  - `reports/read_only_phase1_approval_request_freeze_report.md`
- Tests:
  - `tests/test_read_only_phase1_approval_request_freeze.py`
- Command:
  `python3 scripts/audit_read_only_phase1_approval_request_freeze.py --run-id 20260525T112000`
- Tracked lightweight artifacts:
  phase1 approval-request freeze audit top-level `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; report, tests, script, and
  updated planning/decision/manifest documentation.
- Result:
  The freeze audit passes while authorizing nothing:
  `approval_request_freeze_complete = true`,
  `frozen_step_id = phase1_mounted_stack_tcp_contact_measurement`,
  `frozen_worksheet = tcp_contact_measurements.csv`,
  `packet_markdown_sha256 =
  91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d`,
  packet status `approval_packet_created_not_approved`, packet approval status
  `not_approved`, `freeze_authorizes_execution = false`,
  `approved_read_only_evidence_created = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 0.11s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `220 passed in 11.97s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline
  approval-request bookkeeping only; it does not approve any packet, authorize
  live access, authorize execution, create approved calibration evidence,
  accept a contact model, accept a setup target, relax a gate, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.

## V130 Read-Only Phase1 Preapproval Finalizer Guard

### Audited negative finalizer paths for the frozen phase1 request

- Scripts:
  - `scripts/audit_read_only_phase1_preapproval_finalizer_guard.py`
- Runs:
  - `runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000`
- Report:
  - `reports/read_only_phase1_preapproval_finalizer_guard_report.md`
- Tests:
  - `tests/test_read_only_phase1_preapproval_finalizer_guard.py`
- Command:
  `python3 scripts/audit_read_only_phase1_preapproval_finalizer_guard.py --run-id 20260525T113000`
- Tracked lightweight artifacts:
  phase1 preapproval finalizer guard top-level `metrics.yaml`,
  `metrics.json`, `summary.md`, and `git_state.md`; report, tests, script, and
  updated planning/decision/manifest documentation.
- Result:
  The guard audit passes while authorizing nothing: case count `5`, rejected
  cases `5`, scaffold-preserved cases `5`,
  `approved_read_only_evidence_created_count = 0`,
  `successful_finalization_count = 0`,
  `repository_evidence_run_created = false`, `temp_only_dry_run = true`,
  `guard_authorizes_execution = false`, `completion_claim_allowed = false`,
  and `do_not_mark_goal_complete = true`.
- Validation:
  Focused tests passed with `3 passed in 3.21s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `223 passed in 15.10s`; `git diff --check` passed.
- Limit:
  No live or physical measurement was collected. This is offline preapproval
  guard bookkeeping only; it does not approve any packet, authorize live
  access, authorize execution, create approved calibration evidence, accept a
  contact model, accept a setup target, relax a gate, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.

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
