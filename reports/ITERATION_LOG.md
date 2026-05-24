# Iteration Log

## 2026-05-24 v0 Repository Migration

- Branch: `exp/tase-ur10e-v0-paper-audit`
- Remote: `https://github.com/Mingdao007/reproduce-tase.git`
- Baseline remote state: empty repository, no branches.
- Legacy source:
  `/home/andy/ur10e_ros2_ws/experiments/20260523_tase_finite_time_ur10e_mujoco_reproduction/`
- Commands run:
  - `git clone https://github.com/Mingdao007/reproduce-tase.git /home/andy/reproduce-tase`
  - `git switch -c exp/tase-ur10e-v0-paper-audit`
  - copied configs, scripts, source, assets, docs, reports, and lightweight run
    metadata from the legacy source.
- Artifacts created:
  - repo README
  - mandatory plans
  - decision record
  - repo migration audit
  - math transfer note
  - run artifact manifest
- Result:
  v0 migration in progress. No real robot motion, writes, zeroing, URCap
  changes, TCP writes, or payload writes were performed.
- Next step:
  Run smoke checks from this repo, commit, and push the v0 branch.

## 2026-05-24 v0 Smoke Verification From New Repo

- Branch: `exp/tase-ur10e-v0-paper-audit`
- Commit SHA: none yet; repository had no initial commit at run time.
- Dirty-tree status: all migrated files were untracked at run time.
- Commands run:
  - `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
  - `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
- Run outputs:
  - `runs/fig5_r_sweep/20260524T011145`
  - `runs/ur10e_smoke/20260524T011145`
- Result:
  - Fig.5 scalar sweep completed. It still warned that `q0`,
    `trajectory`, `orientation_signal_raw`, `desired_normal_force_N`, and
    `r_sweep` are `pending_pdf_verify`.
  - UR10e MuJoCo smoke completed using approximate uncalibrated MJCF and the
    unverified 85 mm TCP guess.
- Next step:
  Commit and push the v0 migration branch, then start PDF truth extraction.

## 2026-05-24 Initial PDF Truth Extraction

- Branch: `exp/tase-ur10e-v0-paper-audit`
- Starting commit: `fe8681582e5e28243c62042f41d91c9c16f107b6`
- Commands run:
  - `pdftotext "<paper-pdf>" /tmp/tase_paper.txt`
  - `pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt`
  - `rg -n "Abstract|Index Terms|FINITE|finite-time|force.*motion|MIAE|77\\.26|Experiment|Fig\\. 5|Fig\\. 6|Table|Franka|Panda|UR|r =|0\\.2|0\\.4|0\\.6|0\\.8|1\\.0|cycloid|cardioid|impedance|neural" /tmp/tase_paper.txt`
- Artifacts updated:
  - `configs/paper_truth.yaml`
  - `reports/paper_truth_extraction.md`
  - `reports/DECISION_RECORD.md`
- Result:
  Section V q0, trajectory, force target, joint limits, velocity limits, and
  Fig.5 convergence times are now PDF-grounded. Section VI E1-E4 trajectory
  formulas, contact times, and comparison MIAE values are also recorded.
- Remaining gap:
  Orientation signal dimension, `z0`, and impedance/gain parameters still need
  extraction or interpretation.
- Verification:
  `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml`
  completed after the config update and produced
  `runs/fig5_r_sweep/20260524T011603`.

## 2026-05-24 v1 Math Contract Tests

- Branch: `exp/tase-ur10e-v1-math-contracts`
- Starting commit: `3ca7fe22ca70dab22368523cf5066b2dd30f9e84`
- Files added:
  - `src/tase_repro/kinematics.py`
  - `src/tase_repro/contact.py`
  - `src/tase_repro/constraints.py`
  - `tests/test_finite_time.py`
  - `tests/test_kinematics.py`
  - `tests/test_contact.py`
  - `tests/test_constraints.py`
  - `scripts/run_tests.sh`
- Commands run:
  - `python3 -m pytest -q`
  - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q`
- Result:
  Direct pytest failed during external plugin loading because user-site `anyio`
  expected `_pytest.scope`. With plugin autoload disabled, all math-contract
  tests passed: `11 passed in 0.17s`.
- Additional verification:
  - `scripts/run_tests.sh` passed: `11 passed in 0.13s`.
  - `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml --smoke`
    produced `runs/fig5_r_sweep/20260524T012004`.
  - `python3 scripts/run_ur10e_mujoco_adaptation.py --config configs/mujoco_ur10e.yaml --smoke`
    produced `runs/ur10e_smoke/20260524T012004`.
- Next step:
  Commit and push the v1 math-contract branch, then use these contracts to
  implement the first simulation-only controller path.

## 2026-05-24 v2 Controller Smoke

- Branch: `exp/tase-ur10e-v2-controller-smoke`
- Starting commit: `17093c62c255b27e981b7244477e8c0d7057031e`
- Files added:
  - `src/tase_repro/controller.py`
  - `scripts/run_controller_smoke.py`
  - `tests/test_controller.py`
- Commands run:
  - `scripts/run_tests.sh`
  - `python3 scripts/run_controller_smoke.py --config configs/mujoco_ur10e.yaml --duration-s 1.0`
- Result:
  Tests passed: `13 passed in 0.14s`. Controller smoke produced
  `runs/controller_smoke/20260524T012218` with solver success fraction `1.0`,
  `max_qdot_violation_rad_s = 0.0`, and
  `max_joint_limit_violation_rad = 0.0`.
- Limit:
  This is simulation-only velocity-level tracking. It is not contact control,
  force control, or hardware-ready.
- Next step:
  Add a static contact-force ladder simulation that logs contact sign,
  force target, solver status, and failure conditions before any real robot
  motion is considered.

## 2026-05-24 v3 Contact Force Ladder

- Branch: `exp/tase-ur10e-v3-contact-force-ladder`
- Starting commit: `ab94671f472a6043955dfdea5d605edc55c6dc33`
- Files added:
  - `src/tase_repro/contact_ladder.py`
  - `scripts/run_contact_force_ladder.py`
  - `tests/test_contact_ladder.py`
  - `reports/contact_force_ladder_report.md`
- Commands run:
  - exploratory contact scan over `base_link` z offsets
  - `scripts/run_tests.sh`
  - `python3 scripts/run_contact_force_ladder.py --config configs/mujoco_ur10e.yaml --steps 500 --tail-steps 100 --tolerance-N 0.01`
- Result:
  Tests passed: `15 passed in 0.15s`. Contact ladder run
  `runs/contact_force_ladder/20260524T012524` matched targets
  `[0.5, 1.0, 2.0, 5.0] N` with maximum absolute error
  `0.0088706346160502 N`.
- Limit:
  This is static contact-model calibration via base z offsets, not closed-loop
  force control, not a robot command, and not hardware-ready.
- Next step:
  Implement a stationary contact feedback controller simulation that regulates
  normal force using the bounded velocity solve and logs force error, solver
  status, active bounds, and stop conditions.

## 2026-05-24 v4 Stationary Force Feedback

- Branch: `exp/tase-ur10e-v4-stationary-force-feedback`
- Starting commit: `082ab4e063b57bdd1cc23a4f436967a63d8497a0`
- Files added:
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_stationary_force_feedback.py`
  - `tests/test_force_feedback.py`
  - `reports/stationary_force_feedback_report.md`
- Commands run:
  - exploratory bent-posture force-feedback scans
  - `scripts/run_tests.sh`
  - `python3 scripts/run_stationary_force_feedback.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5`
- Result:
  Tests passed: `16 passed in 0.20s`. Stationary force feedback run
  `runs/stationary_force_feedback/20260524T013040` regulated from
  `5.886648180968636 N` to `5.000002800044511 N`, with solver success
  fraction `1.0` and no qdot or joint-limit violation.
- Limit:
  This is kinematic, simulation-only stationary normal-force feedback. It is
  not tangential trajectory tracking, not orientation compliance, not torque
  dynamics, and not hardware-ready.
- Next step:
  Add low-speed tangential motion while holding normal force in simulation.

## 2026-05-24 v5 Tangential Force-Motion Smoke

- Branch: `exp/tase-ur10e-v5-tangential-force-motion`
- Starting commit: `387ad1dce8b83c0ba5e897a9683e6883661aaca6`
- Files added:
  - `scripts/run_tangential_force_motion.py`
  - `tests/test_force_motion.py`
  - `reports/tangential_force_motion_report.md`
- Files updated:
  - `src/tase_repro/force_feedback.py`
- Commands run:
  - `scripts/run_tests.sh`
  - `python3 scripts/run_tangential_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 4.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --tangential-velocity 0.0005,0.0 --tangential-kp 0.5`
- Result:
  Tests passed: `17 passed in 0.24s`. Tangential force-motion run
  `runs/tangential_force_motion/20260524T013342` moved x by
  `0.0019989989469737 m` while holding 5 N with tail mean absolute force
  error `1.775978411200585e-05 N`, solver success fraction `1.0`, contact
  present fraction `1.0`, and no qdot or joint-limit violation.
- Limit:
  This is simulation-only velocity-level force-motion. It lacks orientation
  compliance, torque dynamics, calibrated TCP, and hardware force source
  validation.
- Next step:
  Run the first low-speed paper-trajectory-shaped contact path in simulation
  with the same metrics.

## 2026-05-24 v6 Paper Trajectory Force-Motion Smoke

- Branch: `exp/tase-ur10e-v6-paper-trajectory-force-motion`
- Starting commit: `e47c2fe6d3ec1b17904623dcab1d787441d0183b`
- Files added:
  - `src/tase_repro/trajectories.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `tests/test_trajectories.py`
  - `reports/paper_trajectory_force_motion_report.md`
- Files updated:
  - `src/tase_repro/force_feedback.py`
  - `tests/test_force_motion.py`
- Commands run:
  - `scripts/run_tests.sh`
  - `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --duration-s 8.0 --target-force-N 5.0 --force-gain 5e-5 --r 0.5 --base-z-offset-m=-4e-5 --trajectory e1-cycloid --amplitude-m 0.015 --omega-rad-s 0.1 --paper-time-scale 1.0 --planar-kp 0.5`
- Result:
  Tests passed: `20 passed in 0.28s`. Paper E1 cycloid force-motion run
  `runs/paper_trajectory_force_motion/20260524T013829` tracked final
  tangential displacement `[0.0012394851720925958, 0.004549066283786667] m`
  against desired `[0.0012387489718280922, 0.00454724750054618] m`, with tail
  mean absolute force error `0.00898488092600231 N`, solver success fraction
  `1.0`, contact present fraction `1.0`, and no qdot or joint-limit
  violation.
- Limit:
  This is the paper E1 planar shape only. It still lacks orientation
  compliance, torque dynamics, calibrated TCP, and hardware force source
  validation.
- Next step:
  Add the remaining paper trajectory shapes as simulation-only force-motion
  smokes and compare force/position metrics across the matrix.

## 2026-05-24 v7 Paper Trajectory Matrix

- Branch: `exp/tase-ur10e-v7-paper-trajectory-matrix`
- Starting commit: `e89f3561d576c420374aebdb8f7fe85839b49674`
- Files updated:
  - `src/tase_repro/trajectories.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `tests/test_trajectories.py`
- Files added:
  - `reports/paper_trajectory_matrix_report.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Full-speed E1-E4 matrix:
    `runs/paper_trajectory_matrix/20260524T014139`
  - Full-speed E1-E4 matrix with `--qdot-limit-rad-s 0.15`:
    `runs/paper_trajectory_matrix/20260524T014244`
  - Low-speed E1-E4 matrix with `--paper-time-scale 0.25`:
    `runs/paper_trajectory_matrix/20260524T014344`
- Result:
  Tests passed: `25 passed in 0.29s`. Full-speed E2/E3 lost contact even when
  the qdot cap was raised to `0.15 rad/s`; stronger force-gain probes saturated
  near the qdot cap and did not recover contact. The low-speed matrix kept all
  E1-E4 trajectories in contact with solver success fraction `1.0`, contact
  present fraction `1.0`, and no qdot or joint-limit violation.
- Limit:
  The accepted matrix uses `paper_time_scale = 0.25`; it is a low-speed
  trajectory-shape smoke, not a full-speed Section VI reproduction.
- Next step:
  Investigate full-speed E2/E3 contact loss with a prioritized or weighted
  normal-force task before claiming full paper-trajectory reproduction.

## 2026-05-24 v8 Weighted Normal Force-Motion Probe

- Branch: `exp/tase-ur10e-v8-normal-weighted-force-motion`
- Starting commit: `1c1329ca32078f7822d426db6962521bcc714c88`
- Files updated:
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
- Files added:
  - `reports/weighted_normal_force_motion_report.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Weighted full-speed probes under
    `runs/weighted_normal_force_motion/20260524T014811`
- Result:
  Tests passed: `27 passed in 0.32s`. Axis weighting confirmed the v7 failure
  mode: equal-weight full-speed E2/E3 lose contact because planar tracking
  dominates the coupled velocity solve. A full-speed weighted matrix with
  `axis_weights = [1, 1, 100]`, `force_gain = 5e-4`, and
  `--qdot-limit-rad-s 0.15` recovered contact and force regulation for E1-E4,
  but E2/E3 had max planar errors `0.02114519099848796 m` and
  `0.016169767707432416 m` respectively, with qdot saturation.
- Limit:
  This is diagnostic controller tuning, not an acceptable full-speed paper
  reproduction.
- Next step:
  Implement a two-stage or prioritized velocity solve that reports normal-force
  task residual and planar tracking slack separately.

## 2026-05-24 v9 Normal Guard Force-Motion Probe

- Branch: `exp/tase-ur10e-v9-normal-guard-force-motion`
- Starting commit: `3eac57b6ee49e55908641b62fc427575f27f39a7`
- Files updated:
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `tests/test_force_motion.py`
- Files added:
  - `reports/normal_guard_force_motion_report.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Guarded full-speed probes under
    `runs/normal_guard_force_motion/20260524T015341`
- Result:
  Tests passed: `28 passed in 0.32s`. The equal-axis guard reduced planar
  commands but did not preserve force on E2/E3. With `normal_axis_weight = 50`,
  contact stayed present for E1-E4, but E2/E3 still had max planar errors
  `0.020166709027307318 m` and `0.015963081975681002 m`, with force errors
  `0.5085483615637729 N` and `0.14769228903285758 N`.
- Limit:
  The scalar guard is diagnostic and does not solve full-speed E2/E3.
- Next step:
  Implement a slack-aware velocity solve with separate normal and planar
  residual metrics.

## 2026-05-24 v10 Residual Metrics

- Branch: `exp/tase-ur10e-v10-residual-metrics`
- Starting commit: `a471f34316296102a5910706d1a9507759946d4b`
- Files updated:
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_tangential_force_motion.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
- Files added:
  - `reports/residual_metrics_force_motion_report.md`
- Commands run:
  - `scripts/run_tests.sh`
  - E2/E3 residual comparison under
    `runs/residual_metrics_force_motion/20260524T015831`
- Result:
  Tests passed: `28 passed in 0.33s`. Equal-axis E2/E3 cases showed small
  planar velocity residuals but large normal residuals and contact loss.
  High-normal-weight E2/E3 cases recovered normal residual and contact but
  produced large planar residuals and centimeter-scale path error.
- Limit:
  Residual instrumentation confirms the tradeoff but does not solve it.
- Next step:
  Implement a bounded solver with explicit normal and planar slack variables
  or task hierarchy.

## 2026-05-24 v11 Slack-Aware Velocity Solve

- Branch: `exp/tase-ur10e-v11-slack-aware-solve`
- Starting commit: `de6296836f05bcb95bd855fc8eb9f5cab33c8730`
- Files updated:
  - `src/tase_repro/constraints.py`
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_tangential_force_motion.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
- Files added:
  - `reports/slack_aware_force_motion_report.md`
- Commands run:
  - `scripts/run_tests.sh`
  - E2/E3 slack-aware probes under
    `runs/slack_aware_force_motion/20260524T020245`
- Result:
  Tests passed: `29 passed in 0.34s`. The slack-aware solver exposed the
  tradeoff directly: low normal slack penalty preserves more planar tracking
  but loses force; high normal slack penalty recovers force/contact but creates
  large planar slack and centimeter-scale path error.
- Limit:
  This is explicit diagnostic slack accounting, not full-speed E2/E3
  reproduction.
- Next step:
  Define pass/fail thresholds for slack, force, contact, and qdot saturation;
  then test feasibility changes such as slower time scaling or different
  initial posture before adding orientation compliance.

## 2026-05-24 v12 Timing Feasibility Gates

- Branch: `exp/tase-ur10e-v12-feasibility-gates`
- Starting commit: `2cd3b4179a3ca6548aa8d4398a7d030a9d388394`
- Files added:
  - `src/tase_repro/feasibility.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `tests/test_feasibility.py`
  - `reports/timing_feasibility_gates_report.md`
- Files updated:
  - `src/tase_repro/force_feedback.py`
- Commands run:
  - `scripts/run_tests.sh`
  - E2/E3 timing feasibility sweep under
    `runs/timing_feasibility_sweep/20260524T021322`
- Result:
  Tests passed: `32 passed in 0.36s`. Full-speed E2/E3 remain rejected by
  position, planar slack, and sustained qdot saturation gates. `paper_time_scale
  = 0.25` passes force, contact, path, and slack gates but still has sustained
  qdot saturation. The fastest tested passing scale for both E2 and E3 is
  `0.2`.
- Limit:
  The `0.2` result is a slowed simulation-only feasibility point, not
  full-speed paper reproduction and not hardware validation.
- Next step:
  Use `paper_time_scale = 0.2` as the controlled baseline for posture or
  approach-phase experiments that try to move the fastest passing scale closer
  to `1.0`.

## 2026-05-24 v13 Posture Feasibility Sweep

- Branch: `exp/tase-ur10e-v13-posture-feasibility`
- Starting commit: `e4131857157e48aa1e16f2f77746eca62ced6971`
- Files added:
  - `scripts/run_posture_feasibility_sweep.py`
  - `reports/posture_feasibility_sweep_report.md`
- Files updated:
  - `src/tase_repro/contact_ladder.py`
  - `tests/test_contact_ladder.py`
- Commands run:
  - `scripts/run_tests.sh`
  - E2/E3 posture feasibility sweep under
    `runs/posture_feasibility_sweep/20260524T022145`
- Result:
  Tests passed: `33 passed in 0.38s`. The posture sweep reused the v12 gates
  with per-posture static 5 N contact calibration. The calibrated near-straight
  baseline did not pass the tested timing matrix. Small bends improved the
  fastest passing E2/E3 scale: `bend_0p03` passed at `0.25`, `bend_0p05` at
  `0.5`, `bend_0p075` at `0.75`, and `bend_0p10` at full paper time scale
  `1.0`.
- Limit:
  The postures are simulation initial conditions, not real robot commands.
  Contact is still approximate MuJoCo base z offset calibration. Orientation
  compliance and hardware validation remain open.
- Next step:
  Use `bend_0p10` as the full-speed simulation baseline before adding
  orientation compliance or planned approach-phase logic.

## 2026-05-24 v14 Full-Speed Posture Matrix

- Branch: `exp/tase-ur10e-v14-fullspeed-posture-matrix`
- Starting commit: `549334a9b27403f8c6e9915416d9c7f6420e0e9c`
- Files added:
  - `reports/fullspeed_posture_matrix_report.md`
- Files updated:
  - `scripts/run_timing_feasibility_sweep.py`
  - `reports/DECISION_RECORD.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Full-speed E1-E4 posture matrix under
    `runs/fullspeed_posture_matrix/20260524T022724`
- Result:
  Tests passed: `33 passed in 0.37s`. With the calibrated `bend_0p10`
  MuJoCo posture, E1, E2, E3, and E4 all pass the v12 feasibility gates at
  `paper_time_scale = 1.0`. Tail mean absolute force errors are below
  `0.001 N`, contact fraction is `1.0`, qdot saturation fraction is `0.0`,
  and tail qdot utilization stays below `0.28` for all four cases.
- Limit:
  This is still a simulation-only posture baseline. `bend_0p10` is not a real
  robot motion command, contact is a static MuJoCo base-offset calibration,
  and orientation compliance remains absent.
- Next step:
  Add orientation compliance or a planned approach phase around the full-speed
  `bend_0p10` baseline before considering any read-only hardware planning
  checklist.

## 2026-05-24 v15 Orientation-Hold Force-Motion

- Branch: `exp/tase-ur10e-v15-orientation-hold`
- Starting commit: `b4a5f09c5c93435ebd5a3e32efce970b4a1a7564`
- Files added:
  - `reports/orientation_hold_force_motion_report.md`
- Files updated:
  - `src/tase_repro/kinematics.py`
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `tests/test_kinematics.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
  - `reports/math_derivation_ur10e_transfer.md`
  - `reports/DECISION_RECORD.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Orientation-hold E1-E4 matrix runs under
    `runs/orientation_hold_matrix/20260524T030000`,
    `runs/orientation_hold_matrix/20260524T023404`, and
    `runs/orientation_hold_matrix/20260524T023429`
- Result:
  Tests passed: `36 passed in 0.42s` before the matrix runs. The controller
  now supports optional angular velocity rows with explicit angular residual
  and slack metrics. At angular slack weight `0.1`, all E1-E4 cases fail the
  existing force-motion gates due planar error/slack. At `0.001`, E1/E3/E4
  pass and E2 fails only the sustained tail qdot utilization gate. At
  `0.0001`, all E1-E4 cases pass the v12 force-motion gates, but orientation
  error reaches `0.08108796381776726 rad` and angular slack reaches
  `0.08895566203803207 rad/s`.
- Limit:
  This is an initial-orientation hold task, not the paper's full orientation
  compliance law. Orientation error is reported but not yet a hard acceptance
  gate.
- Next step:
  Define an orientation-specific gate and test whether posture, timing, or
  task-priority changes can reduce orientation error while preserving the
  full-speed force-motion gates.

## 2026-05-24 v16 Orientation Feasibility Gates

- Branch: `exp/tase-ur10e-v16-orientation-gates`
- Starting commit: `130081a6a406e498927e588b35e19ba64a9f8710`
- Files added:
  - `reports/orientation_gate_timing_report.md`
- Files updated:
  - `src/tase_repro/feasibility.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `tests/test_feasibility.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Orientation-gated timing sweeps under
    `runs/orientation_gate_timing_sweep/20260524T023847`,
    `runs/orientation_gate_timing_sweep/20260524T023938_e2e3_slow`,
    `runs/orientation_gate_timing_sweep/20260524T024000_e3_slowest`, and
    `runs/orientation_gate_timing_sweep/20260524T024026_common_0p075`
- Result:
  Tests passed: `38 passed in 0.42s` before the sweeps. Optional orientation
  gates were added to the feasibility evaluator. With provisional gates
  `max_orientation_error_rad <= 0.03` and
  `max_angular_velocity_slack_rad_s <= 0.03`, the fastest tested passing
  scales are E1 `0.5`, E2 `0.1`, E3 `0.075`, and E4 `0.5`. A common
  E1-E4 matrix passes all combined gates at `paper_time_scale = 0.075`.
- Limit:
  The orientation gate is provisional and the common passing matrix is slowed.
  Full-speed orientation-gated reproduction remains open.
- Next step:
  Try a true task-priority solve, posture search, or paper-specific
  orientation signal if full-speed orientation feasibility is required.

## 2026-05-24 v17 Orientation-Gated Posture Sweep

- Branch: `exp/tase-ur10e-v17-orientation-posture-sweep`
- Starting commit: `c85ca7fd8dd3bb219dfe41b8ebbefefc6d64937c`
- Files added:
  - `reports/orientation_posture_sweep_report.md`
  - `tests/test_posture_feasibility_sweep.py`
  - `runs/orientation_posture_sweep/20260524T024358/ABORTED.md`
- Files updated:
  - `scripts/run_posture_feasibility_sweep.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - Focused full-speed E2/E3 orientation-gated posture sweep under
    `runs/orientation_posture_sweep/20260524T041329_calibration_safe`
  - Focused angular-priority brackets under
    `runs/orientation_posture_sweep/20260524T041329_weight_0p03`,
    `runs/orientation_posture_sweep/20260524T041329_weight_0p01`, and
    `runs/orientation_posture_sweep/20260524T041329_weight_0p003`
- Result:
  The sweep driver now records calibration failures instead of aborting.
  `bend_0p10` and `bend_0p125` calibrate to the `5 N` initial-contact target,
  while `bend_0p15` and `bend_0p20` do not calibrate inside the default
  bracket. At angular slack weight `0.1`, E2/E3 satisfy orientation gates but
  fail planar position/slack gates at full speed. Lower angular slack weights
  restore planar tracking only by failing the orientation gates. No tested
  full-speed E2/E3 posture/weight pair passes the combined gate set.
- Limit:
  This is simulation-only posture and angular-priority evidence. The
  calibration is a MuJoCo base-offset setup, not a hardware approach motion.
- Next step:
  Keep the v16 common `paper_time_scale = 0.075` matrix as the current
  orientation-gated fallback. Pursue a true task-priority/null-space-aware
  solve or a paper-specific orientation signal before more ad hoc posture
  searching.

## 2026-05-24 v18 Linear-Primary Orientation

- Branch: `exp/tase-ur10e-v18-nullspace-orientation`
- Starting commit: `3ab4c4ef8b832230682d89668cc3621e6c493ea4`
- Files added:
  - `reports/nullspace_orientation_report.md`
- Files updated:
  - `src/tase_repro/constraints.py`
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `scripts/run_posture_feasibility_sweep.py`
  - `tests/test_constraints.py`
  - `tests/test_controller.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - E2/E3 linear-primary orientation timing sweep under
    `runs/nullspace_orientation_timing_sweep/20260524T042206`
  - E1-E4 common `0.075` confirmation under
    `runs/nullspace_orientation_timing_sweep/20260524T042206_common_0p075`
- Result:
  Tests passed: `41 passed in 0.45s`. The new two-stage solve preserves the
  primary TCP linear velocity and uses the remaining feasible velocity space
  for orientation hold. It removes the v17 planar-slack failure mode but does
  not recover full-speed E2/E3: both trajectories pass the combined gates only
  at `paper_time_scale = 0.075`, with higher scales rejected by qdot
  saturation and/or orientation gates. The E1-E4 common `0.075` matrix passes.
- Limit:
  The secondary solve is still velocity-level simulation logic, not torque
  hierarchy or hardware validation. Orientation hold is still the initial TCP
  orientation, not a PDF-verified paper orientation signal.
- Next step:
  Keep the linear-primary controller as the cleaner `0.075` fallback. Further
  full-speed work should focus on paper-specific orientation extraction,
  planned timing/orientation scheduling, or an explicit qdot-budget decision.

## 2026-05-24 v19 Paper Orientation Truth

- Branch: `exp/tase-ur10e-v19-paper-orientation-truth`
- Starting commit: `e589ce9af07b3a3b903692409432b5efda5c85f8`
- Files updated:
  - `configs/paper_truth.yaml`
  - `plans/PAPER_TRUTH_EXTRACTION.md`
  - `reports/paper_truth_extraction.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
- Commands run:
  - `pdfinfo "<paper-pdf>"`
  - `pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt`
  - `wc -l /tmp/tase_paper_layout.txt`
  - `nl -ba /tmp/tase_paper_layout.txt | sed -n '140,260p'`
  - `nl -ba /tmp/tase_paper_layout.txt | sed -n '260,390p'`
  - `nl -ba /tmp/tase_paper_layout.txt | sed -n '380,510p'`
  - `nl -ba /tmp/tase_paper_layout.txt | sed -n '500,680p'`
  - `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml --smoke --output-dir /tmp/tase_v19_fig5_smoke`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Tests passed: `41 passed in 0.45s`. `git diff --check` passed. The Fig.5
  smoke completed and emitted only the expected warning for the two retained
  Section V pending fields: `orientation_signal_dimension_resolution` and
  `z0_source`.
- Paper-truth update:
  `reports/paper_truth_extraction.md` now records the force-normal orientation
  law, quaternion outer loop, impedance and velocity-level force-motion law,
  dynamic-programming/RNN formulation, Section V simulation values, Section VI
  gains, force-filter statement, orientation-delay statement, E1-E4 experiment
  matrix, and comparison metrics. `configs/paper_truth.yaml` removes the
  resolved Section VI `pending_pdf_verify` entries.
- Limit:
  The paper's Section III/Section V orientation signal mismatch remains open.
  Current UR10e orientation results remain adapted orientation-hold baselines,
  not paper-faithful orientation compliance.
- Next step:
  Resolve the Section V 2D/3D orientation-signal ambiguity or document an
  explicit adapted UR10e orientation schedule before making further
  full-speed orientation-gated claims.

## 2026-05-24 v20 Orientation Signal Audit

- Branch: `exp/tase-ur10e-v20-orientation-signal-audit`
- Starting commit: `6ef9a6cfa5bf626adba0d8bceaacc029b5904318`
- Files added:
  - `reports/orientation_signal_ambiguity_audit.md`
- Files updated:
  - `configs/paper_truth.yaml`
  - `plans/PAPER_TRUTH_EXTRACTION.md`
  - `reports/paper_truth_extraction.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
- Commands run:
  - `pdftotext -layout "<paper-pdf>" /tmp/tase_paper_layout.txt`
  - `pdftotext -raw "<paper-pdf>" /tmp/tase_paper_raw.txt`
  - `pdftotext -fixed 3 "<paper-pdf>" /tmp/tase_paper_fixed3.txt`
  - `pdftohtml -xml -f 3 -l 4 -stdout "<paper-pdf>" > /tmp/tase_paper_p3_4.xml`
  - `pdftohtml -xml -f 5 -l 8 -stdout "<paper-pdf>" > /tmp/tase_paper_p5_8.xml`
  - `pdftotext -bbox-layout -f 3 -l 5 "<paper-pdf>" /tmp/tase_paper_p3_5_bbox.html`
  - `rg -n "u =|cos\\(0\\.1t|sin\\(0\\.1t|Rd =|sin\\(u\\)|F/kFk" /tmp/tase_paper_*.txt /tmp/tase_paper_*.xml /tmp/tase_paper_*.html`
  - `python3 - <<'PY' ... yaml.safe_load(...) ...`
  - `python3 scripts/run_fig5_r_sweep.py --config configs/paper_truth.yaml --smoke --output-dir /tmp/tase_v20_fig5_smoke`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Tests passed: `41 passed in 0.46s`. `git diff --check` passed. The Fig.5
  smoke completed with only the expected `z0_source` pending warning.
- Paper-truth update:
  Multiple extraction modes confirmed that Section V contains only
  `u = [cos(0.1t), sin(0.1t)]`, while Section III defines `u` as a 3D
  normalized force vector and Eq. (9) uses all three components. The repo now
  treats `orientation_signal_dimension_resolution` as a verified paper
  ambiguity instead of a pending PDF-verification item.
- Limit:
  This does not implement the paper orientation law. It only prevents a hidden
  third-component inference from being mislabeled as paper truth.
- Next step:
  Implement paper-orientation work from the Section III 3D force-normal
  contract, or explicitly label any Section V 2D schedule as an adapted
  assumption. The only remaining Section V paper-truth extraction field is
  `z0_source`.

## 2026-05-24 v21 Force-Normal Orientation Mode

- Branch: `exp/tase-ur10e-v21-force-normal-orientation`
- Starting commit: `e1063f53aebb4e7904d1f0c4cc19725dc3bb0224`
- Files added:
  - `src/tase_repro/orientation.py`
  - `tests/test_orientation.py`
  - `reports/force_normal_orientation_report.md`
  - `runs/force_normal_orientation_smoke/20260524T045559`
- Files updated:
  - `src/tase_repro/contact_ladder.py`
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `scripts/run_posture_feasibility_sweep.py`
  - `tests/test_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile scripts/run_paper_trajectory_force_motion.py src/tase_repro/orientation.py src/tase_repro/contact_ladder.py src/tase_repro/force_feedback.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e.yaml --output-dir runs/force_normal_orientation_smoke/20260524T045559 --duration-s 1.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0009710693359375 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 5.0 --angular-axis-weight 1.0 --angular-slack-weight 1.0`
- Result:
  Tests passed: `46 passed in 0.49s`. The force-normal smoke passed with
  solver success fraction `1.0`, contact present fraction `1.0`, tail mean
  absolute force error `0.0002761445994167211 N`, max orientation error
  `1.589167539872212e-06 rad`, max angular slack
  `1.1092273136082997e-05 rad/s`, qdot saturation fraction `0.0`, and no
  joint or velocity limit violation.
- Limit:
  The current MuJoCo surface is a flat plane with normal `+z`, so this verifies
  wiring and metrics rather than curved-surface orientation adaptation. The
  yaw convention around the force normal is a documented UR10e adaptation.
- Next step:
  Add or configure a tilted/curved MuJoCo contact surface so the force-normal
  orientation target is nontrivial, then rerun orientation-gated smoke before
  revisiting full-speed E2/E3 claims.

## 2026-05-24 v22 Tilted Force-Normal Orientation

- Branch: `exp/tase-ur10e-v22-tilted-force-normal`
- Starting commit: `8745c0d284058a2c42185d17d25276c449d405c9`
- Files added:
  - `assets/mjcf/ur10e_tilted_plane_10deg.xml`
  - `configs/mujoco_ur10e_tilted_plane.yaml`
  - `reports/tilted_force_normal_orientation_report.md`
  - `runs/tilted_force_normal_orientation_smoke/20260524T050139`
  - `runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1`
- Files updated:
  - `src/tase_repro/force_feedback.py`
  - `scripts/run_paper_trajectory_force_motion.py`
  - `scripts/run_timing_feasibility_sweep.py`
  - `scripts/run_posture_feasibility_sweep.py`
  - `tests/test_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/force_feedback.py scripts/run_paper_trajectory_force_motion.py scripts/run_timing_feasibility_sweep.py scripts/run_posture_feasibility_sweep.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/tilted_force_normal_orientation_smoke/20260524T050139 --duration-s 1.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 5.0 --angular-axis-weight 1.0 --angular-slack-weight 1.0`
  - `python3 scripts/run_paper_trajectory_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/tilted_force_normal_orientation_smoke/20260524T050139_kp0p1 --duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --use-slack-solve --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0`
- Result:
  Tests passed: `49 passed in 0.54s`. `git diff --check` passed. The tilted
  plane has expected world normal `[0.1736481777, 0.0, 0.9848077530]`, and
  both tilted smokes reached solver success fraction `1.0` and contact present
  fraction `1.0`. The `kp = 5.0` run reached tail mean absolute force error
  `0.003091381344228328 N` and tail mean orientation error
  `0.07593713278249946 rad`, but saturated qdot for the whole run. The
  `kp = 0.1` comparison avoided qdot saturation and reached tail mean absolute
  force error `0.00017028171203874897 N`, but still had tail mean orientation
  error `0.14577470816672422 rad`.
- Limit:
  This is a single tilted analytic plane, not a curved unknown surface. Neither
  gain is an orientation-gated pass: one saturates qdot, the other leaves large
  orientation error.
- Next step:
  Run a small tilted-plane orientation-gain/timing sweep with the existing
  gates. If no case passes without qdot saturation, record an explicit
  orientation approach-phase or qdot-budget decision.

## 2026-05-24 v23 Tilted Gain/Timing Sweep

- Branch: `exp/tase-ur10e-v23-tilted-gain-timing`
- Starting commit: `e37a5545af1cb9d406848180a7ef5d772df7f4e8`
- Files added:
  - `reports/tilted_gain_timing_sweep_report.md`
  - `runs/tilted_orientation_gain_timing_sweep/20260524T091826`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 scripts/run_timing_feasibility_sweep.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/tilted_orientation_gain_timing_sweep/20260524T091826/kp<gain> --trajectories e1-cycloid --time-scales 0.05,0.075,0.1 --duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --omega-rad-s 0.1 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --orientation-mode force-normal --orientation-priority-mode linear-primary --orientation-kp <gain> --angular-axis-weight 1.0 --angular-slack-weight 1.0 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Tests passed: `49 passed in 0.53s`. `git diff --check` passed. The sweep
  covered 18 E1 cases: gains `0.1`, `0.25`, `0.5`, `1.0`, `2.0`, and `5.0`
  across paper time scales `0.05`, `0.075`, and `0.1`. No case passed. Low
  gains avoided qdot saturation but failed the max-orientation-error gate at
  about `0.174 rad`. Gains at or above `0.5` also failed qdot saturation and
  angular-slack gates.
- Limit:
  This isolates the tilted orientation transition on E1 only. It does not test
  curved surfaces, hardware, or full E1-E4 article reproduction.
- Next step:
  Implement a staged orientation approach/pre-alignment simulation before
  paper-trajectory tracking, or explicitly record a qdot-budget relaxation
  decision before further tilted orientation-gated claims.

## 2026-05-24 v24 Staged Orientation Approach

- Branch: `exp/tase-ur10e-v24-staged-orientation-approach`
- Starting commit: `9059345767e6f2282013a2d6bc28d530b0e99440`
- Files added:
  - `src/tase_repro/staged_force_motion.py`
  - `scripts/run_staged_orientation_force_motion.py`
  - `tests/test_staged_force_motion.py`
  - `reports/staged_orientation_approach_report.md`
  - `runs/staged_orientation_force_motion/20260524T092927`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_force_motion/20260524T092927 --approach-duration-s 4.0 --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  Tests passed: `51 passed in 1.10s`. `git diff --check` passed. The approach
  reached final orientation error `0.0020237968932491765 rad` and crossed the
  `0.03 rad` threshold at `0.912 s`. The following E1 trajectory phase passed
  all current gates with max orientation error `0.0020303573682621625 rad`,
  qdot saturation fraction `0.003`, and no failed criteria.
- Limit:
  The approach phase itself is not a full feasibility pass. It has qdot
  saturation fraction `0.961`, max planar drift `0.009738544642078033 m`, and
  max angular slack `0.06085033484246333 rad/s`.
- Next step:
  Improve the approach phase to reduce planar drift and sustained qdot
  saturation, or explicitly record a separate relaxed approach budget before
  claiming a full staged maneuver pass.

## 2026-05-24 v25 Staged Approach Bracket

- Branch: `exp/tase-ur10e-v25-approach-bracket`
- Starting commit: `0a686dcb4972b9c4292f414af41c3fbb97f544ca`
- Files added:
  - `reports/staged_approach_bracket_report.md`
  - `runs/staged_orientation_approach_bracket/20260524T093536`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_approach_bracket/20260524T093536/<case> --approach-duration-s 4.0 --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight <weight> --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode <mode> --approach-orientation-kp <gain> --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight <weight> --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The bracket covered seven Stage A cases. Approach terminal-orientation pass
  count was `5 / 7`, trajectory-after-approach pass count was `3 / 7`, and
  full staged-feasibility pass count was `0 / 7`. No approach case passed the
  ordinary feasibility gate. The best trajectory-enabling weighted cases still
  had approach qdot saturation fractions between `0.8875` and `0.9995` plus
  millimeter-scale planar drift.
- Limit:
  This is E1-only tilted-plane simulation evidence. It does not solve Stage A
  and does not validate hardware.
- Next step:
  Stop simple Stage A scalar/slack bracketing. Choose a redesigned approach
  controller, a longer scheduled approach with explicit approach-specific
  gates, or a documented relaxed-budget prealignment decision.

## 2026-05-24 v26 Long Approach Probe

- Branch: `exp/tase-ur10e-v26-long-approach-probe`
- Starting commit: `2b2f515988ed1f703f26fbba73a850fa40780edd`
- Files added:
  - `reports/long_approach_probe_report.md`
  - `runs/staged_orientation_long_approach_probe/20260524T094156`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_long_approach_probe/20260524T094156/<case> --approach-duration-s <duration> --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode <mode> --approach-orientation-kp <gain> --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The probe covered six longer Stage A cases from `4 s` to `18 s`. Approach
  terminal-orientation pass count was `3 / 6`, terminal approach-budget pass
  count was `0 / 6`, trajectory-after-approach pass count was `0 / 6`, and
  full staged-feasibility pass count was `0 / 6`.
- Limit:
  This is E1-only tilted-plane simulation evidence. It does not introduce a
  new controller and does not validate hardware.
- Next step:
  Implement or test an orientation-rate-limited approach schedule, or record a
  relaxed-budget approach decision. Do not keep extending the same low-gain
  Stage A probe without a controller change.

## 2026-05-24 v27 Approach Rate Cap

- Branch: `exp/tase-ur10e-v27-approach-rate-cap`
- Starting commit: `5bf5cb829744625a52905d82e996b20515049f84`
- Files added:
  - `reports/approach_rate_cap_report.md`
  - `runs/staged_orientation_rate_cap_probe/20260524T094752`
- Files updated:
  - `src/tase_repro/force_feedback.py`
  - `src/tase_repro/staged_force_motion.py`
  - `scripts/run_staged_orientation_force_motion.py`
  - `tests/test_staged_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/force_feedback.py src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_rate_cap_probe/20260524T094752/<case> --approach-duration-s <duration> --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode <mode> --approach-orientation-kp 2.0 --approach-max-angular-command-rad-s <cap> --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The cap was respected in all six probe cases. Approach terminal-orientation
  pass count was `5 / 6`, trajectory-after-approach pass count was `3 / 6`,
  and full staged-feasibility pass count was `0 / 6`. The best capped weighted
  qdot saturation fraction was `0.46366666666666667`, still above the current
  `0.01` budget, and weighted planar drift remained above `0.0075 m`.
- Limit:
  This is E1-only tilted-plane simulation evidence. It adds useful command
  limiting instrumentation but does not solve Stage A.
- Next step:
  Stop changing only orientation command magnitude. Test a position-hold or
  contact/position-first task structure, or record a relaxed-budget
  prealignment decision before expanding staged checks to E2-E4.

## 2026-05-24 v28 Approach Qdot Budget

- Branch: `exp/tase-ur10e-v28-approach-qdot-budget`
- Starting commit: `f621584c6a3e90cf8ed55837d317ac9e4541e30b`
- Files added:
  - `reports/approach_qdot_budget_report.md`
  - `runs/staged_orientation_approach_qdot_budget_probe/20260524T095305`
- Files updated:
  - `src/tase_repro/staged_force_motion.py`
  - `scripts/run_staged_orientation_force_motion.py`
  - `tests/test_staged_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_approach_qdot_budget_probe/20260524T095305/<case> --approach-duration-s 4.0 --trajectory-duration-s 2.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s <limit> --trajectory-qdot-limit-rad-s 0.15 --trajectory e1-cycloid --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode <mode> --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The staged helper and runner now support separate approach and trajectory
  qdot limits. The seven-case probe produced `4 / 7` approach terminal
  orientation passes, `0 / 7` terminal approach-budget passes, `3 / 7`
  trajectory-after-approach passes, and `0 / 7` full staged-feasibility
  passes.
- Limit:
  This is E1-only tilted-plane simulation evidence. It tests qdot budget
  separation, not a new task-priority solver.
- Next step:
  Stop treating qdot relaxation alone as sufficient. Either implement a real
  position/contact-first approach formulation or explicitly decide that
  prealignment is a relaxed-drift phase outside paper-trajectory feasibility.

## 2026-05-24 v29 Staged E1-E4 After Prealignment

- Branch: `exp/tase-ur10e-v29-staged-e1-e4-after-prealign`
- Starting commit: `7045c23005cd9932e4b8bc6a9c2f57ff74fc11dc`
- Files added:
  - `reports/staged_e1e4_after_prealign_report.md`
  - `runs/staged_orientation_e1e4_after_prealign/20260524T095804`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... summary aggregate check ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e1e4_after_prealign/20260524T095804/<trajectory> --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory <trajectory> --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.1 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The four-case matrix produced `4 / 4` approach terminal-orientation passes,
  `0 / 4` approach ordinary-feasibility passes, `3 / 4`
  trajectory-after-approach passes, `3 / 4` trajectory-feasibility passes, and
  `0 / 4` full staged-feasibility passes. E1, E3, and E4 pass Stage B after
  the weighted prealignment. E2 fails Stage B only on qdot saturation fraction
  `0.9935` and tail qdot utilization `1.0`.
  Validation passed with `54 passed in 1.19s`, `git diff --check`, and
  aggregate check `4 0 3 0`.
- Limit:
  This is a tilted-plane simulation matrix at `paper_time_scale = 0.075`.
  Stage A remains infeasible under the ordinary budget, and E2 remains a
  post-prealignment qdot-budget blocker.
- Next step:
  Run a focused E2 post-prealignment timing/task-priority bracket, or replace
  the Stage A task structure instead of accepting relaxed-drift prealignment
  as a full staged reproduction.

## 2026-05-24 v30 E2 After Prealignment Bracket

- Branch: `exp/tase-ur10e-v30-e2-after-prealign-bracket`
- Starting commit: `5e98b0f3516e6a171de6151046bda12be3bfca78`
- Files added:
  - `reports/e2_after_prealign_bracket_report.md`
  - `runs/staged_orientation_e2_after_prealign_bracket/20260524T100429`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... summary aggregate check ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e2_after_prealign_bracket/20260524T100429/scale<scale>_kp<kp> --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale <0.075|0.05|0.025> --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp <0.10|0.05|0.02|0.00> --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The 12-case bracket produced `12 / 12` approach terminal-orientation passes,
  `0 / 12` approach ordinary-feasibility passes, `0 / 12`
  trajectory-after-approach passes, and `0 / 12` full staged-feasibility
  passes. Every Stage B row failed only qdot saturation and tail qdot
  utilization. The slowest zero-gain case (`scale0p025_kp0p00`) still had
  qdot saturation fraction `0.906` and tail qdot utilization `1.0`.
  Validation passed with `54 passed in 1.21s`, `git diff --check`, and
  aggregate check `12 0 0 0`.
- Limit:
  This is E2-only tilted-plane simulation evidence under the same
  post-prealignment posture. It does not test posture redesign or a new
  tangent allocation.
- Next step:
  Stop scalar E2 timing/gain expansion. Test posture/prealignment terminal
  configuration changes or add a posture/nullspace objective before E2.

## 2026-05-24 v31 E2 Short Approach Bracket

- Branch: `exp/tase-ur10e-v31-e2-short-approach-bracket`
- Starting commit: `63a7910bd10d43e55ed2ecf05137745f8245e53f`
- Files added:
  - `reports/e2_short_approach_bracket_report.md`
  - `runs/staged_orientation_e2_short_approach_bracket/20260524T101113`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... summary aggregate check ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e2_short_approach_bracket/20260524T101113/approach<duration> --approach-duration-s <0.94|1.00|1.20|2.00|4.00> --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The five-case bracket produced `5 / 5` approach terminal-orientation passes,
  `0 / 5` approach ordinary-feasibility passes, `0 / 5`
  trajectory-after-approach passes, and `0 / 5` full staged-feasibility
  passes. Shorter approaches reduced drift but made E2 fail orientation and
  angular gates; longer approaches recovered orientation but left E2 qdot
  saturation near `0.99`.
  Validation passed with `54 passed in 1.20s`, `git diff --check`, and
  aggregate check `5 0 0 0`.
- Limit:
  This is E2-only tilted-plane simulation evidence. It changes Stage A
  duration but not the posture objective or QP task structure.
- Next step:
  Stop duration-only Stage A changes for E2. Add a posture/nullspace objective
  or otherwise change the terminal configuration before retesting E2.

## 2026-05-24 v32 E2 Posture Regularization

- Branch: `exp/tase-ur10e-v32-posture-regularization`
- Starting commit: `e1af9174121dedb56af4489dcffbe06f3ef8cb9b`
- Files added:
  - `reports/e2_posture_regularization_report.md`
  - `runs/staged_orientation_e2_posture_regularization/20260524T102224`
- Files updated:
  - `scripts/run_staged_orientation_force_motion.py`
  - `src/tase_repro/constraints.py`
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `src/tase_repro/staged_force_motion.py`
  - `tests/test_constraints.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... v32 posture matrix and summary aggregation ... PY`
  - `python3 - <<'PY' ... summary aggregate check ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e2_posture_regularization/20260524T102224/<case> --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory e2-figure-eight --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03 [optional posture flags]`
- Result:
  The controller now supports an optional joint-velocity posture target inside
  the bounded solve. In `linear-primary` mode, the primary linear solve keeps
  its existing behavior while the posture target is applied in the secondary
  objective that preserves primary TCP linear velocity. The 10-case E2 matrix
  produced `10 / 10` approach terminal-orientation passes, `0 / 10` approach
  ordinary-feasibility passes, `4 / 10` trajectory-after-approach passes, and
  `0 / 10` full staged-feasibility passes. Moderate trajectory posture
  weighting (`0.001` and `0.01`) removes the E2 qdot saturation failure;
  strong approach posture weighting (`0.1`) breaks contact/force tracking.
  Validation passed with `58 passed in 1.21s`, `git diff --check`, and
  aggregate check `10 0 4 0`.
- Limit:
  This fixes the isolated E2 Stage B blocker after the current relaxed
  weighted prealignment, but it does not fix Stage A. The result remains
  simulation-only and is not hardware-ready.
- Next step:
  Preserve the moderate trajectory posture objective and retest the staged
  E1-E4 matrix, or focus directly on a new Stage A task structure that avoids
  sustained qdot saturation and unbounded drift.

## 2026-05-24 v33 Staged E1-E4 With Trajectory Posture Regularization

- Branch: `exp/tase-ur10e-v33-e1e4-posture-regularized`
- Starting commit: `5892c29ae030c19b518eaddafdf0185726fbc04d`
- Files added:
  - `reports/staged_e1e4_posture_regularized_report.md`
  - `runs/staged_orientation_e1e4_posture_regularized/20260524T102747`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... v33 E1-E4 posture-regularized matrix and summary aggregation ... PY`
  - `python3 - <<'PY' ... summary aggregate check ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py --config configs/mujoco_ur10e_tilted_plane.yaml --output-dir runs/staged_orientation_e1e4_posture_regularized/20260524T102747/<trajectory> --approach-duration-s 4.0 --trajectory-duration-s 8.0 --target-force-N 5.0 --force-gain 5e-4 --r 0.5 --base-z-offset-m=-0.0011631221220595766 --initial-q 0,-0.1,0.15,-0.05,0,0 --qdot-limit-rad-s 0.15 --approach-qdot-limit-rad-s 0.25 --trajectory-qdot-limit-rad-s 0.15 --trajectory <trajectory> --omega-rad-s 0.1 --paper-time-scale 0.075 --planar-kp 0.5 --planar-slack-weight 1.0 --normal-slack-weight 10000.0 --slack-constraint-weight 1000.0 --normal-velocity-mode contact-normal --approach-orientation-priority-mode weighted --approach-orientation-kp 2.0 --trajectory-orientation-priority-mode linear-primary --trajectory-orientation-kp 0.10 --angular-axis-weight 1.0 --angular-slack-weight 1.0 --trajectory-posture-target-q 0,-0.1,0.15,-0.05,0,0 --trajectory-posture-kp 1.0 --trajectory-posture-weight 0.001 --trajectory-max-posture-velocity-rad-s 0.05 --approach-orientation-threshold-rad 0.03 --max-orientation-error-rad 0.03 --max-angular-slack-rad-s 0.03`
- Result:
  The four-case E1-E4 matrix produced `4 / 4` approach terminal-orientation
  passes, `0 / 4` approach ordinary-feasibility passes, `4 / 4`
  trajectory-after-approach passes, and `0 / 4` full staged-feasibility
  passes. Every Stage B trajectory has no failed criteria and qdot saturation
  fraction `0.0`. Validation passed with `58 passed in 1.22s`,
  `git diff --check`, and aggregate check `4 0 4 0`.
- Limit:
  This is slowed tilted-plane simulation evidence after the current weighted
  prealignment. It confirms Stage B after prealignment, not full staged
  feasibility.
- Next step:
  Stop tuning Stage B for the slowed E1-E4 matrix and focus on Stage A:
  either define an accepted relaxed approach budget or redesign the approach
  task priority so contact, drift, terminal orientation, and qdot saturation
  can pass together.

## 2026-05-24 v34 Planar-Primary Approach Priority

- Branch: `exp/tase-ur10e-v34-planar-primary-approach`
- Starting commit: `9973dd16cfb445487c02d843854e40fb3892af42`
- Files added:
  - `reports/planar_primary_approach_report.md`
  - `runs/staged_orientation_planar_primary_approach/20260524T103539`
  - `runs/staged_orientation_planar_primary_normal_weight/20260524T103646`
- Files updated:
  - `scripts/run_staged_orientation_force_motion.py`
  - `src/tase_repro/constraints.py`
  - `src/tase_repro/controller.py`
  - `src/tase_repro/force_feedback.py`
  - `tests/test_constraints.py`
  - `tests/test_controller.py`
  - `tests/test_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh`
  - `git diff --check`
  - `python3 - <<'PY' ... planar-primary approach bracket and summary aggregation ... PY`
  - `python3 - <<'PY' ... planar-primary normal-weight bracket and summary aggregation ... PY`
  - `python3 - <<'PY' ... summary aggregate checks ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py ... --approach-orientation-priority-mode planar-primary ...`
- Result:
  Added a general primary/secondary bounded solver and a `planar-primary`
  orientation priority mode. The first six-case bracket produced `6 / 6`
  terminal-orientation passes, `0 / 6` terminal-budget passes, `1 / 6`
  trajectory-after-approach passes, and `0 / 6` full staged passes. The
  planar-primary rows reduced x/y drift below `3e-5 m`, but lost contact and
  force tracking under default normal secondary weighting. The five-case
  normal-weight follow-up produced `1 / 5` terminal-orientation passes,
  `0 / 5` terminal-budget passes, `0 / 5` trajectory-after-approach passes,
  and `0 / 5` full staged passes. Strong normal weighting preserved force
  better but stalled orientation near `0.07 rad`. Validation passed with
  `61 passed in 1.26s`, `git diff --check`, and aggregate checks `6 0 1 0`
  and `5 0 0 0`.
- Limit:
  This is E1-only tilted-plane simulation evidence for Stage A structure. It
  does not establish a full approach solution or hardware readiness.
- Next step:
  Stop treating two-level planar-primary velocity priority as the fix. The
  next Stage A iteration should either define an explicit relaxed approach
  budget, or test a planned prealignment path with separately verified
  contact-maintenance and terminal-state gates.

## 2026-05-24 v35 Two-Phase Approach Recenter Probe

- Branch: `exp/tase-ur10e-v35-two-phase-approach-recenter`
- Starting commit: `aa9ba76c3ef6e5119efaddb0cdbce87d955879af`
- Files added:
  - `reports/two_phase_recenter_probe_report.md`
  - `runs/staged_orientation_two_phase_recenter/20260524T104957`
- Files updated:
  - `scripts/run_staged_orientation_force_motion.py`
  - `src/tase_repro/force_feedback.py`
  - `src/tase_repro/staged_force_motion.py`
  - `tests/test_force_motion.py`
  - `tests/test_staged_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/force_feedback.py src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
  - `scripts/run_tests.sh`
  - `python3 - <<'PY' ... two-phase recenter matrix and summary aggregation ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py ... --recenter-duration-s <duration> --recenter-orientation-priority-mode <mode> --setup-max-final-tangential-error-m 0.002 ...`
- Result:
  Added an explicit `planar_reference_xy_m` hook so a later phase can target
  the original setup x/y point, optional recenter support in the staged
  runner, and a setup terminal-state gate that checks final orientation, final
  x/y error, contact, tail force error, and hard qdot/joint-limit violations.
  The 10-case E2 matrix produced `0 / 10` setup terminal-state passes,
  `4 / 10` trajectory feasibility passes, `4 / 10` legacy
  trajectory-after-approach passes, `0 / 10` planned setup-then-trajectory
  passes, and `0 / 10` full staged-feasibility passes. Short linear-primary
  recenter windows keep Stage B passing but fail setup force and x/y gates.
  Long linear-primary recentering can meet the x/y and force terminal gates,
  but loses terminal orientation and makes Stage B fail.
- Validation:
  `scripts/run_tests.sh` passed with `63 passed in 1.31s`. The aggregate
  summary check reads `10 0 4 4 0 0`.
- Limit:
  This is E2-only tilted-plane simulation evidence. It does not establish a
  complete E1-E4 planned setup or hardware readiness.
- Next step:
  Stop scalar recenter-duration tuning. Either add a force-maintaining
  recenter formulation with phase-specific normal/force authority, or record
  an explicit relaxed setup budget that accepts weighted-prealignment drift
  without calling it paper-equivalent full staged feasibility.

## 2026-05-24 v36 Three-Phase Setup Settle Probe

- Branch: `exp/tase-ur10e-v36-three-phase-setup-settle`
- Starting commit: `4fdc9b8bc640871e0a7057f3b5bd70e87acc4ed8`
- Files added:
  - `reports/three_phase_settle_probe_report.md`
  - `runs/staged_orientation_three_phase_settle/20260524T110039`
- Files updated:
  - `scripts/run_staged_orientation_force_motion.py`
  - `src/tase_repro/staged_force_motion.py`
  - `tests/test_staged_force_motion.py`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/staged_force_motion.py scripts/run_staged_orientation_force_motion.py`
  - `scripts/run_tests.sh`
  - `python3 - <<'PY' ... three-phase settle matrix and summary aggregation ... PY`
  - `python3 scripts/run_staged_orientation_force_motion.py ... --recenter-duration-s <duration> --settle-duration-s <duration> --settle-orientation-priority-mode <weighted|linear-primary> ...`
- Result:
  Added optional `approach_settle` support after recentering. The 10-case E2
  matrix produced `0 / 10` setup terminal-state passes, `8 / 10` trajectory
  feasibility passes, `8 / 10` legacy trajectory-after-approach passes,
  `0 / 10` planned setup-then-trajectory passes, and `0 / 10` full staged
  passes. Weighted settle rows restore force/orientation enough for Stage B
  but return final x/y error to `7.2-8.3 mm`. The linear-primary settle row
  keeps x/y error near zero but fails terminal orientation and Stage B
  orientation.
- Validation:
  `scripts/run_tests.sh` passed with `64 passed in 1.38s`. The aggregate
  summary check reads `10 0 8 8 0 0`.
- Limit:
  This is E2-only tilted-plane simulation evidence. It does not establish a
  complete E1-E4 planned setup or hardware readiness.
- Next step:
  Stop scalar phase-duration bracketing under the current instantaneous
  velocity formulation. Either decision-record a relaxed setup budget that
  explicitly accepts weighted-prealignment drift, or change the Stage A
  mathematical formulation.

## 2026-05-24 v37 Setup Terminal IK Audit

- Branch: `exp/tase-ur10e-v37-terminal-ik-audit`
- Starting commit: `8d83f0117875c757051f1b7806a018caa4d70702`
- Files added:
  - `src/tase_repro/setup_terminal_ik.py`
  - `scripts/run_setup_terminal_ik_probe.py`
  - `tests/test_setup_terminal_ik.py`
  - `reports/setup_terminal_ik_audit_report.md`
  - `runs/setup_terminal_ik_audit/20260524T111150`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/setup_terminal_ik.py scripts/run_setup_terminal_ik_probe.py`
  - `scripts/run_tests.sh`
  - `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001`
- Result:
  Added a terminal nonlinear least-squares setup audit that removes Stage A
  path/controller constraints and directly searches for terminal joint states
  satisfying the setup x/y, force, contact, and force-normal orientation gate.
  The run produced `65` candidates and `0 / 65` terminal setup passes. The
  best candidate kept contact and force error small
  (`0.004835673570861232 N`) but still failed x/y
  (`0.002178947478445584 m`) and orientation
  (`0.05199834145021794 rad`) gates.
- Validation:
  `scripts/run_tests.sh` passed with `66 passed in 1.38s`.
- Limit:
  This is a terminal local IK audit, not a path/controller solution and not a
  global infeasibility proof. It uses the approximate tilted-plane MJCF and
  unverified 85 mm TCP.
- Next step:
  Define a relaxed setup-budget decision for the current UR10e adapted
  reproduction, or revisit model/TCP/contact geometry before designing another
  Stage A controller.

## 2026-05-24 v38 Relaxed Setup Budget

- Branch: `exp/tase-ur10e-v38-relaxed-setup-budget`
- Starting commit: `b39265de3af59fec4770e7a7f72e11141eb8c084`
- Files added:
  - `configs/ur10e_adapted_acceptance.yaml`
  - `src/tase_repro/relaxed_setup_budget.py`
  - `scripts/evaluate_relaxed_setup_budget.py`
  - `tests/test_relaxed_setup_budget.py`
  - `reports/relaxed_setup_budget_report.md`
  - `runs/relaxed_setup_budget_eval/20260524T111859`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/math_derivation_ur10e_transfer.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/relaxed_setup_budget.py scripts/evaluate_relaxed_setup_budget.py`
  - `scripts/run_tests.sh`
  - `scripts/evaluate_relaxed_setup_budget.py --run-root runs/staged_orientation_e1e4_posture_regularized/20260524T102747 --acceptance-config configs/ur10e_adapted_acceptance.yaml`
- Result:
  Defined a separate `ur10e_adapted_trajectory_after_relaxed_setup` label and
  evaluated the v33 slowed tilted-plane E1-E4 matrix under it. The evaluation
  produced `4 / 4` relaxed setup passes, `4 / 4` trajectory feasibility
  passes, `4 / 4` UR10e adapted trajectory-after-relaxed-setup passes, and
  `0 / 4` strict full staged feasibility passes.
- Validation:
  `scripts/run_tests.sh` passed with `68 passed in 1.38s`.
- Limit:
  This is acceptance bookkeeping for simulation results. It is not
  paper-equivalent full staged feasibility and not hardware readiness.
- Next step:
  Use this label in the completion audit and keep any future controller/model
  work separate from the accepted UR10e adapted simulation claim.

## 2026-05-24 v39 Completion Audit

- Branch: `exp/tase-ur10e-v39-completion-audit`
- Starting commit: `b0e431dae51a09a3923c2689eea79f34249fd775`
- Files added:
  - `reports/completion_audit.md`
- Files updated:
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `git status --short --branch`
  - `git log --oneline --decorate -n 10`
  - mandatory plan/report existence checks
  - `python3 - <<'PY' ... inspect v33/v36/v37/v38 summary metrics ... PY`
- Result:
  The audit maps the goal requirements to concrete artifacts and evidence.
  It confirms the current accepted claim is only the UR10e adapted slowed
  tilted-plane E1-E4 result under the relaxed setup budget. Strict
  paper-equivalent full staged feasibility, hardware readiness, and a separate
  paper-faithful 7DOF executable reproduction remain incomplete.
- Limit:
  This is an audit/documentation iteration, not a new controller or simulation
  result.
- Next step:
  Close the remaining PDF truth gap, validate or replace the approximate
  TCP/contact model, or create the separate paper-faithful 7DOF reproduction
  line before claiming the overall goal complete.

## 2026-05-24 v40 Section V z0 Audit

- Branch: `exp/tase-ur10e-v40-section-v-z0-audit`
- Starting commit: `879696285b3e8f69ecf765cef8e9eb0004e09613`
- Files added:
  - `reports/section_v_z0_audit.md`
- Files updated:
  - `configs/paper_truth.yaml`
  - `plans/PAPER_TRUTH_EXTRACTION.md`
  - `reports/paper_truth_extraction.md`
  - `reports/orientation_signal_ambiguity_audit.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `pdftotext -layout "<paper-pdf>" /tmp/tase_paper_v40_layout.txt`
  - `rg -n -C 8 "z0|z_0|0\\.2 cos|0\\.2cos|cos\\(0\\.2|SIMULATION|V\\." /tmp/tase_paper_v40_layout.txt`
  - `pdftotext -raw "<paper-pdf>" /tmp/tase_paper_v40_raw.txt`
  - `rg -n -C 8 "z0|z_0|0\\.2 cos|0\\.2cos|cos\\(0\\.2|SIMULATION|V\\." /tmp/tase_paper_v40_raw.txt`
  - `pdfinfo "<paper-pdf>"`
- Result:
  The final pending paper-truth extraction item is closed. Section V is now
  recorded as using `z0` without defining its source; Section VI's experiment
  `z0` definition remains separate. `configs/paper_truth.yaml` now has no
  `pending_pdf_verify` fields.
- Limit:
  This is a paper-truth audit only. It does not implement a separate
  paper-faithful 7DOF reproduction line and does not change UR10e hardware
  readiness.
- Next step:
  Validate or replace the approximate TCP/contact model, or create the
  separate paper-faithful 7DOF executable reproduction line before claiming
  the overall goal complete.

## 2026-05-24 v41 Paper 7DOF Executable Diagnostic

- Branch: `exp/tase-ur10e-v41-paper-7dof-line`
- Starting commit: `d298cb020f5e7e91d44c9becacd4003abf54dd26`
- Code commit:
  `bf7209d52476d951e99f6ed7cbce1c7acc3db0e8`
- Files added:
  - `src/tase_repro/panda_kinematics.py`
  - `src/tase_repro/paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py`
  - `tests/test_panda_kinematics.py`
  - `tests/test_paper_7dof.py`
  - `reports/paper_7dof_executable_diagnostic_report.md`
  - `runs/paper_7dof_section_v/20260524T113608/metrics.yaml`
  - `runs/paper_7dof_section_v/20260524T113608/metrics.json`
  - `runs/paper_7dof_section_v/20260524T113608/summary.md`
- Files updated:
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_panda_kinematics.py tests/test_paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc`
- Result:
  Created the first separate paper-platform 7DOF executable diagnostic path.
  The recorded run executes from a clean code commit, respects joint and qdot
  bounds, and remains finite. It does not pass force/contact behavior:
  `contact_force_tail_success = false`, `tail_contact_fraction = 0.0`, and
  `tail_force_error_mean_N = 5.0`.
- Validation:
  Targeted v41 tests passed with `6 passed in 0.08s`; full suite passed with
  `74 passed in 1.44s`.
- Limit:
  This is a diagnostic 7DOF executable line, not paper-faithful Fig.5/Fig.6
  parity and not hardware readiness.
- Next step:
  Debug the paper-platform normal-force/contact loop, or return to the UR10e
  TCP/contact model validation path. Do not claim the overall goal complete.

## 2026-05-24 v42 Paper 7DOF Contact Loop Diagnostic

- Branch: `exp/tase-ur10e-v42-paper-7dof-contact-loop`
- Starting commit: `d53251b7a5f4023d1fd048d35d0e984d2dd14f20`
- Code commit:
  `16ba42368f81145f2970c8d8d295f6ed238e7be4`
- Files updated:
  - `scripts/run_paper_7dof_section_v.py`
  - `tests/test_paper_7dof.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `docs/goal.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_7dof_contact_loop_report.md`
  - `runs/paper_7dof_section_v/20260524T114244/metrics.yaml`
  - `runs/paper_7dof_section_v/20260524T114244/metrics.json`
  - `runs/paper_7dof_section_v/20260524T114244/summary.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode pinv_bounded --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Result:
  The contact-stabilized 7DOF diagnostic run passed the tail contact-force
  gate: `contact_force_tail_success = true`, `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.013764149103712913`, and no q or qdot bound
  violations.
- Validation:
  Targeted paper 7DOF tests passed with `5 passed in 0.24s`; full suite
  passed with `75 passed in 1.53s`.
- Limit:
  This is still not paper-faithful KKT parity. The passing run uses
  `pinv_bounded` and a capped force integral; the v41 KKT-projection line
  still loses contact.
- Next step:
  Debug the KKT-projection contact loss or define a paper-platform parity gate
  against the legacy MATLAB/RNN outputs. Do not claim the overall goal
  complete.

## 2026-05-24 v43 Paper 7DOF KKT Contact Recovery

- Branch: `exp/tase-ur10e-v43-paper-7dof-kkt-sweep`
- Starting commit: `d655455ea47fbaa0fd9892266846f9404670a0e8`
- Code commit:
  `38216bba5e08af8fbf0f078583f438c044990d68`
- Files updated:
  - `tests/test_paper_7dof.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_7dof_kkt_contact_recovery_report.md`
  - `runs/paper_7dof_section_v/20260524T114736/metrics.yaml`
  - `runs/paper_7dof_section_v/20260524T114736/metrics.json`
  - `runs/paper_7dof_section_v/20260524T114736/summary.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py --duration-s 5.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
- Result:
  The capped-integral KKT diagnostic passed the tail contact-force gate:
  `contact_force_tail_success = true`, `tail_contact_fraction = 1.0`,
  `tail_force_error_mean_N = 0.06720487008205062`, and no q or qdot bound
  violations.
- Validation:
  Targeted paper 7DOF tests passed with `6 passed in 0.76s`; full suite
  passed with `76 passed in 2.10s`.
- Limit:
  The force-integral cap is diagnostic anti-windup, not a PDF-verified Section
  V parameter. This is still not paper-equivalent numerical parity.
- Next step:
  Define a paper-platform parity gate against legacy MATLAB/RNN outputs, or
  audit Panda/Franka DH model provenance before making stronger paper-platform
  claims.

## 2026-05-24 v44 Paper Platform Parity Gate

- Branch: `exp/tase-ur10e-v44-paper-platform-parity-gate`
- Starting commit: `e5b0ab2e66bfa31c937730ad50e56ec2637048f3`
- Files added:
  - `configs/paper_platform_parity.yaml`
  - `src/tase_repro/paper_platform_parity.py`
  - `scripts/evaluate_paper_platform_parity.py`
  - `tests/test_paper_platform_parity.py`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/paper_platform_parity_eval/20260524T115641/metrics.yaml`
  - `runs/paper_platform_parity_eval/20260524T115641/metrics.json`
  - `runs/paper_platform_parity_eval/20260524T115641/summary.md`
- Files updated:
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_platform_parity.py`
  - `scripts/evaluate_paper_platform_parity.py`
- Result:
  Defined a strict paper-platform parity gate against the legacy MATLAB/RNN
  Section V verification reports. The v43 Python capped-integral KKT
  candidate passes execution/contact/bounds and matches formula-faithful tail
  force, position, and orientation metrics within configured tolerances.
  Strict parity still fails because the candidate is only `5.0 s`, cannot
  expose q7 at `22 s`, has no Python Fig.5 r-sweep coverage, and uses the
  finite force-integral cap.
- Validation:
  Targeted parity tests passed with `3 passed in 0.04s`.
- Limit:
  This is a gate definition plus a failing evaluation. It improves claim
  discipline but does not achieve paper-equivalent numerical parity or
  hardware readiness.
- Next step:
  Run or implement a 30 s Python 7DOF candidate with q7-at-22 s and Fig.5
  r-sweep outputs, then address the capped-integral assumption or verify
  Panda/Franka model provenance.

## 2026-05-24 v45 Paper 7DOF 30 s Candidate

- Branch: `exp/tase-ur10e-v45-paper-7dof-30s-candidate`
- Starting commit: `7c7985c80adc40ccd115587d0db3df36930603e6`
- Code commit:
  `51f76512449051d278abe8f8a75cd96ed45480c8`
- Files updated:
  - `src/tase_repro/paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py`
  - `scripts/evaluate_paper_platform_parity.py`
  - `tests/test_paper_7dof.py`
  - `tests/test_paper_platform_parity.py`
  - `configs/paper_platform_parity.yaml`
  - `reports/paper_platform_parity_gate_report.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_7dof_30s_candidate_report.md`
  - `runs/paper_7dof_section_v/20260524T120439/metrics.yaml`
  - `runs/paper_7dof_section_v/20260524T120439/metrics.json`
  - `runs/paper_7dof_section_v/20260524T120439/summary.md`
  - `runs/paper_platform_parity_eval/20260524T120503/metrics.yaml`
  - `runs/paper_platform_parity_eval/20260524T120503/metrics.json`
  - `runs/paper_platform_parity_eval/20260524T120503/summary.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_7dof.py tests/test_paper_platform_parity.py`
  - `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
  - `scripts/evaluate_paper_platform_parity.py`
- Result:
  Added tracked q7-at-22 s metrics for long Python 7DOF runs and recorded a
  clean 30 s capped-integral KKT candidate. The candidate passes
  execution/contact/bounds and formula-faithful tail convergence tolerances.
  The strict parity gate now passes duration coverage but still fails
  `fig6_q7_22s_landmark`, `fig5_r_sweep_coverage`, and
  `paper_assumption_compatibility`.
- Validation:
  Targeted tests passed with `10 passed in 0.81s`.
- Limit:
  This is stronger paper-platform diagnostic evidence, not paper-equivalent
  numerical parity. The q7 landmark mismatch is now measured rather than
  missing.
- Next step:
  Investigate the Fig.6 q7 landmark mismatch, add Python Fig.5 r-sweep
  coverage, or remove/justify the force-integral cap before making stronger
  paper-platform claims.

## 2026-05-24 v46 Paper 7DOF Fig.5 r Sweep

- Branch: `exp/tase-ur10e-v46-paper-7dof-fig5-sweep`
- Starting commit: `59075df3bae1b03811208227ee8db7a2b030e39e`
- Code commit:
  `43f71fd79988f4f28549e213f542a3fa2fd30d28`
- Files added:
  - `scripts/run_paper_7dof_fig5_r_sweep.py`
  - `reports/paper_7dof_fig5_sweep_report.md`
  - `runs/paper_7dof_fig5_r_sweep/20260524T121033/**`
  - `runs/paper_platform_parity_eval/20260524T121116/metrics.yaml`
  - `runs/paper_platform_parity_eval/20260524T121116/metrics.json`
  - `runs/paper_platform_parity_eval/20260524T121116/summary.md`
- Files updated:
  - `configs/paper_platform_parity.yaml`
  - `src/tase_repro/paper_platform_parity.py`
  - `tests/test_paper_platform_parity.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_platform_parity.py`
  - `scripts/run_paper_7dof_fig5_r_sweep.py --duration-s 2.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-limit 0.1 --force-integral-leak 0.0`
  - `scripts/evaluate_paper_platform_parity.py`
- Result:
  Added Python 7DOF Fig.5 r-sweep coverage and made the parity gate validate
  each configured r metrics file. The v46 gate passes duration, Fig.5
  coverage, and formula-faithful tail convergence checks. Strict parity still
  fails on `fig6_q7_22s_landmark` and `paper_assumption_compatibility`.
- Limit:
  Fig.5 coverage is not Fig.5 numerical parity. The r-sweep rows are
  diagnostic and use the same capped-integral assumption as the current
  candidate.
- Next step:
  Investigate the q7-at-22 s mismatch or remove/justify the force-integral
  cap.

## 2026-05-24 v47 Paper 7DOF Uncapped KKT Candidate

- Branch: `exp/tase-ur10e-v47-paper-7dof-q7-variant-probe`
- Starting commit: `d4884d79c3e0702228e11205976bb8dc506e4472`
- Files updated:
  - `configs/paper_platform_parity.yaml`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_7dof_uncapped_candidate_report.md`
  - `runs/paper_7dof_section_v/20260524T121503/metrics.yaml`
  - `runs/paper_7dof_section_v/20260524T121503/metrics.json`
  - `runs/paper_7dof_section_v/20260524T121503/summary.md`
  - `runs/paper_platform_parity_eval/20260524T121542/metrics.yaml`
  - `runs/paper_platform_parity_eval/20260524T121542/metrics.json`
  - `runs/paper_platform_parity_eval/20260524T121542/summary.md`
- Commands run:
  - `scripts/run_paper_7dof_section_v.py --duration-s 30.0 --dt-s 0.002 --solver-mode kkt_projection --orientation-mode force_shortest_arc --communication-delay-s 0.032 --force-integral-leak 0.0`
  - `scripts/evaluate_paper_platform_parity.py`
- Result:
  Recorded an uncapped 30 s KKT candidate. It passes execution/contact/bounds
  and formula-faithful tail convergence checks. The strict parity gate now
  passes duration coverage, Fig.5 coverage, and paper-assumption compatibility.
  It fails only on `fig6_q7_22s_landmark`.
- Limit:
  This is still not paper-equivalent numerical parity because
  `q7@22s = 1.6680622878116045 rad`, while the figure-match reference is
  `2.5 rad`.
- Next step:
  Investigate the q7 landmark mismatch directly.

## 2026-05-24 v48 Paper 7DOF q7 Mismatch Probe

- Branch: `exp/tase-ur10e-v48-paper-7dof-q7-mismatch-probe`
- Starting commit: `5a6888ae76edf448ed61135941b50199d2bcf8af`
- Code commit:
  `48683797d62c4bbee0d8e1dbaeaacd5a4c545b68`
- Files added:
  - `scripts/run_paper_7dof_q7_variant_probe.py`
  - `reports/paper_7dof_q7_variant_probe_report.md`
  - `runs/paper_7dof_q7_variant_probe/20260524T122345/**`
- Files updated:
  - `tests/test_paper_7dof.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_7dof.py`
  - `scripts/run_paper_7dof_q7_variant_probe.py --duration-s 30.0 --dt-s 0.002 --communication-delay-s 0.032 --force-integral-leak 0.0`
  - `scripts/run_tests.sh`
- Result:
  Added a reusable q7 variant probe and recorded a full 30 s, eight-variant
  matrix. All variants executed successfully, all exposed q7 at 22 s, q7
  stayed within `1.661263839866546-1.6835894792145727 rad`, and
  `figure_match_pass_count = 0`.
- Validation:
  Full tests passed with `81 passed in 2.32s`.
- Limit:
  This does not pass strict paper-platform parity. It narrows the remaining
  q7 mismatch away from the tested solver/orientation/cap knobs and toward
  model provenance, redundancy/nullspace behavior, or legacy figure-match
  tuning.
- Next step:
  Compare Python Panda kinematics and q trajectories against legacy MATLAB
  Fig.6 raw data or audit the figure-match q7 landmark provenance.

## 2026-05-24 v49 Paper Fig.6 Raw Provenance Audit

- Branch: `exp/tase-ur10e-v49-paper-fig6-raw-provenance-audit`
- Starting commit: `8228c1bd2b97dca7a170e73a9432e5709801b585`
- Code commit:
  `b5941061881fd5962e4b2504b40d1f0f61575704`
- Files added:
  - `scripts/compare_paper_7dof_fig6_raw_provenance.py`
  - `reports/paper_7dof_fig6_raw_provenance_report.md`
  - `runs/paper_7dof_fig6_raw_provenance/20260524T123130/**`
- Files updated:
  - `tests/test_panda_kinematics.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_panda_kinematics.py`
  - `scripts/compare_paper_7dof_fig6_raw_provenance.py`
- Result:
  The Python Panda FK/Jacobian port matches sampled legacy formula-faithful
  and figure-match raw Fig.6 states to numerical precision. The q7 landmark
  mismatch is now tied to legacy figure-match provenance: the legacy
  figure-match line uses `pinv_bounded`, `normal_only`, `admittance_proxy`,
  and `landmark` acceptance, while the Python candidate uses `paper_literal`.
  The legacy figure-match q7 trajectory is exactly at the upper limit for
  `17829` samples and first nears the limit at `11.872999999998859 s`.
- Validation:
  Full tests passed with `82 passed in 2.20s`.
- Limit:
  This still does not pass the strict parity gate. It narrows the remaining
  paper-platform issue to the claim structure around the figure-match
  landmark or the need for a separate Python `admittance_proxy` figure-match
  candidate.
- Next step:
  Audit the legacy `admittance_proxy` force loop and figure-match tuning
  source, then decide whether to implement that line in Python or revise the
  strict gate claim structure.

## 2026-05-24 v50 Legacy Figure-Match Source Audit

- Branch: `exp/tase-ur10e-v50-legacy-figure-match-source-audit`
- Starting commit: `13ff58a68dcca6129e9a00a67e3f8bd089b9dcf5`
- Code commit:
  `deaf21d52abb86e52ed146ddafe7a80e147dd773`
- Files added:
  - `scripts/audit_legacy_figure_match_source.py`
  - `tests/test_legacy_figure_match_source_audit.py`
  - `reports/legacy_figure_match_source_audit_report.md`
  - `runs/legacy_figure_match_source_audit/20260524T123651/**`
- Files updated:
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_legacy_figure_match_source_audit.py`
  - `scripts/audit_legacy_figure_match_source.py`
- Result:
  The legacy `figure_match` path has eight non-paper-faithful tuning knobs:
  `normal_only`, `pinv_bounded`, `admittance_proxy`, `landmark`,
  `alpha = 20.0`, `maxAngularSpeed = 1.5`, `kp = 25.0`, and
  `q7NullspaceSpeed = 0.35`. The q7 nullspace speed is explicitly wired into
  the pseudoinverse nullspace branch, and the raw trajectory pins q7 at the
  upper limit for `17829` samples.
- Validation:
  Full tests passed with `83 passed in 2.28s`.
- Limit:
  This does not implement a Python figure-match candidate and does not pass
  the existing strict parity gate. It resolves the source provenance question
  enough to revise the gate claim structure.
- Next step:
  Split the paper-platform gate into formula-faithful parity and
  figure-match landmark evidence, or implement a separately labeled Python
  figure-match candidate.

## 2026-05-24 v51 Split Paper-Platform Parity Claims

- Branch: `exp/tase-ur10e-v51-split-paper-parity-claims`
- Starting commit: `4f3e21653526d252277ee6988ffd00f78076f1b6`
- Code commit:
  `bddf1dad1645199de92458616162291b6881aa4c`
- Files updated:
  - `src/tase_repro/paper_platform_parity.py`
  - `scripts/evaluate_paper_platform_parity.py`
  - `tests/test_paper_platform_parity.py`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `plans/MATH_TRANSFER_7DOF_TO_UR10E_6DOF.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `reports/paper_platform_parity_gate_report.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_platform_split_claim_report.md`
  - `runs/paper_platform_parity_eval/20260524T124200/**`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_platform_parity.py`
  - `scripts/evaluate_paper_platform_parity.py`
- Result:
  The paper-platform evaluator now reports split claim levels. The v51 run
  has `paper_platform_formula_convergence_pass = true`,
  `paper_platform_figure_match_landmark_pass = false`, and
  `paper_platform_parity_pass = false`. The next-thread goal prompt now points
  future work at the v51 branch, the completion audit, and the split claim
  boundary before any further implementation.
- Validation:
  Full tests passed with `84 passed in 2.28s`.
- Limit:
  This is a claim-structure fix, not full paper-equivalent numerical parity.
  The candidate still does not reproduce the tuned figure-match q7 landmark.
- Next step:
  Implement a separately labeled Python figure-match candidate if that
  landmark is still needed, or proceed with UR10e adapted work using the
  formula-convergence claim boundary.

## 2026-05-24 v52 Python Tuned Figure-Match Candidate

- Branch: `exp/tase-ur10e-v52-python-figure-match-candidate`
- Starting commit:
  `c7d3ebfd9c0d3c3a2558a711d3e20b952dbdd617`
- Code commit:
  `2f65a5908528670868ed5d9e4ffab9f8443b77a2`
- Files updated:
  - `src/tase_repro/paper_7dof.py`
  - `scripts/run_paper_7dof_section_v.py`
  - `scripts/compare_paper_7dof_fig6_raw_provenance.py`
  - `tests/test_paper_7dof.py`
  - `reports/ITERATION_LOG.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Files added:
  - `reports/paper_7dof_tuned_figure_match_candidate_report.md`
  - `reports/paper_7dof_tuned_figure_match_provenance_report.md`
  - `reports/paper_platform_split_evidence_report.md`
  - `runs/paper_7dof_section_v/20260524T134441/**`
  - `runs/paper_7dof_fig6_raw_provenance/20260524T134549/**`
- Commands run:
  - `scripts/run_tests.sh tests/test_paper_7dof.py`
  - `scripts/run_tests.sh`
  - `scripts/run_paper_7dof_section_v.py --figure-match-preset --duration-s 30 --dt-s 0.001`
  - `scripts/compare_paper_7dof_fig6_raw_provenance.py --python-label python_v52_tuned_figure_match --python-raw-npz runs/paper_7dof_section_v/20260524T134441/paper_7dof_section_v_raw.npz --python-metrics-yaml runs/paper_7dof_section_v/20260524T134441/metrics.yaml`
- Result:
  The Python paper-platform runner now has an explicitly labeled
  `paper_platform_7dof_tuned_figure_match_candidate`. The formal run records
  `fig6_q7_at_22s_rad = 2.4999999999331863` and
  `fig6_q7_abs_error_to_2p5_rad = 6.681366571115177e-11`. The provenance
  comparison records legacy-vs-Python figure-match joint RMSE of
  `6.081574510252252e-09 rad`.
- Validation:
  Full tests passed with `85 passed in 2.26s`.
- Limit:
  This is a tuned landmark reproduction candidate. It uses
  `admittance_proxy` and q7 nullspace bias and must not be relabeled as
  formula-faithful paper-equivalent parity.
- Next step:
  Move to UR10e adapted TCP/contact model validation before any hardware gate.

## 2026-05-24 v53 UR10e TCP/Contact Model Audit

- Branch: `exp/tase-ur10e-v53-tcp-contact-model-audit`
- Starting commit:
  `936baee1b7ed1898bc889afdd944133ce3738aa3`
- Code commit:
  `d8d9c26d36bf9b08169aee333b39d26460b5803c`
- Files added:
  - `src/tase_repro/tcp_contact_model_audit.py`
  - `scripts/audit_tcp_contact_model.py`
  - `tests/test_tcp_contact_model_audit.py`
  - `reports/tcp_contact_model_audit_report.md`
  - `runs/tcp_contact_model_audit/20260524T135607/**`
  - `runs/setup_terminal_ik_audit/20260524T135619/**`
- Files updated:
  - `reports/setup_terminal_ik_audit_report.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `docs/goal.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_tcp_contact_model_audit.py`
  - `scripts/audit_tcp_contact_model.py`
  - `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The TCP/contact audit verifies that the config TCP guess and MJCF body
  offset both use the EOAT note distance of `0.085 m`, but the
  `tcp_site_unverified_85mm` site is coincident with the center of the
  colliding `contact_tip` sphere. The actual simulated plane-contact surface
  is one sphere radius away from the site, with
  `site_to_sphere_surface_projection_on_normal_m = 0.04500000000000001` and
  `parent_to_sphere_surface_distance_m = 0.12955222618906498`.
- Terminal setup rerun:
  The v53 rerun preserves the strict terminal setup failure: `0 / 65` passes.
  The best candidate has force error `0.004835673570861232 N`, x/y error
  `0.002178947478445584 m`, orientation error
  `0.05199834145021794 rad`, and failed criteria
  `tangential_error_m;orientation_error_rad`.
- Limit:
  This validates the current model convention problem; it does not replace the
  model or make the result hardware-ready. The 85 mm EOAT note is still
  unverified as either a physical contact point or a sphere-center/tool-frame
  point.
- Validation:
  Full tests passed with `87 passed in 2.25s`. `git diff --check` passed.
- Next step:
  Create an explicit replacement model variant with a named contact-point
  convention, or measure the mounted EOAT stack and regenerate the MJCF/config
  before rerunning the terminal setup audit.

## 2026-05-24 v54 TCP Contact-Point Model Variant

- Branch: `exp/tase-ur10e-v54-tcp-contact-point-model`
- Starting commit:
  `9dca0b65a594dc70f4cd3fae0a0e565669e4ea0d`
- Code commits:
  - `1ee13f89d693f008fdb83079181472f8716f8341`
  - `d504e3dcefcf5bb4bd5ac416a44eff62b2828c63`
  - `1725f4c28796fc844dc1d350236755e6c4d59c28`
- Files added:
  - `assets/mjcf/ur10e_tilted_plane_10deg_tcp_contact_point.xml`
  - `configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
  - `reports/tcp_contact_point_model_variant_report.md`
  - `runs/tcp_contact_model_audit/20260524T140535/**`
  - `runs/setup_terminal_ik_audit/20260524T140539/**`
- Files updated:
  - `src/tase_repro/tcp_contact_model_audit.py`
  - `scripts/audit_tcp_contact_model.py`
  - `tests/test_tcp_contact_model_audit.py`
  - `reports/setup_terminal_ik_audit_report.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `docs/goal.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_tcp_contact_model_audit.py`
  - `scripts/audit_tcp_contact_model.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml`
  - `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count 64 --random-seed-std-rad 0.15 --random-seed 37 --max-nfev 300 --posture-weight 0.0001`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The v54 model keeps the `85 mm` TCP site as the intended contact point and
  moves the colliding sphere center to local `[0, 0, 0.045]`. The audit records
  `site_coincident_with_contact_geom_center = false`,
  `contact_surface_offset_requires_model_decision = false`,
  `site_to_sphere_surface_projection_on_normal_m = 0.0006836511144550518`,
  and `surface_extension_beyond_declared_tcp_m = -0.00068365111445505`.
- Terminal setup rerun:
  The strict terminal setup gate still fails with `0 / 65` passing candidates.
  The best candidate has force error `0.0050975519688662985 N`, x/y error
  `0.0030075788240061675 m`, orientation error
  `0.07240603253666981 rad`, and failed criteria
  `tangential_error_m;orientation_error_rad`.
- Limit:
  This resolves the simple center/site collision-proxy convention in
  simulation only. It does not measure the mounted EOAT stack and does not
  make the model hardware-ready.
- Validation:
  Full tests passed with `88 passed in 2.25s`. `git diff --check` passed.
- Next step:
  Run a broader terminal feasibility or gate-definition audit on the v54
  contact-point model before designing another Stage A controller.

## 2026-05-24 v55 Broad Terminal Feasibility Audit

- Branch: `exp/tase-ur10e-v55-broad-terminal-feasibility`
- Starting commit:
  `1e4a8318efd4a77a077fd04e7b09485280e73345`
- Code commit:
  `8da8828ac9182816459bcb54e129d33413fcfa98`
- Files updated:
  - `src/tase_repro/contact_ladder.py`
  - `src/tase_repro/setup_terminal_ik.py`
  - `scripts/run_setup_terminal_ik_probe.py`
  - `tests/test_setup_terminal_ik.py`
  - `reports/setup_terminal_ik_audit_report.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `docs/goal.md`
- Files added:
  - `reports/broad_terminal_feasibility_audit_report.md`
  - `runs/setup_terminal_ik_audit/20260524T141321/**`
- Commands run:
  - `scripts/run_tests.sh tests/test_setup_terminal_ik.py tests/test_tcp_contact_model_audit.py`
  - `python3 -m py_compile src/tase_repro/contact_ladder.py src/tase_repro/setup_terminal_ik.py scripts/run_setup_terminal_ik_probe.py`
  - `scripts/run_setup_terminal_ik_probe.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count 512 --random-seed-std-rad 2.0 --random-seed 541 --max-nfev 800 --posture-weight 0.0`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The terminal setup audit now gates force/contact on the named
  `contact_plane` / `contact_tip` pair and records total contact force
  separately. This closes a broad-seed false-positive path where self-collision
  force could previously satisfy the force gate.
- Broad terminal run:
  The v55 broad run reports `0 / 513` passing candidates. The best target
  contact candidate has force error `0.005097546556703136 N`, x/y error
  `0.0030075762251302427 m`, orientation error
  `0.07240605683117833 rad`, and failed criteria
  `tangential_error_m;orientation_error_rad`.
- Limit:
  This is still not a global infeasibility proof. Most broad seeds lose target
  contact, and local least-squares is weak at discovering a discontinuous
  contact manifold from non-contact states.
- Validation:
  Full tests passed with `89 passed in 2.27s`. `git diff --check` passed.
- Next step:
  Build a contact-manifold or gate-definition audit that seeds from known
  target-contact states and explicitly tests whether the current x/y, force,
  and orientation gates are mutually compatible under UR10e 6DOF geometry.

## 2026-05-24 v56 Contact-Manifold Gate Audit

- Branch: `exp/tase-ur10e-v56-contact-manifold-gate-audit`
- Starting commit:
  `429b9626352cbf92b1fe045cf57b4c583fd9e26b`
- Code commits:
  - `e8a51253b29306999838f38ed8177b3de41bfef0`
  - `2d5a34aec3a2f1e490bbeef7f8b7c79ed87cdf96`
  - `1d83e8f99ca29c75b1392d16033327df0d340d99`
- Files added:
  - `src/tase_repro/contact_manifold_gate_audit.py`
  - `scripts/audit_contact_manifold_setup_gate.py`
  - `tests/test_contact_manifold_gate_audit.py`
  - `reports/contact_manifold_gate_audit_report.md`
  - `runs/contact_manifold_gate_audit/20260524T142404/**`
- Files updated:
  - `reports/setup_terminal_ik_audit_report.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `docs/goal.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_contact_manifold_gate_audit.py`
  - `python3 -m py_compile src/tase_repro/contact_manifold_gate_audit.py scripts/audit_contact_manifold_setup_gate.py`
  - `scripts/audit_contact_manifold_setup_gate.py --config configs/mujoco_ur10e_tilted_plane_tcp_contact_point.yaml --random-seed-count-per-std 40 --random-seed-stds-rad 0.03,0.1,0.3,0.8 --random-seed 761 --max-nfev 800`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The v56 audit seeds from known target-contact neighborhoods and tests gate
  combinations. The strict `xy_force_orientation` case reports `0 / 161`
  passes. The best strict candidate has force error
  `0.005097551486581864 N`, x/y error `0.0030075787462736734 m`, and
  orientation error `0.07240603326354965 rad`.
- Gate-definition evidence:
  `xy_force` can satisfy force and x/y but leaves orientation error
  `0.14697007178233126 rad`; `xy_orientation` can satisfy x/y and orientation
  but loses target contact and force; the best optimized `force_orientation`
  candidate has x/y error `0.014127706733724453 m`.
- Limit:
  This is still not a mathematical global infeasibility proof, but it is
  strong enough to stop scalar phase-scheduling work under the current gate
  definition.
- Validation:
  Full tests passed with `90 passed in 2.44s`. `git diff --check` passed.
- Next step:
  Explicitly relax or redefine the UR10e adapted setup gate, or change the
  setup target definition, before designing another Stage A controller.

## 2026-05-24 v57 Adapted Terminal Setup Diagnostic Gate

- Branch: `exp/tase-ur10e-v57-adapted-terminal-gate`
- Starting commit:
  `e93a0509f4b5e0f2a3858cfba4db3d45e7f43b10`
- Code commit:
  `167ca325dd71c2d25281ebe1c86a7e7e27c85d94`
- Files added:
  - `src/tase_repro/terminal_setup_gate.py`
  - `scripts/evaluate_terminal_setup_gate.py`
  - `tests/test_terminal_setup_gate.py`
  - `reports/adapted_terminal_setup_gate_report.md`
  - `runs/terminal_setup_gate_eval/20260524T143019/**`
- Files updated:
  - `configs/ur10e_adapted_acceptance.yaml`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `docs/goal.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_terminal_setup_gate.py`
  - `python3 -m py_compile src/tase_repro/terminal_setup_gate.py scripts/evaluate_terminal_setup_gate.py`
  - `scripts/evaluate_terminal_setup_gate.py --setup-metrics runs/setup_terminal_ik_audit/20260524T141321/metrics.yaml --acceptance-config configs/ur10e_adapted_acceptance.yaml`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `ur10e_adapted_terminal_setup_diagnostic_gate` with x/y threshold
  `0.004 m`, orientation threshold `0.08 rad`, force threshold `0.25 N`, and
  target contact count `>= 1`. The v57 evaluation reports `1 / 513` passing
  terminal candidates under this diagnostic-only gate.
- Limit:
  This is not a path, trajectory, paper-equivalent, or hardware-readiness
  claim.
- Validation:
  Full tests passed with `92 passed in 2.41s`. `git diff --check` passed.
- Next step:
  Before any new Stage A controller work, choose which setup label the
  controller targets: strict paper-equivalent setup, v38 relaxed
  trajectory-after-setup budget, or v57 diagnostic terminal setup.

## 2026-05-24 v58 Stage A Target Selection

- Branch: `exp/tase-ur10e-v58-stage-a-target-selection`
- Starting commit:
  `6209be0a09a525bb01b43d8a9e4d01521768d131`
- Files added:
  - `configs/ur10e_adapted_stage_a_target.yaml`
  - `reports/stage_a_target_selection_report.md`
- Files updated:
  - `README.md`
  - `docs/goal.md`
  - `plans/MASTER_PLAN.md`
  - `plans/MUJOCO_ENVIRONMENT_PLAN.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
  - `tests/test_terminal_setup_gate.py`
- Commands run:
  - `scripts/run_tests.sh tests/test_terminal_setup_gate.py`
  - `python3 -m py_compile src/tase_repro/terminal_setup_gate.py scripts/evaluate_terminal_setup_gate.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The next Stage A simulation prototype target label is now explicitly
  selected as `ur10e_adapted_terminal_setup_diagnostic`. The selected target
  comes from `runs/terminal_setup_gate_eval/20260524T143019/metrics.yaml` and
  uses q =
  `[-1.1745579135426345e-08, -0.02440152369247043, -0.00048297839388595083, 0.0002982283198967393, 2.405416739224147e-10, 0.12671314216940235]`.
- Limit:
  This is a target-selection decision only. It is not a controller
  implementation and not a path, trajectory, paper-equivalent, or hardware
  readiness claim.
- Validation:
  Full tests passed with `93 passed in 2.49s`. `git diff --check` passed.
- Next step:
  Implement or evaluate the next Stage A controller prototype against the v58
  selected diagnostic terminal setup target, while preserving the claim
  boundary.

## 2026-05-24 v59 Diagnostic Target Handoff Audit

- Branch: `exp/tase-ur10e-v59-diagnostic-target-handoff`
- Starting commit:
  `2aebf1bb10769a20349d6af69103ded12a0c09bc`
- Code commit:
  `7763394662bebd9376994d39ebdf7be524f1f04c`
- Files added:
  - `src/tase_repro/stage_a_target_handoff.py`
  - `scripts/evaluate_stage_a_target_handoff.py`
  - `tests/test_stage_a_target_handoff.py`
  - `reports/stage_a_target_handoff_report.md`
  - `runs/stage_a_target_handoff_eval/20260524T144654/**`
- Files updated:
  - `README.md`
  - `docs/goal.md`
  - `plans/MASTER_PLAN.md`
  - `plans/MUJOCO_ENVIRONMENT_PLAN.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_stage_a_target_handoff.py`
  - `python3 -m py_compile src/tase_repro/stage_a_target_handoff.py scripts/evaluate_stage_a_target_handoff.py`
  - `scripts/evaluate_stage_a_target_handoff.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Starting directly from the v58 selected diagnostic terminal q, E1-E4 keep
  target-pair contact and satisfy force, x/y, and diagnostic orientation
  thresholds, but the handoff pass count is `0 / 4`. Every row fails
  `qdot_saturation_fraction` and `tail_max_qdot_utilization`.
- Limit:
  This is a handoff audit only. It does not implement a Stage A path
  controller and is not path, trajectory, paper-equivalent, or hardware
  feasibility.
- Validation:
  Full tests passed with `96 passed in 2.40s`. `git diff --check` passed.
- Next step:
  Implement a qdot-aware Stage A/Stage B prototype against the diagnostic
  target, or explicitly change timing/gates before claiming trajectory
  feasibility.

## 2026-05-24 v60 Qdot-Aware Diagnostic Handoff

- Branch: `exp/tase-ur10e-v60-qdot-aware-diagnostic-handoff`
- Starting commit:
  `bfd60c8e7fbbd0f1cf56f73cb2e4f9875c6b0945`
- Code commit:
  `67b0f053f525cfbcf23db872ccc994d100ecca7f`
- Files added:
  - `reports/qdot_aware_diagnostic_handoff_report.md`
  - `runs/stage_a_target_handoff_eval/20260524T145433/**`
- Files updated:
  - `scripts/evaluate_stage_a_target_handoff.py`
  - `README.md`
  - `docs/goal.md`
  - `plans/MASTER_PLAN.md`
  - `plans/MUJOCO_ENVIRONMENT_PLAN.md`
  - `plans/CONTROLLER_IMPLEMENTATION_PLAN.md`
  - `plans/EXPERIMENT_MATRIX.md`
  - `reports/DECISION_RECORD.md`
  - `reports/ITERATION_LOG.md`
  - `reports/completion_audit.md`
  - `runs/RUN_ARTIFACTS_MANIFEST.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_stage_a_target_handoff.py`
  - `python3 -m py_compile scripts/evaluate_stage_a_target_handoff.py src/tase_repro/stage_a_target_handoff.py`
  - `scripts/evaluate_stage_a_target_handoff.py --orientation-kp 0.0 --paper-time-scale 0.01 --force-gain 1e-4`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  The slowed low-gain diagnostic handoff reports `4 / 4` E1-E4 passes from
  the selected target. All rows keep target contact, satisfy force/x-y/
  diagnostic-orientation gates, and avoid qdot saturation.
- Limit:
  This is direct-target handoff evidence only. It does not implement a Stage A
  path to the selected target and must not be used as paper-equivalent or
  hardware evidence.
- Validation:
  Full tests passed with `96 passed in 2.43s`. `git diff --check` passed.
- Next step:
  Implement a qdot-aware Stage A path to the selected diagnostic terminal
  target, or keep v60 labeled as direct-target handoff evidence only.

## 2026-05-24 v61 Contact Path To Diagnostic Target

### Offline quasi-static Stage A path audit

- Branch:
  `exp/tase-ur10e-v61-contact-path-to-diagnostic-target`
- Code commit:
  `878bb1649f876344f703a3a4d8156ece32847c12`
- Run:
  `runs/stage_a_contact_path_audit/20260524T151201`
- Report:
  `reports/stage_a_contact_path_audit_report.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_stage_a_contact_path.py`
  - `python3 -m py_compile src/tase_repro/stage_a_contact_path.py scripts/audit_stage_a_contact_path.py`
  - `scripts/audit_stage_a_contact_path.py`
- Result:
  The audit finds an offline 128-knot quasi-static contact path from the
  ordinary initial q to the selected diagnostic target. The path gate and
  terminal diagnostic gate pass. Target contact is present throughout, max
  force error is `0.005097546556703136 N`, and the minimum duration for the
  `0.15 rad/s` qdot budget is `14.332635022800167 s`.
- Limit:
  This is offline path evidence only. It does not prove an online Stage A
  controller can track the path, does not prove strict trajectory feasibility,
  and does not authorize hardware use. The force-normal orientation error is
  not under the terminal diagnostic threshold at every intermediate knot.
- Validation:
  Focused tests passed with `4 passed in 0.11s`. Full tests passed with
  `100 passed in 2.55s`; `git diff --check` passed.
- Next step:
  Track the v61 offline path with an online qdot-aware Stage A controller, then
  connect it to the v60 slowed handoff under one explicit timing and acceptance
  policy.

## 2026-05-24 v62 Contact Path Tracking

### Qdot-limited tracking of the v61 Stage A path

- Branch:
  `exp/tase-ur10e-v62-contact-path-tracking`
- Code commit:
  `6edddf4a05fae2671ee91f62bc653ec11d2f6058`
- Run:
  `runs/stage_a_contact_path_tracking/20260524T152346`
- Report:
  `reports/stage_a_contact_path_tracking_report.md`
- Commands run:
  - `scripts/run_tests.sh tests/test_stage_a_contact_path_tracking.py tests/test_stage_a_contact_path.py`
  - `python3 -m py_compile src/tase_repro/stage_a_contact_path_tracking.py scripts/track_stage_a_contact_path.py`
  - `scripts/track_stage_a_contact_path.py`
- Result:
  The qdot-limited joint-path tracker follows the v61 path over `15.0 s`. The
  tracking gate and terminal diagnostic gate pass. Max qdot is
  `0.14332635022814824 rad/s`, qdot saturation is `0.0`, final tracking error
  is `0.0`, target contact is present throughout, and max force error is
  `0.13962429878283 N`.
- Limit:
  This is a Stage A path tracking prototype only. It does not connect to the
  v60 Stage B handoff, does not prove force-feedback recovery, does not prove
  strict paper-equivalent feasibility, and does not authorize hardware use.
- Validation:
  Focused tests passed with `8 passed in 0.05s`. Full tests passed with
  `104 passed in 2.39s`; `git diff --check` passed.
- Next step:
  Run a stitched Stage A tracker plus v60 handoff simulation under one explicit
  timing and acceptance policy.

## 2026-05-24 v63 Stitched Stage A Handoff

### Diagnostic staged simulation with Stage A tracker and Stage B handoff

- Branch:
  `exp/tase-ur10e-v63-stitched-stage-a-handoff`
- Code commit:
  `748c4d46730d6f7044c8056fb6babc6c0804f1d2`
- Run:
  `runs/stitched_stage_a_handoff_eval/20260524T152807`
- Report:
  `reports/stitched_stage_a_handoff_report.md`
- Commands run:
  - `python3 -m py_compile scripts/evaluate_stitched_stage_a_handoff.py`
  - `scripts/evaluate_stitched_stage_a_handoff.py`
- Result:
  The stitched gate passes. Stage A tracking passes, and Stage B reports `4 / 4`
  E1-E4 handoff passes. Stage A max qdot is `0.14332635022814824 rad/s`; Stage A
  qdot saturation is `0.0`. All Stage B rows keep target contact, stay under the
  diagnostic orientation threshold, and have qdot saturation `0.0`.
- Limit:
  This is nominal diagnostic-label simulation evidence only. It is not strict
  paper-equivalent feasibility, a perturbation robustness claim, or hardware
  readiness.
- Validation:
  Full tests passed with `104 passed in 2.43s`; `git diff --check` passed.
- Next step:
  Run a sensitivity audit around the v63 stitched policy.

## 2026-05-24 v64 Stitched Handoff Sensitivity Audit

### Sensitivity boundary around the v63 diagnostic stitched policy

- Branch:
  `exp/tase-ur10e-v64-stitched-sensitivity-audit`
- Code commit:
  `1e15d9828145cc30b93c274d77eb99d2206a670f`
- Run:
  `runs/stitched_stage_a_handoff_sensitivity/20260524T161111`
- Report:
  `reports/stitched_stage_a_handoff_sensitivity_report.md`
- Commands run:
  - `python3 -m py_compile scripts/evaluate_stitched_stage_a_handoff.py scripts/audit_stitched_stage_a_handoff_sensitivity.py src/tase_repro/stitched_sensitivity.py`
  - `scripts/run_tests.sh tests/test_stitched_sensitivity.py tests/test_stage_a_contact_path_tracking.py tests/test_stage_a_target_handoff.py`
  - `scripts/run_tests.sh`
  - `scripts/audit_stitched_stage_a_handoff_sensitivity.py`
  - `git diff --check`
- Result:
  The sensitivity matrix passes `4 / 9` stitched cases. Passing cases are
  nominal, `stage_a_16s`, `force_gain_5e-5`, and `force_gain_2e-4`. Failing
  cases are `base_z_minus_1mm`, `base_z_plus_1mm`, `stage_a_14s`,
  `qdot_limit_0p12`, and `paper_time_scale_0p02`.
- Limit:
  This is diagnostic-label simulation sensitivity evidence only. It is not
  strict paper-equivalent feasibility, a robustness proof, or hardware
  readiness.
- Validation:
  Focused tests passed with `10 passed in 0.20s`. Full tests passed with
  `107 passed in 2.50s`; `git diff --check` passed before the formal run.
- Next step:
  Test whether perturbation-aware Stage A path reoptimization or margin-aware
  timing can recover the v64 base-z/contact and qdot failures.

## 2026-05-24 v65 Stitched Timing Margin Audit

### Margin-aware recovery of qdot/timing sensitivity cases

- Branch:
  `exp/tase-ur10e-v65-stitched-timing-margin`
- Code commit:
  `c071469132a2d39336f9e8727f51fed88d5334a1`
- Run:
  `runs/stitched_stage_a_handoff_timing_margin/20260524T162005`
- Report:
  `reports/stitched_stage_a_handoff_timing_margin_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_stitched_stage_a_handoff_sensitivity.py scripts/evaluate_stitched_stage_a_handoff.py src/tase_repro/stitched_sensitivity.py`
  - `scripts/run_tests.sh tests/test_stitched_sensitivity.py`
  - `scripts/run_tests.sh`
  - `scripts/audit_stitched_stage_a_handoff_sensitivity.py --case-set timing-margin`
  - `git diff --check`
- Result:
  The timing-margin case set passes `4 / 7` stitched cases. Passing recovery
  cases are `stage_a_14p5_recovery`, `qdot012_stage_a_18p0_recovery`, and
  `paper_time_scale_0p012_recovery`, plus nominal. Nearby reference-fail cases
  at `14.0 s`, `0.12 rad/s` with `17.5 s`, and `paper_time_scale = 0.0125`
  remain failing.
- Limit:
  This is diagnostic-label timing-margin evidence only. It does not recover
  the 1 mm base-z/contact perturbation failures and is not a strict
  paper-equivalent, robustness, or hardware-readiness claim.
- Validation:
  Focused tests passed with `3 passed in 0.00s`. Full tests passed with
  `107 passed in 2.43s`; `git diff --check` passed before the formal run.
- Next step:
  Test perturbation-aware Stage A path reoptimization for `base_z_minus_1mm`
  and `base_z_plus_1mm`.

## 2026-05-24 v66 Stage A Base-Z Recovery Audit

### Perturbation-aware endpoint/path recovery for base-z cases

- Branch:
  `exp/tase-ur10e-v66-base-z-path-recovery`
- Run:
  `runs/stage_a_base_z_recovery/20260524T163746`
- Report:
  `reports/stage_a_base_z_recovery_report.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/base_z_recovery.py scripts/audit_stage_a_base_z_recovery.py scripts/audit_stage_a_contact_path.py`
  - `scripts/run_tests.sh tests/test_stage_a_contact_path.py tests/test_base_z_recovery.py`
  - `scripts/audit_stage_a_base_z_recovery.py`
- Result:
  The base-z recovery case set passes `1 / 3` cases. The recovered case is
  `base_z_minus_1mm_stage_a_16s_recovery`, which uses a rebalanced start,
  perturbed terminal target, reoptimized 128-knot path, and `16.0 s` Stage A
  duration. The exact `15.0 s` `base_z_minus_1mm` reference remains failing
  because the path requires `15.652271522331025 s` at `0.15 rad/s`.
  `base_z_plus_1mm` remains unresolved with no passing start plus terminal
  target pair under this diagnostic search.
- Limit:
  This is diagnostic-label simulation recovery evidence only. It is not a
  strict paper-equivalent claim, robustness proof, contact-model calibration,
  or hardware readiness.
- Validation:
  Focused tests passed with `7 passed in 0.05s`. Full tests passed with
  `110 passed in 2.40s`; `git diff --check` passed.
- Next step:
  Investigate the unresolved `+1 mm` base-z/contact side and the exact
  `15.0 s` `-1 mm` boundary.

## 2026-05-24 v67 Stage A Base-Z Bracket Audit

### Compact bracket around positive-side base-z failure

- Branch:
  `exp/tase-ur10e-v67-base-z-bracket`
- Run:
  `runs/stage_a_base_z_bracket/20260524T165411`
- Report:
  `reports/stage_a_base_z_bracket_report.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/setup_terminal_ik.py src/tase_repro/base_z_recovery.py scripts/audit_stage_a_base_z_bracket.py`
  - `scripts/run_tests.sh tests/test_setup_terminal_ik.py tests/test_base_z_recovery.py`
  - `scripts/audit_stage_a_base_z_bracket.py`
- Result:
  The compact bracket evaluates `13` base-z deltas and two Stage A durations.
  Nominal, `-0.25 mm`, and `-0.5 mm` recover at both `15.0 s` and `16.0 s`;
  `-1.0 mm` recovers only at `16.0 s`; `-0.75 mm` has start and terminal
  feasibility but fails the path geometry gate. No positive delta from
  `+0.05 mm` through `+1.0 mm` has both start and terminal feasibility.
- Limit:
  This is diagnostic-label simulation bracket evidence only. It is not a
  strict paper-equivalent claim, robustness proof, contact-model calibration,
  or hardware readiness.
- Validation:
  Focused tests passed with `8 passed in 0.13s`. Full tests passed with
  `113 passed in 2.48s`; `git diff --check` passed.
- Next step:
  Investigate the positive-side contact-model/start-contact definition that
  fails already at `+0.05 mm`.

## 2026-05-24 v68 Positive Base-Z Start Contact Audit

### Separate positive-side start contact from terminal orientation

- Branch:
  `exp/tase-ur10e-v68-positive-start-contact`
- Run:
  `runs/positive_base_z_start_contact/20260524T170350`
- Report:
  `reports/positive_base_z_start_contact_report.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/base_z_recovery.py scripts/audit_positive_base_z_start_contact.py`
  - `scripts/run_tests.sh tests/test_base_z_recovery.py`
  - `scripts/audit_positive_base_z_start_contact.py`
- Result:
  The positive base-z start-contact audit evaluates `8` positive deltas from
  `+0.05 mm` through `+1.0 mm`. With deterministic single-joint, paired-joint,
  and random seed sweeps, start contact passes `8 / 8` cases. The terminal
  diagnostic gate passes `0 / 8`; every positive terminal row still fails the
  orientation gate, with best orientation error rising from
  `0.0838175590896232 rad` at `+0.05 mm` to `0.11948560786548146 rad` at
  `+1.0 mm`.
- Limit:
  This is diagnostic-label simulation start-contact evidence only. It is not a
  strict paper-equivalent claim, terminal recovery, path or stitched recovery,
  robustness proof, contact-model calibration, or hardware readiness.
- Validation:
  Focused base-z tests passed with `5 passed in 0.00s`. Full tests passed with
  `114 passed in 2.47s`; `git diff --check` passed.
- Next step:
  Investigate the positive-side terminal orientation gate/model convention.

## 2026-05-24 v69 Positive Terminal Orientation Audit

### Separate orientation margin from yaw and contact-model convention

- Branch:
  `exp/tase-ur10e-v69-positive-terminal-orientation`
- Run:
  `runs/positive_terminal_orientation/20260524T171705`
- Report:
  `reports/positive_terminal_orientation_report.md`
- Commands run:
  - `python3 -m py_compile src/tase_repro/base_z_recovery.py scripts/audit_positive_terminal_orientation.py`
  - `scripts/run_tests.sh tests/test_base_z_recovery.py`
  - `scripts/audit_positive_terminal_orientation.py`
- Result:
  The current contact-point model passes force/x-y/contact for all `8 / 8`
  positive terminal cases from `+0.05 mm` through `+1.0 mm`, but diagnostic
  orientation passes `0 / 8`. The full-rotation error and force-normal-only
  error differ by at most `4.884981308350689e-15 rad`, so yaw handling is not
  the limiting convention. Covering all positive force/x-y/contact terminal
  cases in the current model requires about `0.11948560786548146 rad` of
  orientation margin. The legacy sphere-center comparison passes `6 / 8`
  through `+0.5 mm`, but remains a known flawed geometry comparison.
- Limit:
  This is terminal-state diagnostic simulation evidence only. It is not a
  strict paper-equivalent claim, path or stitched recovery, robustness proof,
  contact-model calibration, or hardware readiness.
- Validation:
  Focused base-z tests passed with `6 passed in 0.01s`. Full tests passed with
  `115 passed in 2.45s`; `git diff --check` passed.
- Next step:
  Test positive-side path/stitched recovery only under an explicit justified
  `0.12 rad` terminal orientation envelope, or revisit the contact-point /
  terminal target definition if that envelope is unacceptable.

## 2026-05-24 v70 Positive Relaxed Orientation Recovery Audit

### Test positive-side path and stitched recovery under a 0.12 rad terminal gate

- Branch:
  `exp/tase-ur10e-v70-positive-relaxed-orientation-recovery`
- Run:
  `runs/positive_relaxed_orientation_recovery/20260524T172909`
- Report:
  `reports/positive_relaxed_orientation_recovery_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_relaxed_orientation_recovery.py`
  - `scripts/audit_positive_relaxed_orientation_recovery.py`
- Result:
  The run-local relaxed target config sets
  `max_terminal_orientation_error_rad = 0.12` without modifying the canonical
  v58 target config. Positive start, terminal, and path geometry pass `8 / 8`
  through `+1.0 mm`; max positive terminal/path delta is `+1.0 mm`. Stitched
  recovery remains `0`: every tested row has Stage A passing but Stage B
  handoff `3 / 4`, with `e2-figure-eight` failing on qdot saturation and tail
  max qdot utilization.
- Limit:
  This is diagnostic-label simulation evidence only. It is not a strict
  paper-equivalent claim, robustness proof, contact-model calibration, or
  hardware readiness. The relaxed `0.12 rad` config is a run artifact, not a
  canonical config change.
- Validation:
  `python3 -m py_compile scripts/audit_positive_relaxed_orientation_recovery.py scripts/audit_stage_a_contact_path.py scripts/track_stage_a_contact_path.py`
  passed. Full tests passed with `115 passed in 2.44s`; `git diff --check`
  passed.
- Next step:
  Combine the v70 relaxed terminal/path setup with a Stage B E2 timing or qdot
  margin audit.

## 2026-05-24 v71 Positive Stage B E2 Margin Audit

### Isolate E2 timing and qdot margin after v70 positive path recovery

- Branch:
  `exp/tase-ur10e-v71-stage-b-e2-margin`
- Run:
  `runs/positive_stage_b_e2_margin/20260524T192129`
- Report:
  `reports/positive_stage_b_e2_margin_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_stage_b_e2_margin.py`
  - `scripts/audit_positive_stage_b_e2_margin.py`
- Result:
  The E2-only timing sweep reuses the v70 run-local `0.12 rad` relaxed target
  config and per-delta path CSV artifacts. At original `paper_time_scale =
  0.01`, E2 passes `0 / 8` positive deltas. At `0.0075`, E2 passes `7 / 8`
  through `+0.75 mm`; at `0.005` and `0.0025`, E2 passes `8 / 8` through
  `+1.0 mm`. The qdot-limit-only probe on `+1.0 mm` at original `0.01` timing
  still fails up to `0.25 rad/s` because max orientation error remains just
  above `0.12 rad`.
- Limit:
  This is diagnostic-label E2 Stage B margin evidence only. It is not a full
  E1-E4 stitched recovery claim, strict paper-equivalent claim, robustness
  proof, contact-model calibration, or hardware readiness. The relaxed
  `0.12 rad` config remains a run artifact, not a canonical config change.
- Validation:
  `python3 -m py_compile scripts/audit_positive_stage_b_e2_margin.py`
  passed. Full tests passed with `115 passed in 2.45s`; `git diff --check`
  passed.
- Next step:
  Run the full positive E1-E4 stitched matrix with the v70 relaxed
  terminal/path setup and `paper_time_scale = 0.005`.

## 2026-05-24 v72 Positive Full Stitched Recovery Audit

### Run the full positive E1-E4 stitched matrix at the E2-safe timing

- Branch:
  `exp/tase-ur10e-v72-positive-full-stitched`
- Run:
  `runs/positive_full_stitched_recovery/20260524T192854`
- Report:
  `reports/positive_full_stitched_recovery_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_full_stitched_recovery.py`
  - `scripts/audit_positive_full_stitched_recovery.py`
- Result:
  The audit reuses the v70 run-local `0.12 rad` relaxed target config and
  per-delta path CSV artifacts, then evaluates all E1-E4 trajectories at
  `paper_time_scale = 0.005`. Positive stitched recovery passes `8 / 8`
  through `+1.0 mm`; every row has Stage A passing and Stage B handoff
  `4 / 4`. Max Stage B qdot saturation fraction is `0.006`, max Stage B tail
  qdot utilization is `0.3579877267896789`, and max Stage B orientation error
  is `0.1199788204275829 rad`.
- Limit:
  This is diagnostic-label simulation evidence only. It depends on the
  run-local `0.12 rad` relaxed orientation gate and slowed
  `paper_time_scale = 0.005`; it is not strict paper-equivalent, robust,
  contact-model calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_positive_full_stitched_recovery.py`
  passed. Full tests passed with `115 passed in 2.50s`; `git diff --check`
  passed.
- Next step:
  Stress-test the v72 recovered positive stitched policy under a compact
  sensitivity matrix.

## 2026-05-24 v73 Positive Stitched Sensitivity Audit

### Bound the recovered positive stitched diagnostic policy

- Branch:
  `exp/tase-ur10e-v73-positive-stitched-sensitivity`
- Run:
  `runs/positive_stitched_sensitivity/20260524T193845`
- Report:
  `reports/positive_stitched_sensitivity_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_stitched_sensitivity.py`
  - `scripts/audit_positive_stitched_sensitivity.py`
- Result:
  The audit reuses the v70 run-local relaxed terminal/path setup and tests five
  compact sensitivity scenarios across the same eight positive deltas and all
  E1-E4 Stage B trajectories. The matrix passes `37 / 40` stitched cells.
  `nominal_v72` and `stage_a_14p5s` pass `8 / 8`. `qdot012_stage_a18s` passes
  `7 / 8` and fails `+0.2 mm` on Stage A `final_tracking_error_norm_rad`, while
  Stage B remains `4 / 4`. `paper_time_scale_0p0075` passes `7 / 8` and fails
  `+1.0 mm` on E2 qdot saturation, tail qdot utilization, and orientation.
  `orientation_gate_0p119` passes `7 / 8` and fails `+1.0 mm` on Stage A
  terminal orientation plus all Stage B orientation rows.
- Limit:
  This is diagnostic-label simulation sensitivity evidence only. It bounds the
  v72 recovery and is not a robustness proof, strict paper-equivalent claim,
  contact-model calibration, or hardware readiness. The tightened orientation
  config is run-local only.
- Validation:
  `python3 -m py_compile scripts/audit_positive_stitched_sensitivity.py`
  passed. Full tests passed with `115 passed in 2.47s`; `git diff --check`
  passed.
- Next step:
  Isolate the `qdot012_stage_a18s` `+0.2 mm` Stage A final-tracking boundary
  with a small Stage A duration/path-retiming margin audit.
