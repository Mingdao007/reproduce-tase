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

## 2026-05-24 v74 Qdot012 Stage A Margin Audit

### Isolate the positive qdot012 duration boundary

- Branch:
  `exp/tase-ur10e-v74-qdot012-stage-a-margin`
- Run:
  `runs/qdot012_stage_a_margin/20260524T194817`
- Report:
  `reports/qdot012_stage_a_margin_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_qdot012_stage_a_margin.py`
  - `scripts/audit_qdot012_stage_a_margin.py`
- Result:
  The audit isolates the v73 `qdot012_stage_a18s` `+0.2 mm` failing cell while
  holding the v70 relaxed target/path setup, `qdot_limit_rad_s = 0.12`,
  `paper_time_scale = 0.005`, and `max_orientation_error_rad = 0.12` fixed.
  Stage B handoff passes `4 / 4` for all seven tested durations. Stage A final
  tracking fails through `18.03 s`; `18.035 s`, `18.04 s`, and `18.05 s` pass.
  The first passing case has max Stage A qdot `0.1199690367457867 rad/s`.
- Limit:
  This is diagnostic-label Stage A duration margin evidence only. It does not
  recover the v73 faster-timing or tighter-orientation `+1.0 mm` sensitivity
  failures and is not strict paper-equivalent, robust, calibrated, or
  hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_qdot012_stage_a_margin.py scripts/audit_positive_stitched_sensitivity.py`
  passed. Full tests passed with `115 passed in 2.55s`; `git diff --check`
  passed.
- Next step:
  Decide whether to fold the `18.035 s` qdot012 duration margin into a compact
  positive stitched recovery matrix or move to the harder `+1.0 mm`
  timing/orientation sensitivity limits.

## 2026-05-24 v75 Qdot012 Positive Stitched Matrix

### Fold the qdot012 Stage A duration margin into all positive deltas

- Branch:
  `exp/tase-ur10e-v75-qdot012-positive-matrix`
- Run:
  `runs/positive_full_stitched_recovery/20260524T195501`
- Report:
  `reports/qdot012_positive_stitched_matrix_report.md`
- Commands run:
  - `scripts/audit_positive_full_stitched_recovery.py --stage-a-duration-s 18.035 --qdot-limit-rad-s 0.12 --paper-time-scale 0.005 --max-orientation-error-rad 0.12`
- Result:
  The audit applies the v74 `18.035 s` Stage A duration margin to the full
  positive matrix with `qdot_limit_rad_s = 0.12`, reusing the v70 run-local
  relaxed terminal/path setup and `paper_time_scale = 0.005`. Stitched recovery
  passes `8 / 8` through `+1.0 mm`; every row has Stage A passing and Stage B
  handoff `4 / 4`. Max Stage B qdot saturation fraction is `0.001`, max Stage B
  tail qdot utilization is `0.4474846584870986`, and max Stage B orientation
  error is `0.11997895388586574 rad`.
- Limit:
  This is diagnostic-label simulation evidence only. It closes the qdot012
  branch of the v73 compact sensitivity failure, but it does not recover the
  faster-timing or tighter-orientation `+1.0 mm` sensitivity failures and is
  not strict paper-equivalent, robust, calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_positive_full_stitched_recovery.py scripts/audit_qdot012_stage_a_margin.py scripts/audit_positive_stitched_sensitivity.py`
  passed. Full tests passed with `115 passed in 2.46s`; `git diff --check`
  passed.
- Next step:
  Move to the harder `+1.0 mm` faster-timing and tighter-orientation
  sensitivity limits unless the qdot012 branch is intentionally stopped at the
  recovered diagnostic matrix.

## 2026-05-24 v76 Positive Timing Boundary Audit

### Isolate the `+1.0 mm` faster-timing boundary

- Branch:
  `exp/tase-ur10e-v76-positive-timing-boundary`
- Run:
  `runs/positive_timing_boundary/20260524T200236`
- Report:
  `reports/positive_timing_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_timing_boundary.py`
  - `scripts/audit_positive_timing_boundary.py`
- Result:
  The audit isolates the v73 `paper_time_scale_0p0075` `+1.0 mm` failing cell
  while holding the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `qdot_limit_rad_s = 0.15`, and `max_orientation_error_rad = 0.12`
  fixed. Stage A passes all nine timing cases. Stitched recovery passes at
  `paper_time_scale = 0.005` and `0.0052`, then first fails at `0.0054` on E2
  `max_orientation_error_rad = 0.12001811086329595 rad`. Larger timing scales
  keep the same E2 orientation failure, and qdot saturation becomes severe at
  `0.007` and `0.0075`.
- Limit:
  This is diagnostic-label timing-boundary evidence only. It bounds, but does
  not recover, the faster-timing `+1.0 mm` sensitivity failure under the same
  `0.12 rad` diagnostic gate. It does not address the separate
  `orientation_gate_0p119` `+1.0 mm` failure and is not strict
  paper-equivalent, robust, calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_positive_timing_boundary.py` passed.
  Full tests passed with `115 passed in 2.64s`; `git diff --check` passed.
  The run artifact is lightweight: `67` files, `952K`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `81ab8d6d04342e4be8dc78cabe29dc7c45c6967b`.
- Next step:
  Move to the remaining `+1.0 mm` tightened-orientation sensitivity limit, or
  test a targeted Stage B orientation-margin/control change for the v76 timing
  boundary without relaxing the diagnostic gate.

## 2026-05-24 v77 Positive Orientation Gate Boundary Audit

### Isolate the `+1.0 mm` tightened-orientation boundary

- Branch:
  `exp/tase-ur10e-v77-positive-orientation-gate-boundary`
- Run:
  `runs/positive_orientation_gate_boundary/20260524T221842`
- Report:
  `reports/positive_orientation_gate_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_orientation_gate_boundary.py`
  - `scripts/audit_positive_orientation_gate_boundary.py`
- Result:
  The audit isolates the v73 `orientation_gate_0p119` `+1.0 mm` failing cell
  while holding the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `paper_time_scale = 0.005`, and `qdot_limit_rad_s = 0.15` fixed. The
  script writes a run-local Stage A target config for each gate and passes the
  same gate to Stage B. Stage A fails at `0.119` and `0.11925`, then first
  passes at `0.1195 rad`. Full stitched recovery still fails through
  `0.11997`, then first passes at `0.11998` because E2 reaches
  `0.1199788204275829 rad`.
- Limit:
  This is diagnostic-label orientation-boundary evidence only. It localizes
  the gate margin but does not change the terminal/contact model, prove
  robustness, establish strict paper-equivalent feasibility, calibrate contact,
  or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_positive_orientation_gate_boundary.py`
  passed. Full tests passed with `115 passed in 2.55s`; `git diff --check`
  passed. The run artifact is lightweight: `76` files, `1008K`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `66715852488151da19379a5b4a9373dd44c0c407`.
- Next step:
  Test a targeted Stage B orientation-margin/control change or revisit the
  terminal/contact model before claiming anything stronger than diagnostic
  recovery.

## 2026-05-24 v78 Stage B Orientation Kp Probe

### Test the existing Stage B orientation-feedback hook at the tightened gate

- Branch:
  `exp/tase-ur10e-v78-stage-b-orientation-kp-probe`
- Run:
  `runs/stage_b_orientation_kp_probe/20260524T222953`
- Report:
  `reports/stage_b_orientation_kp_probe_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_stage_b_orientation_kp_probe.py`
  - `scripts/audit_stage_b_orientation_kp_probe.py`
- Result:
  The audit isolates the v77 tightened-orientation `+1.0 mm` E2 row at a
  `0.11995 rad` Stage A/Stage B orientation gate while holding the v70 relaxed
  target/path setup, `stage_a_duration_s = 15.0`, and
  `paper_time_scale = 0.005` fixed. It sweeps qdot limits
  `[0.15, 0.16, 0.18, 0.2, 0.25] rad/s` and `orientation_kp` values
  `[0, 0.001, 0.002, 0.003, 0.005, 0.01]` for E2 only. Stage A passes every
  case, but stitched recovery passes `0 / 30`. `13 / 30` rows get E2
  orientation under `0.11995 rad`, but every orientation-correcting row fails
  qdot saturation and/or tail qdot utilization.
- Limit:
  This is diagnostic-label E2 Stage B probe evidence only. It does not change
  canonical controller defaults, does not prove full E1-E4 stitched recovery,
  and is not strict paper-equivalent, robust, calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_stage_b_orientation_kp_probe.py`
  passed. Full tests passed with `115 passed in 2.54s`; `git diff --check`
  passed. The run artifact is lightweight: `215` files, `1.6M`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `2b56ab4fd9b828fec54870afe1ae0b0792bec89a`.
- Next step:
  Move away from single-gain Stage B orientation feedback as the direct fix.
  Revisit the terminal/contact model or test a redesigned Stage B
  priority/posture formulation before claiming anything stronger than
  diagnostic recovery.

## 2026-05-24 v79 Stage B Priority Recovery

### Recover the localized tightened-gate row with planar-primary priority

- Branch:
  `exp/tase-ur10e-v79-stage-b-priority-posture-probe`
- Run:
  `runs/stage_b_priority_recovery/20260524T224404`
- Report:
  `reports/stage_b_priority_recovery_report.md`
- Commands run:
  - `python3 -m py_compile scripts/evaluate_stitched_stage_a_handoff.py scripts/audit_stage_b_priority_recovery.py`
  - `scripts/audit_stage_b_priority_recovery.py`
- Result:
  The audit holds the v70 relaxed target/path setup, the `+1.0 mm` positive
  cell, `stage_a_duration_s = 15.0`, `paper_time_scale = 0.005`,
  `qdot_limit_rad_s = 0.15`, and a `0.11995 rad` Stage A/Stage B orientation
  gate fixed while comparing seven Stage B priority scenarios over E1-E4.
  Stage A passes every scenario. Linear-primary controls still fail on E2:
  no orientation feedback fails orientation, `orientation_kp = 0.003` fails
  qdot, and handoff-posture regularization preserves qdot by giving up the
  orientation correction. Planar-primary controls expose the normal-force
  tradeoff; normal-axis weight `10` fails E2 force, while normal-axis weight
  `100` returns to the E2 orientation/qdot boundary. The two normal-axis
  weight `30` scenarios pass stitched recovery `4 / 4` at
  `orientation_kp = 0.001` and `0.002`.
- Limit:
  This is a localized diagnostic Stage B priority-formulation recovery only.
  It does not prove the full positive-delta matrix, robustness, strict
  paper-equivalent feasibility, contact-model calibration, or hardware
  readiness.
- Validation:
  `python3 -m py_compile scripts/evaluate_stitched_stage_a_handoff.py scripts/audit_stage_b_priority_recovery.py`
  passed. Full tests passed with `115 passed in 2.54s`; `git diff --check`
  passed. The run artifact is lightweight: `54` files, `788K`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `9bfdb9b6dbf0c76760ca41b4a918d790ae61dc08`.
- Next step:
  Run the recovered planar-primary formulation across the full positive-delta
  matrix, or stress it against faster timing/tighter gates, before claiming
  anything stronger than localized diagnostic recovery.

## 2026-05-24 v80 Positive Planar-Priority Matrix

### Carry the recovered planar-primary formulation across all positive deltas

- Branch:
  `exp/tase-ur10e-v80-planar-priority-positive-matrix`
- Run:
  `runs/positive_planar_priority_matrix/20260524T225138`
- Report:
  `reports/positive_planar_priority_matrix_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_planar_priority_matrix.py`
  - `scripts/audit_positive_planar_priority_matrix.py`
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `paper_time_scale = 0.005`, `qdot_limit_rad_s = 0.15`, and a
  `0.11995 rad` Stage A/Stage B orientation gate fixed, then evaluates both
  v79 passing planar-primary candidates across all eight positive base-z
  deltas and all E1-E4 Stage B trajectories. Both scenarios pass all eight
  positive deltas through `+1.0 mm`; total stitched pass count is `16 / 16`.
  The `orientation_kp = 0.001` scenario has max Stage B orientation
  `0.11973133163816624 rad`, max qdot saturation `0.001`, and max tail force
  error `0.1223546677432889 N`. The `orientation_kp = 0.002` scenario has max
  Stage B orientation `0.11961552028823065 rad`, max qdot saturation `0.001`,
  and max tail force error `0.1902561439715911 N`.
- Limit:
  This is diagnostic-label full positive-delta matrix evidence for the
  planar-primary Stage B priority formulation. It is not a canonical config
  change, faster-timing recovery, qdot012 tightened-gate recovery, strict
  paper-equivalent feasibility, robustness proof, contact-model calibration,
  or hardware readiness.
- Validation:
  `python3 -m py_compile scripts/audit_positive_planar_priority_matrix.py`
  passed. Full tests passed with `115 passed in 2.55s`; `git diff --check`
  passed. The run artifact is lightweight: `117` files, `1.8M`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `8e7832eedb85cc3642a3cb89047325969e1cb3d0`.
- Next step:
  Stress the recovered planar-primary formulation against the v73/v76
  faster-timing boundary and the tighter `0.119 rad` orientation gate before
  claiming anything stronger than diagnostic recovery.

## 2026-05-24 v81 Planar-Priority Stress

### Stress the recovered planar-primary formulation against timing and gate limits

- Branch:
  `exp/tase-ur10e-v81-planar-priority-stress`
- Run:
  `runs/planar_priority_stress/20260524T230109`
- Report:
  `reports/planar_priority_stress_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_planar_priority_stress.py`
  - `scripts/audit_planar_priority_stress.py`
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, and `qdot_limit_rad_s = 0.15` fixed while testing the two v80
  planar-primary candidates against focused `+1.0 mm` timing/gate sweeps and
  full positive-delta stress rows. Total stitched pass count is `35 / 66`.
  Both candidates pass the focused `+1.0 mm` timing sweep through
  `paper_time_scale = 0.0065` and first fail at `0.007`. The focused
  orientation-gate sweep first passes at `0.1198 rad` for
  `planar_normal30_kp0p001` and `0.1197 rad` for
  `planar_normal30_kp0p002`. Full `paper_time_scale = 0.0075` stress fails
  `0 / 16` stitched cells across both candidates. The `0.119 rad` gate stress
  passes through `+0.75 mm` but still fails `+1.0 mm` for both candidates.
- Limit:
  This is diagnostic-label stress evidence only. It improves the focused
  boundary margins but does not recover the full faster-timing stress, does
  not recover the `+1.0 mm`, `0.119 rad` gate, and is not strict
  paper-equivalent, robust, contact-calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_planar_priority_stress.py` passed. Full
  tests passed with `115 passed in 2.60s`; `git diff --check` passed. The run
  artifact is lightweight: `474` files, `7.2M`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `6207d72c588802f2181234037e5c40301376d43a`.
- Next step:
  Choose the next diagnostic branch from the v81 failure modes: redesign the
  faster-timing E2 qdot/tail-utilization behavior at `paper_time_scale =
  0.0075`, or revisit the terminal/contact model and orientation gate before
  trying to force the `+1.0 mm`, `0.119 rad` case through Stage B tuning.

## 2026-05-24 v82 Weighted Timing Recovery

### Recover the faster-timing face with weighted zero-angular priority

- Branch:
  `exp/tase-ur10e-v82-weighted-timing-recovery`
- Run:
  `runs/weighted_timing_recovery/20260524T231454`
- Report:
  `reports/weighted_timing_recovery_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_weighted_timing_recovery.py`
  - `scripts/audit_weighted_timing_recovery.py`
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, `qdot_limit_rad_s = 0.15`, and `orientation_gate = 0.11995 rad`
  fixed while comparing linear-primary, the two v80 planar-primary candidates,
  and weighted zero-angular-command priority on the full positive-delta
  `paper_time_scale = 0.0075` stress face. Linear-primary passes `7 / 8` and
  still fails `+1.0 mm`; both planar-primary candidates pass `0 / 8`; both
  weighted candidates pass `8 / 8` through `+1.0 mm`. The
  `weighted_kp0_normal1` focused `+1.0 mm` timing sweep passes all tested
  values from `paper_time_scale = 0.005` through `0.01`.
- Limit:
  This is diagnostic-label faster-timing recovery evidence under the
  `0.11995 rad` gate. It is not a canonical controller default, does not
  recover the `0.119 rad` gate, does not prove a full positive-delta
  `paper_time_scale = 0.01` matrix, and is not strict paper-equivalent,
  robust, contact-calibrated, or hardware-ready.
- Validation:
  `python3 -m py_compile scripts/audit_weighted_timing_recovery.py` passed.
  Full tests passed with `115 passed in 2.66s`; `git diff --check` passed. The
  run artifact is lightweight: `355` files, `5.4M`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `484490292ba2a4b612896ec4b38f3026fe605d51`.
- Next step:
  Stress the weighted zero-angular-command candidate against the `0.119 rad`
  orientation gate and decide whether a full positive-delta
  `paper_time_scale = 0.01` matrix is a meaningful diagnostic target before
  treating the faster-timing face as closed.

## 2026-05-24 v83 Weighted Gate/Time Matrix

### Close the full `0.01` timing matrix and bracket the tightened gate

- Branch:
  `exp/tase-ur10e-v83-weighted-gate-time-matrix`
- Run:
  `runs/weighted_gate_time_matrix/20260524T232637`
- Report:
  `reports/weighted_gate_time_matrix_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py`
  - `scripts/audit_weighted_gate_time_matrix.py`
- Result:
  The audit holds the v70 relaxed target/path setup, `stage_a_duration_s =
  15.0`, and `qdot_limit_rad_s = 0.15` fixed while testing the two v82
  weighted zero-angular-command candidates. Both weighted scenarios pass the
  full positive-delta `paper_time_scale = 0.01`, `orientation_gate = 0.11995`
  matrix `8 / 8` through `+1.0 mm`. At the tighter `0.119 rad` gate, both
  timings pass through `+0.75 mm` but fail `+1.0 mm`. The focused `+1.0 mm`
  gate boundary first passes at `0.11955 rad` for `paper_time_scale = 0.0075`
  and `0.1196 rad` for `paper_time_scale = 0.01`.
- Limit:
  This is diagnostic-label timing/gate matrix evidence only. It closes the
  full `paper_time_scale = 0.01` positive matrix under the `0.11995 rad` gate,
  but it does not recover the `+1.0 mm`, `0.119 rad` gate and is not a
  canonical controller default, strict paper-equivalent feasibility,
  robustness proof, contact-model calibration, or hardware readiness.
- Validation:
  `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py` passed.
  Full tests passed with `115 passed in 2.78s`; `git diff --check` passed. The
  run artifact is lightweight: `460` files, `7.0M`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `8c97fdafc5c0113a907c087c881e72f8fea4c1dd`.
- Next step:
  Treat the faster-timing face as recovered under the `0.11995 rad` gate. The
  remaining simulation blocker is the `+1.0 mm`, `0.119 rad` orientation-gate
  row, so revisit the terminal/contact orientation definition or model
  calibration before more Stage B qdot tuning.

## 2026-05-24 v84 Weighted Orientation Model Sensitivity

### Attribute the remaining `0.119 rad` miss before more qdot tuning

- Branch:
  `exp/tase-ur10e-v84-orientation-model-sensitivity`
- Run:
  `runs/weighted_orientation_model_sensitivity/20260524T233945`
- Report:
  `reports/weighted_orientation_model_sensitivity_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_weighted_orientation_model_sensitivity.py`
  - `python3 scripts/audit_weighted_orientation_model_sensitivity.py`
- Result:
  The audit reads the v83 weighted gate/time matrix and the v69 positive
  terminal orientation audit. The critical `0.119 rad` weighted rows exceed
  the gate by less than `0.00057 rad` (`0.033 deg`) and have `0.0` qdot
  saturation. The contact-point +1.0 mm terminal orientation is
  `0.11948560786548146 rad`; the legacy sphere-center +1.0 mm terminal
  orientation is `0.09525838838593075 rad`, so the geometry convention shifts
  the terminal orientation by `0.024227219479550713 rad`.
- Limit:
  This is diagnostic sensitivity evidence only. It does not recover the
  `+1.0 mm`, `0.119 rad` gate, calibrate the contact model, change controller
  defaults, prove robustness, prove strict paper-equivalent feasibility, or
  authorize hardware motion/configuration.
- Validation:
  - `python3 -m py_compile scripts/audit_weighted_orientation_model_sensitivity.py`
    passed.
  - `scripts/run_tests.sh`: `115 passed in 2.72s`.
  - `git diff --check` passed.
  - Current-script reproducibility check: rerunning the audit to
    `/tmp/reproduce-tase-v84-verify.S4rN7N` produced identical `metrics.yaml`
    and `metrics.json`; `summary.md` differed only by the run-root path.
  - Artifact audit: `4` files, `28K`, no `.npz/.npy/.mat/.tar/.gz/.zip`
    payloads under `runs/weighted_orientation_model_sensitivity/20260524T233945`.
  - Branch push was verified at
    `8289d252dbb8a3ea9d3c9744ff08eaeba5fe0ed1`.
- Next step:
  Tighten terminal/contact orientation definition, measured mounted-stack
  geometry, contact point convention, and plane/contact normal calibration
  before more Stage B qdot tuning for the `0.119 rad` row.

## 2026-05-24 v85 Contact Orientation Calibration Margin

### Quantify the physical/modeling correction for the remaining row

- Branch:
  `exp/tase-ur10e-v85-contact-orientation-calibration`
- Run:
  `runs/contact_orientation_calibration_margin/20260524T235723`
- Report:
  `reports/contact_orientation_calibration_margin_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_contact_orientation_calibration_margin.py`
  - `python3 scripts/audit_contact_orientation_calibration_margin.py`
  - `scripts/run_tests.sh`
- Result:
  The audit reads the v84 weighted orientation model sensitivity metrics, v83
  weighted gate/time matrix, v69 positive terminal orientation metrics, v77
  orientation-gate boundary metrics, and current contact/acceptance configs.
  The hardest remaining row is the `paper_time_scale = 0.01`,
  `0.119 rad` weighted `+1.0 mm` row. It needs
  `0.0005664520369604714 rad` (`0.03245531101442353 deg`) of
  normal-orientation margin to close the current gate, equivalent to
  `0.014963398168061883 mm` (`14.963398168061882 um`) under the v84 terminal
  slope proxy. Existing metrics show scoped recovery at `0.11955`, `0.1196`,
  and `0.11995 rad`, but v85 does not accept any of those as replacement gates
  without calibrated geometry/contact-normal evidence.
- Limit:
  This is a diagnostic calibration/definition margin audit only. It does not
  recover the `+1.0 mm`, `0.119 rad` gate, accept a relaxed gate, calibrate the
  contact model, change controller defaults, prove robustness, prove strict
  paper-equivalent feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_contact_orientation_calibration_margin.py`
  passed. Full tests passed with `115 passed in 2.69s`. The run artifact is
  lightweight: `4` files, `48K`, with no `.npz/.npy/.mat/.tar/.gz/.zip`
  payloads. `git diff --check` passed. Branch push was verified at
  `e9603612a47fed63e19d9aa0f90bd925d2015991`.
- Next step:
  Collect or define measured mounted-stack TCP/contact point, contact patch
  convention, plane normal in the robot base frame, force-source/frame
  reconciliation, and accepted orientation-gate semantics before more Stage B
  qdot tuning.

## 2026-05-25 v86 Measured Geometry Readiness

### Audit whether existing records support the v85 calibration margin

- Branch:
  `exp/tase-ur10e-v86-measured-geometry-readiness`
- Run:
  `runs/measured_geometry_readiness/20260525T000739`
- Report:
  `reports/measured_geometry_readiness_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_measured_geometry_readiness.py`
  - `python3 scripts/audit_measured_geometry_readiness.py`
- Result:
  The audit inspects current lab-vault hardware state, EOAT TCP notes, v13 EOAT
  verification metadata, the contact-point config/MJCF, and the v85 margin.
  Existing records do not support accepting the v85 `0.03246 deg` /
  `14.96 um` correction as calibrated evidence. The `85.0 mm` contact point is
  design metadata, the current UR TCP `[0, 0, 0.12254, 0, 0, 0]` is temporary
  and not contact-validated, the KSM contact patch convention is unverified,
  the plane normal is analytic simulation geometry, and direct TCP DAQ still
  disagrees with RTDE/PolyScope force values by about `32 N`.
- Limit:
  This is read-only local-record evidence only. It does not recover the
  `+1.0 mm`, `0.119 rad` row, accept a replacement gate, calibrate the contact
  model, prove robustness, prove strict paper-equivalent feasibility, or
  authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_measured_geometry_readiness.py` passed.
  Full tests passed with `115 passed in 2.64s`; `git diff --check` passed.
  The run artifact is lightweight: `4` files, `44K`, with no
  `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `70a1b35cf6436b284ed8bc8d1fcf936f9b0724a1`.
- Next step:
  Turn the v86 checklist into a read-only measurement/SOP for mounted-stack
  TCP/contact point, KSM contact patch convention, plane normal in the robot
  base frame, force-source/frame reconciliation, and accepted orientation-gate
  semantics.

## 2026-05-25 v87 Read-Only Calibration Measurement SOP

### Define the safe measurement gates before live bench evidence collection

- Branch:
  `exp/tase-ur10e-v87-readonly-measurement-sop`
- SOP:
  `reports/read_only_calibration_measurement_sop.md`
- Commands run:
  - no live hardware commands
- Result:
  The SOP defines the required artifacts, pass/fail gates, and abort
  conditions for mounted-stack TCP/contact point, KSM contact patch convention,
  plane normal in robot base frame, force-source/frame reconciliation, and
  orientation-gate semantics. It explicitly compares the required geometry and
  normal evidence to the v85 `14.963398168061882 um` and
  `0.03245531101442353 deg` margins.
- Limit:
  This is a planning/SOP artifact only. It was not executed, does not collect
  new measurements, and does not authorize robot motion, configuration writes,
  zeroing, force control, gate relaxation, calibrated contact-model claims, or
  hardware readiness.
- Validation:
  Full tests passed with `115 passed in 2.65s`; `git diff --check` passed. No
  live hardware commands were run. Branch push was verified at
  `e60a90cfb112e4f5962c67efc2abbbcc3db313d0`.
- Next step:
  Execute only safe read-only portions of the SOP after explicit user
  confirmation, or refine the SOP if any measurement path is ambiguous.

## 2026-05-25 v88 Read-Only Measurement Templates

### Make the v87 SOP executable as a non-executed scaffold

- Branch:
  `exp/tase-ur10e-v88-readonly-measurement-templates`
- Run:
  `runs/read_only_calibration_measurement/20260525T012234`
- Report:
  `reports/read_only_calibration_measurement_template_report.md`
- Commands run:
  - `python3 -m py_compile scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T012234`
- Result:
  Added a reusable template under
  `templates/read_only_calibration_measurement/`, a scaffold command, and a
  pytest that verifies generated runs keep live hardware access, robot motion,
  configuration writes, zeroing/biasing, force control, gate relaxation, and
  hardware-readiness flags false. The generated run is
  `scaffold_created_not_executed` and records git state.
- Limit:
  This is a template-only, non-executed run. It does not collect measurements,
  execute the SOP, calibrate the contact model, accept any replacement gate,
  prove robustness, prove strict paper-equivalent feasibility, or authorize
  hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold test passed with `1 passed in 0.19s`; full tests
  passed with `116 passed in 2.82s`; `git diff --check` passed before
  full-test validation. The generated run artifact has `12` files, `52K`, and
  no `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `67b486ef5b7b42c14ecf30e22dc1bb89014ec4c9`.
- Next step:
  Use the scaffold only for an explicitly approved read-only SOP step, or keep
  refining the worksheets if the live measurement path is still ambiguous.

## 2026-05-25 v89 Read-Only Run Audit

### Add an offline claim-boundary verifier for scaffolded measurement runs

- Branch:
  `exp/tase-ur10e-v89-readonly-run-audit`
- Run:
  `runs/read_only_calibration_measurement_run_audit/20260525T012835`
- Report:
  `reports/read_only_calibration_measurement_run_audit_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --run-id 20260525T012835`
- Result:
  Added `scripts/audit_read_only_calibration_measurement_run.py`, which checks
  required files, metrics YAML/JSON consistency, worksheet headers, non-executed
  status, false execution flags, false hardware/gate/calibration verdicts,
  false claim-boundary flags, expected missing-evidence statuses, and absence
  of heavy payloads. The v88 scaffold run passed with no violations.
- Limit:
  This is an offline consistency and claim-boundary audit only. It does not
  collect measurements, execute the SOP, calibrate the contact model, accept
  any replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold/audit tests passed with `3 passed in 0.63s`; full
  tests passed with `118 passed in 3.22s`; `git diff --check` passed before
  full-test validation. The generated audit artifact has `4` files, `20K`, and
  no `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was verified at
  `ec3490654c6555f3d9713392edc0f7ebe76cdc36`.
- Next step:
  Use the verifier before any future worksheet-filled run is cited as evidence.
  Live bench evidence still requires explicit approval for the exact read-only
  SOP step.

## 2026-05-25 v90 Read-Only Audit Modes

### Allow explicitly approved read-only evidence without weakening safety gates

- Branch:
  `exp/tase-ur10e-v90-readonly-evidence-audit-modes`
- Run:
  `runs/read_only_calibration_measurement_run_audit/20260525T013421`
- Report:
  `reports/read_only_calibration_measurement_audit_modes_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T012234 --audit-mode scaffold --run-id 20260525T013421`
- Result:
  Added explicit `scaffold` and `approved-read-only` audit modes. Scaffold
  mode keeps user confirmation and live hardware access false and rejects any
  worksheet rows. Approved-read-only mode requires explicit user confirmation,
  allows a boolean live-read flag, requires at least one evidence-status change,
  and still hard-fails motion, writes, zeroing/biasing, force control,
  contact-model updates, gate relaxation, hardware claims, and hardware
  readiness.
- Limit:
  This is an offline audit-gate refinement only. It does not collect
  measurements, execute the SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold/audit-mode tests passed with `4 passed in 0.86s`;
  full tests passed with `119 passed in 3.50s`; `git diff --check` passed
  before full-test validation. The generated audit artifact has `4` files,
  `20K`, and no `.npz/.npy/.mat/.tar/.gz/.zip` payloads. Branch push was
  verified at `aa4f48f8cb87d5af1f0051f65768fbc09e3c06ab`.
- Next step:
  Use `--audit-mode approved-read-only` only after the user approves the exact
  read-only SOP step and the run folder records that approval. Otherwise keep
  refining worksheets or gates offline.

## 2026-05-25 v91 Read-Only Evidence Finalizer

### Convert worksheet-filled scaffolds through an explicit offline approval gate

- Branch:
  `exp/tase-ur10e-v91-readonly-evidence-finalizer`
- Report:
  `reports/read_only_calibration_measurement_evidence_finalizer_report.md`
- Commands run:
  - `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `scripts/finalize_read_only_calibration_measurement_evidence.py`, an
  offline finalizer that requires the exact read-only approval phrase,
  approved step ID, operator, explicit `live_hardware_accessed` metadata,
  matching metrics YAML/JSON, default scaffold safety state, and at least one
  worksheet CSV row before converting a scaffold to
  `approved_read_only_evidence`. The tool derives evidence statuses from
  worksheet rows, writes YAML/JSON metrics consistently, updates the run
  summary and git state, and self-checks through the v90 `approved-read-only`
  audit mode.
- Limit:
  This is an offline metadata finalizer only. It does not collect
  measurements, execute the SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold/finalizer/audit tests passed with
  `6 passed in 1.34s`; full tests passed with `121 passed in 4.01s`;
  `git diff --check` passed after full-test validation. Branch push was
  verified at `0121ea3c6815eacdddcad6c0f877d44f2dc7fe73`.
- Next step:
  Use the finalizer only after the user approves the exact read-only SOP step
  and approved worksheet rows exist. If no live bench interaction is approved,
  refine KSM contact patch convention or orientation-gate worksheet coverage
  offline.

## 2026-05-25 v92 Read-Only Worksheet Coverage

### Add KSM contact patch and orientation semantics worksheets

- Branch:
  `exp/tase-ur10e-v92-readonly-worksheet-coverage`
- Runs:
  - `runs/read_only_calibration_measurement/20260525T014755`
  - `runs/read_only_calibration_measurement_run_audit/20260525T014756`
- Report:
  `reports/read_only_calibration_measurement_worksheet_coverage_report.md`
- Commands run:
  - `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T014755`
  - `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T014755 --audit-mode scaffold --run-id 20260525T014756`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `ksm_contact_patch_convention.csv` and
  `orientation_gate_semantics.csv` to the read-only measurement template. The
  audit validates optional worksheet headers when present and rejects optional
  worksheet rows in scaffold mode. The finalizer now derives KSM and
  orientation semantics evidence statuses from approved optional rows. The new
  scaffold run passed with `audit_passed = true`, `violations = []`, 14
  lightweight files, and no heavy payloads.
- Limit:
  This is worksheet/audit/finalizer coverage only. It does not collect
  measurements, execute the SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold/finalizer/audit tests passed with
  `7 passed in 1.56s`; the new scaffold audit passed; full tests passed with
  `122 passed in 4.26s`; `git diff --check` passed after full-test
  validation. Branch push was verified at
  `11bfa3ac02a06cf184343e119739e2392ae9cfbf`.
- Next step:
  Use the updated scaffold only after the user approves the exact read-only SOP
  step. If no live bench interaction is approved, refine orientation-gate
  acceptance semantics offline so collected read-only rows cannot be mistaken
  for gate relaxation.

## 2026-05-25 v93 Orientation Acceptance Boundary

### Keep orientation semantics evidence separate from gate acceptance

- Branch:
  `exp/tase-ur10e-v93-orientation-acceptance-boundary`
- Runs:
  - `runs/read_only_calibration_measurement/20260525T015400`
  - `runs/read_only_calibration_measurement_run_audit/20260525T015401`
- Report:
  `reports/read_only_calibration_measurement_orientation_acceptance_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/create_read_only_calibration_measurement_run.py --run-id 20260525T015400`
  - `python3 scripts/audit_read_only_calibration_measurement_run.py runs/read_only_calibration_measurement/20260525T015400 --audit-mode scaffold --run-id 20260525T015401`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added an explicit `orientation_gate_acceptance` metrics block and audit
  checks. Orientation semantics rows can be collected as read-only evidence,
  but the accepted gate remains `not_accepted`, `evidence_only = true`, and all
  accepted-gate fields stay null. The finalizer writes the same boundary when
  approved read-only orientation rows exist. Tests now reject fabricated
  orientation acceptance drift. The new scaffold audit passed with
  `audit_passed = true`, `violations = []`, 14 lightweight files, and no heavy
  payloads.
- Limit:
  This is a boundary/audit/finalizer refinement only. It does not collect
  measurements, execute the SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/create_read_only_calibration_measurement_run.py`
  passed; focused scaffold/finalizer/audit tests passed with
  `8 passed in 1.81s`; the new scaffold audit passed; full tests passed with
  `123 passed in 4.43s`; `git diff --check` passed after full-test
  validation. Branch push was verified at
  `b8246d247734c5df5a3d0c3f056d4ac60b25729c`.
- Next step:
  Use the updated scaffold only after the user approves the exact read-only SOP
  step. If no live bench interaction is approved, define a separate
  non-default gate-acceptance review template that cannot be invoked by the
  read-only evidence finalizer.

## 2026-05-25 v94 Gate-Acceptance Review Template

### Create a separate non-default review path for future gate decisions

- Branch:
  `exp/tase-ur10e-v94-gate-acceptance-review-template`
- Runs:
  - `runs/orientation_gate_acceptance_review/20260525T020054`
  - `runs/orientation_gate_acceptance_review_audit/20260525T020055`
- Report:
  `reports/orientation_gate_acceptance_review_template_report.md`
- Commands run:
  - `python3 -m py_compile scripts/create_orientation_gate_acceptance_review.py scripts/audit_orientation_gate_acceptance_review.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_orientation_gate_acceptance_review_template.py tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/create_orientation_gate_acceptance_review.py --review-id 20260525T020054`
  - `python3 scripts/audit_orientation_gate_acceptance_review.py runs/orientation_gate_acceptance_review/20260525T020054 --run-id 20260525T020055`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `templates/orientation_gate_acceptance_review/`,
  `scripts/create_orientation_gate_acceptance_review.py`, and
  `scripts/audit_orientation_gate_acceptance_review.py`. The scaffold is
  separate from read-only evidence finalization, defaults to
  `review_scaffold_not_executed`, keeps source evidence null, keeps
  `orientation_gate_acceptance.decision = not_accepted`, and rejects acceptance
  drift. The new scaffold audit passed with `audit_passed = true`,
  `violations = []`, 7 lightweight files, and no heavy payloads.
- Limit:
  This is a review-template/audit refinement only. It does not collect
  measurements, execute the read-only SOP, calibrate the contact model, accept
  any replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/create_orientation_gate_acceptance_review.py scripts/audit_orientation_gate_acceptance_review.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py`
  passed; focused gate-review/read-only tests passed with
  `11 passed in 2.03s`; the new gate-acceptance review scaffold audit passed;
  full tests passed with `126 passed in 4.72s`; `git diff --check` passed
  after full-test validation. Branch push was verified at
  `777e3b2c86ca51394c03aea74220cca0f3be284a`.
- Next step:
  Use the read-only measurement scaffold/finalizer/audit path only after the
  user approves the exact read-only SOP step. Keep the gate-acceptance review
  scaffold unused until a passed approved-read-only evidence run exists and a
  separate review is explicitly authorized.

## 2026-05-25 v95 Offline Completion Blockers

### Classify remaining requirements by offline versus approval-blocked work

- Branch:
  `exp/tase-ur10e-v95-offline-completion-blockers`
- Run:
  `runs/offline_completion_blockers/20260525T020734`
- Report:
  `reports/offline_completion_blockers_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_offline_completion_blockers.py`
  - `scripts/run_tests.sh tests/test_offline_completion_blockers.py`
  - `python3 scripts/audit_offline_completion_blockers.py --run-id 20260525T020734`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `scripts/audit_offline_completion_blockers.py`, which reads the current
  relaxed simulation, strict staged, robustness, measured-geometry, read-only
  measurement, and gate-acceptance review metrics. The audit reports
  `overall_goal_complete = false`, `completion_blocked = true`, and
  `do_not_mark_goal_complete = true`. It classifies strict paper-equivalent
  full staged feasibility and robustness as non-final offline-actionable, while
  approved read-only calibration evidence, calibrated contact geometry,
  orientation-gate acceptance, and hardware readiness remain blocked on
  explicit approval/evidence.
- Limit:
  This is a blocker-classification audit only. It does not collect
  measurements, execute the read-only SOP, calibrate the contact model, accept
  any replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_offline_completion_blockers.py` passed;
  focused blocker-audit tests passed with `2 passed in 0.19s`; the v95 blocker
  audit run was created; full tests passed with `128 passed in 4.80s`;
  `git diff --check` passed after full-test validation. Branch push was
  verified at `af1fa3f793219afefcf4b0c97bc825ef473adda4`.
- Next step:
  Use the read-only measurement scaffold/finalizer/audit path only after the
  user approves the exact read-only SOP step. Without live approval, continue
  only non-final offline simulation or paper-platform work identified by the
  v95 audit.

## 2026-05-25 v96 Strict Feasibility Blockers

### Quantify the strict setup terminal tradeoff

- Branch:
  `exp/tase-ur10e-v96-strict-feasibility-blockers`
- Run:
  `runs/strict_feasibility_blockers/20260525T051640`
- Report:
  `reports/strict_feasibility_blockers_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_feasibility_blockers.py`
  - `scripts/run_tests.sh tests/test_strict_feasibility_blockers.py`
  - `python3 scripts/audit_strict_feasibility_blockers.py --run-id 20260525T051640`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `scripts/audit_strict_feasibility_blockers.py`, which reads the strict
  acceptance thresholds, the posture-regularized strict staged summary, the
  three-phase settle summary, and the v95 blocker metrics. The audit reports
  `strict_feasibility_complete = false`, `strict_setup_gate_complete = false`,
  strict full staged feasibility `0 / 4`, three-phase setup terminal state
  `0 / 10`, three-phase trajectory feasibility `8 / 10`, and
  `primary_blocker = strict_setup_terminal_tradeoff`.
- Limit:
  This is an offline blocker audit only. It does not collect measurements,
  execute the read-only SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_strict_feasibility_blockers.py` passed;
  focused strict-feasibility blocker tests passed with `2 passed in 0.18s`;
  the v96 blocker audit run was created; full tests passed with
  `130 passed in 5.04s`; `git diff --check` passed after full-test
  validation. Branch push was verified at
  `31bcca912b2623bd4f29850077ab86a76ec1ec4e`.
- Next step:
  Without live approval, continue only non-final offline work. Candidate paths
  are strict setup policy search across tangential/orientation/force/qdot gates
  or the separate robustness blocker from the v95 audit.

## 2026-05-25 v97 Robustness Blockers

### Quantify accepted-model robustness gaps

- Branch:
  `exp/tase-ur10e-v97-robustness-blockers`
- Run:
  `runs/robustness_blockers/20260525T052457`
- Report:
  `reports/robustness_blockers_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_robustness_blockers.py`
  - `scripts/run_tests.sh tests/test_robustness_blockers.py`
  - `python3 scripts/audit_robustness_blockers.py --run-id 20260525T052457`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `scripts/audit_robustness_blockers.py`, which reads the v64 baseline
  stitched sensitivity, v65 timing-margin recovery, v66/v67 base-z recovery
  and bracket, v73 positive stitched sensitivity, v75 qdot012 positive
  recovery, v84 weighted orientation sensitivity, v85 contact margin, and the
  v95/v96 blocker metrics. The audit reports `robustness_complete = false`,
  baseline diagnostic stitched sensitivity `4 / 9`, positive stitched
  sensitivity `37 / 40`, and `primary_blocker =
  accepted_model_robustness_not_closed`.
- Limit:
  This is an offline blocker audit only. It does not collect measurements,
  execute the read-only SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_robustness_blockers.py` passed;
  focused robustness blocker tests passed with `2 passed in 0.38s`; the v97
  blocker audit run was created; full tests passed with
  `132 passed in 5.44s`; `git diff --check` passed after full-test
  validation. Branch push was verified at
  `f74c3719d4770e21604ae0087d8b27cc22e4b7d9`.
- Next step:
  Without live approval, continue only non-final offline work. Candidate paths
  are defining and stress-testing one accepted diagnostic robustness matrix,
  strict setup policy search, or paper-platform parity refinement without
  upgrading claim scope.

## 2026-05-25 v98 Diagnostic Robustness Matrix Candidate

### Assemble current robustness faces into one candidate matrix

- Branch:
  `exp/tase-ur10e-v98-diagnostic-robustness-matrix`
- Run:
  `runs/diagnostic_robustness_matrix_candidate/20260525T053101`
- Report:
  `reports/diagnostic_robustness_matrix_candidate_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_diagnostic_robustness_matrix_candidate.py`
  - `scripts/run_tests.sh tests/test_diagnostic_robustness_matrix_candidate.py`
  - `python3 scripts/audit_diagnostic_robustness_matrix_candidate.py --run-id 20260525T053101`
  - `scripts/run_tests.sh`
  - `git diff --check`
- Result:
  Added `scripts/audit_diagnostic_robustness_matrix_candidate.py`, which reads
  the v95 offline blockers, v96 strict blockers, and v97 robustness blockers
  metrics. The audit defines a 12-cell diagnostic robustness matrix candidate:
  7 diagnostic passes, 1 non-final diagnostic recovery, and 4 failed cells
  (`base_z_plus1mm`, `positive_fast_timing_0p0075`,
  `positive_orientation_gate_0p119`, and `weighted_plus1mm_0p119_gate`).
- Limit:
  This is an offline candidate-matrix audit only. It does not collect
  measurements, execute the read-only SOP, calibrate the contact model, accept
  any replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_diagnostic_robustness_matrix_candidate.py`
  passed; focused matrix-candidate tests passed with `2 passed in 0.18s`; the
  v98 candidate matrix audit run was created; full tests passed with
  `134 passed in 5.59s`; `git diff --check` passed after full-test
  validation. Branch push was verified at
  `9d284be82583ba88cb76fbc3a21cfabf29c8ca50`.
- Next step:
  Without live approval, continue only non-final offline work. The clearest
  target is to convert the four failed v98 matrix cells into executable
  offline experiment cases.

## 2026-05-25 v99 Failed Diagnostic Robustness Experiment Matrix

### Convert failed candidate cells into planned offline commands

- Branch:
  `exp/tase-ur10e-v99-failed-robustness-experiment-matrix`
- Run:
  `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909`
- Report:
  `reports/failed_diagnostic_robustness_experiment_matrix_report.md`
- Commands run:
  - `python3 -m py_compile scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
  - `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_matrix.py`
  - `python3 scripts/create_failed_diagnostic_robustness_experiment_matrix.py --run-id 20260525T053909`
  - `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/metrics.yaml`
  - `scripts/run_tests.sh`
- Result:
  Added `scripts/create_failed_diagnostic_robustness_experiment_matrix.py`,
  which reads the v98 candidate matrix and verifies the four expected failed
  cells: `base_z_plus1mm`, `positive_fast_timing_0p0075`,
  `positive_orientation_gate_0p119`, and `weighted_plus1mm_0p119_gate`. The
  generated run is `planned_not_executed`, contains four concrete offline
  commands in `commands.sh`, and creates no experiment output directories.
- Limit:
  This is an offline planning artifact only. It does not execute the planned
  experiments, collect measurements, execute the read-only SOP, calibrate the
  contact model, accept any replacement gate, prove robustness, prove strict
  paper-equivalent feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/create_failed_diagnostic_robustness_experiment_matrix.py`
  passed; focused failed-cell matrix tests passed with `2 passed in 0.13s`;
  the v99 planned experiment matrix run was created; the YAML anchor check
  found no anchors; full tests passed with `136 passed in 5.75s`;
  `git diff --check` passed after validation. Branch push was verified at
  `f81df802cede561528849dc886b303ad3d5e63dc`.
- Next step:
  Without live approval, continue only non-final offline work. The clearest
  target is to execute at most one planned v99 command at a time and add a
  separate audit that compares the output metrics against the failed-cell
  closure criteria.

## 2026-05-25 v100 Base-Z Failed-Cell Execution Audit

### Execute and audit the planned `base_z_plus1mm` command

- Branch:
  `exp/tase-ur10e-v100-base-z-failed-cell-execution`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T054646`
- Report:
  `reports/failed_diagnostic_robustness_experiment_execution_report.md`
- Commands run:
  - `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_stage_a_base_z_bracket.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm --base-z-deltas-mm 1.0 --stage-a-durations-s 15.0,16.0,18.0`
  - `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  - `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_execution.py`
  - `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T054646`
  - `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T054646/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/base_z_plus1mm/metrics.yaml`
  - `scripts/run_tests.sh`
- Result:
  Executed the v99 `base_z_plus1mm` command and added
  `scripts/audit_failed_diagnostic_robustness_experiment_execution.py` to
  compare the output against the failed-cell closure criteria. The executed
  cell is `executed_unresolved`: start pass count `0`, terminal pass count
  `0`, path geometry pass count `0`, duration recovery count `0`, and
  terminal orientation error `0.11948560786548146 rad`.
- Limit:
  This is one offline diagnostic experiment plus a comparison audit. It does
  not execute the other three v99 planned commands, collect measurements,
  execute the read-only SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed; focused execution-audit tests passed with `2 passed in 0.12s`; the
  v100 execution audit run was created; the YAML anchor check found no
  anchors; full tests passed with `138 passed in 5.87s`;
  `git diff --check` passed after validation. Branch push was verified at
  `ce48bcef63a1fa5f3c3969530774cfe59c6275b9`.
- Next step:
  Without live approval, continue only non-final offline work. Candidate paths
  are to execute one remaining v99 planned command at a time, or design a
  narrower diagnostic probe for the unresolved `base_z_plus1mm` start-contact
  and terminal-orientation failure.

## 2026-05-25 v101 Positive Fast-Timing Failed-Cell Execution

### Execute and audit the planned `positive_fast_timing_0p0075` command

- Branch:
  `exp/tase-ur10e-v101-positive-fast-timing-execution`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T055322`
- Report:
  `reports/positive_fast_timing_failed_cell_execution_report.md`
- Commands run:
  - `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_stitched_sensitivity.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075 --base-z-deltas-mm 1.0 --scenarios paper_time_scale_0p0075`
  - `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  - `scripts/run_tests.sh tests/test_failed_diagnostic_robustness_experiment_execution.py`
  - `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T055322`
  - `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T055322/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_fast_timing_0p0075/metrics.yaml`
- Result:
  Executed the v99 `positive_fast_timing_0p0075` command and extended the
  execution audit to evaluate the cell. The executed cell is
  `executed_unresolved`: Stage A passes, but stitched recovery is false with
  Stage B handoff `3 / 4`. The failed row is E2, with failed criteria
  `qdot_saturation_fraction`, `tail_max_qdot_utilization`, and
  `max_orientation_error_rad`.
- Limit:
  This is one additional offline diagnostic experiment plus a comparison
  audit. It does not execute the two remaining v99 planned commands, collect
  measurements, execute the read-only SOP, calibrate the contact model, accept
  any replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed; focused execution-audit tests passed with `3 passed in 0.20s`; the
  v101 execution audit run was created; the YAML anchor check found no
  anchors; full tests passed with `139 passed in 5.89s`;
  `git diff --check` passed after validation. Branch push was verified at
  `7bd28a07a3eb4fe9a1122b9397b156a25401d33f`.
- Next step:
  Without live approval, continue only non-final offline work. Candidate paths
  are to execute one of the two remaining v99 planned commands, or design
  narrower diagnostic probes for the unresolved `+1.0 mm` rows.

## 2026-05-25 v102 Positive Orientation-Gate Failed-Cell Execution

### Execute and audit the planned `positive_orientation_gate_0p119` command

- Branch:
  `exp/tase-ur10e-v102-positive-orientation-gate-execution`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T060119`
- Report:
  `reports/positive_orientation_gate_failed_cell_execution_report.md`
- Commands run:
  - `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_positive_orientation_gate_boundary.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119 --base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11975,0.1199,0.11995,0.11997,0.11998,0.12`
  - `python3 -m py_compile scripts/audit_positive_orientation_gate_boundary.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  - `scripts/run_tests.sh tests/test_positive_orientation_gate_boundary.py tests/test_failed_diagnostic_robustness_experiment_execution.py`
  - `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T060119`
  - `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T060119/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/positive_orientation_gate_0p119/metrics.yaml`
- Result:
  Executed the v99 `positive_orientation_gate_0p119` command and extended the
  execution audit to evaluate the cell. The executed cell is
  `executed_unresolved`: the current `0.119 rad` gate fails, Stage A at that
  gate fails with handoff `0 / 4`, and the diagnostic boundary first passes at
  `0.11998 rad`.
- Limit:
  This is one additional offline diagnostic experiment plus a comparison
  audit. The `0.11998 rad` boundary is not an accepted replacement gate. V102
  does not execute the remaining v99 planned command, collect measurements,
  execute the read-only SOP, calibrate the contact model, accept any
  replacement gate, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_positive_orientation_gate_boundary.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed; focused execution-audit tests passed with `6 passed in 0.48s`; the
  v102 execution audit run was created; the YAML anchor check found no
  anchors; full tests passed with `142 passed in 6.06s`;
  `git diff --check` passed after validation. Branch push was verified at
  `5f7b30e7009296ca8153a020bd1475fec0b6dabd`.
- Next step:
  Without live approval, continue only non-final offline work. Candidate paths
  are to execute the remaining `weighted_plus1mm_0p119_gate` planned command,
  or design narrower diagnostic probes for the unresolved `+1.0 mm` rows.

## 2026-05-25 v103 Weighted +1.0 mm Gate Failed-Cell Execution

### Execute and audit the planned `weighted_plus1mm_0p119_gate` command

- Branch:
  `exp/tase-ur10e-v103-weighted-plus1mm-gate-execution`
- Runs:
  - `runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate`
  - `runs/failed_diagnostic_robustness_experiment_audit/20260525T061328`
- Report:
  `reports/weighted_plus1mm_gate_failed_cell_execution_report.md`
- Commands run:
  - `/usr/bin/python3 /home/andy/reproduce-tase/scripts/audit_weighted_gate_time_matrix.py --output-dir /home/andy/reproduce-tase/runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate --base-z-deltas-mm 1.0 --boundary-base-z-delta-mm 1.0 --orientation-gates 0.119,0.11925,0.1195,0.11955,0.1196,0.1197,0.11995`
  - `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py scripts/audit_weighted_timing_recovery.py scripts/audit_stage_b_priority_recovery.py scripts/audit_positive_stitched_sensitivity.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  - `scripts/run_tests.sh tests/test_weighted_gate_time_matrix.py tests/test_failed_diagnostic_robustness_experiment_execution.py`
  - `python3 scripts/audit_failed_diagnostic_robustness_experiment_execution.py --run-id 20260525T061328`
  - `rg -n "&id|\*id" runs/failed_diagnostic_robustness_experiment_audit/20260525T061328/metrics.yaml runs/failed_diagnostic_robustness_experiment_matrix/20260525T053909/experiments/weighted_plus1mm_0p119_gate/metrics.yaml`
- Result:
  Executed the v99 `weighted_plus1mm_0p119_gate` command and extended the
  execution audit to evaluate the cell. The executed cell is
  `executed_unresolved`: all current `0.119 rad` weighted rows fail on
  orientation, while diagnostic boundaries first pass at `0.11955 rad` for
  time `0.0075` and `0.1196 rad` for time `0.01`. The v103 audit reports
  executed cells `4`, closed cells `0`, and not-executed cells `0`.
- Limit:
  This is one additional offline diagnostic experiment plus a comparison
  audit. The diagnostic boundaries are not accepted replacement gates. V103
  does not collect measurements, execute the read-only SOP, calibrate the
  contact model, accept any replacement gate, prove robustness, prove strict
  paper-equivalent feasibility, or authorize hardware motion/configuration.
- Validation:
  `python3 -m py_compile scripts/audit_weighted_gate_time_matrix.py scripts/audit_weighted_timing_recovery.py scripts/audit_stage_b_priority_recovery.py scripts/audit_positive_stitched_sensitivity.py scripts/audit_failed_diagnostic_robustness_experiment_execution.py`
  passed; focused execution-audit tests passed with `6 passed in 0.96s`; the
  v103 execution audit run was created; the YAML anchor check found no
  anchors; full tests passed with `144 passed in 6.60s`;
  `git diff --check` passed after validation. Branch push was verified at
  `ce266165b9ec3e47dbe6fdcce3cb0c717b8dda15`.
- Next step:
  Without live approval, continue only non-final offline work. All v99 planned
  commands have now been executed; candidate paths are narrower diagnostic
  probes for the unresolved `+1.0 mm` rows or explicitly approved read-only
  evidence before changing contact/gate interpretation.

## 2026-05-25 v104 Plus1mm Unresolved Diagnostic Probe

### Classify remaining `+1.0 mm` blocker signatures

- Branch:
  `exp/tase-ur10e-v104-plus1mm-unresolved-probe`
- Runs:
  - `runs/plus1mm_unresolved_diagnostic_probe/20260525T062237`
- Report:
  `reports/plus1mm_unresolved_diagnostic_probe_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
  - `scripts/run_tests.sh tests/test_plus1mm_unresolved_diagnostic_probe.py`
  - `python3 scripts/audit_plus1mm_unresolved_diagnostic_probe.py`
  - `rg -n "&id|\*id" runs/plus1mm_unresolved_diagnostic_probe/20260525T062237/metrics.yaml`
- Result:
  Classified the four executed unresolved `+1.0 mm` failed cells from actual
  v100-v103 metrics. All four remain unresolved. The only qdot-limited cell is
  `positive_fast_timing_0p0075`; the weighted current-gate rows have max qdot
  saturation `0.0` and remain orientation-margin/gate-acceptance blocked.
- Limit:
  This is post-hoc offline bookkeeping over existing metrics. It does not rerun
  MuJoCo, collect measurements, execute the read-only SOP, calibrate the
  contact model, accept any replacement gate, prove robustness, prove strict
  paper-equivalent feasibility, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `2 passed in 0.22s`; YAML anchor check found no
  anchors in the generated metrics; full tests passed with
  `146 passed in 6.74s`; `git diff --check` passed. Branch push was verified
  at `b412ddf5bbec20682ce021b754aa0efc845a3372`.
- Next step:
  Without live approval, continue only non-final offline work. The most focused
  offline candidates are a `base_z_plus1mm` start-contact versus
  terminal-orientation split probe or a `positive_fast_timing_0p0075` E2
  qdot/usage isolation probe.

## 2026-05-25 v105 Positive Fast-Timing E2 Qdot Isolation

### Isolate qdot-limit effects on the `+1.0 mm` fast E2 row

- Branch:
  `exp/tase-ur10e-v105-positive-fast-e2-qdot-isolation`
- Runs:
  - `runs/positive_fast_timing_e2_qdot_isolation/20260525T063019`
- Report:
  `reports/positive_fast_timing_e2_qdot_isolation_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_stage_b_e2_margin.py`
  - `scripts/run_tests.sh tests/test_positive_stage_b_e2_margin.py`
  - `python3 scripts/audit_positive_stage_b_e2_margin.py --output-dir runs/positive_fast_timing_e2_qdot_isolation/20260525T063019 --base-z-deltas-mm 1.0 --paper-time-scales 0.0075,0.007,0.0065,0.006,0.0055,0.0052,0.005 --qdot-probe-limits-rad-s 0.15,0.18,0.2,0.25,0.3`
  - `rg -n "&id|\*id" runs/positive_fast_timing_e2_qdot_isolation/20260525T063019/metrics.yaml`
- Result:
  The first tested E2 timing pass is `paper_time_scale = 0.0052`. At
  `paper_time_scale = 0.0075`, qdot-limit-only probes fail `0 / 5` through
  `0.3 rad/s`: qdot saturation can be reduced to `0.0`, but orientation
  remains above the run-local `0.12 rad` gate.
- Limit:
  This is E2-only diagnostic simulation. It does not close the v99
  `positive_fast_timing_0p0075` failed cell, accept a relaxed orientation gate,
  calibrate contact geometry, prove robustness, prove strict paper-equivalent
  feasibility, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `1 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; full tests passed with
  `147 passed in 6.86s`; `git diff --check` passed. Branch push was verified
  at `6cc6733a3ac78b93090d4079b62480ade57e82a7`.
- Next step:
  Without live approval, continue only non-final offline work. Avoid pure
  qdot-limit escalation for this row; either probe orientation-margin
  reduction at `paper_time_scale = 0.0075` without gate relaxation or switch to
  the `base_z_plus1mm` start-contact versus terminal-orientation split.

## 2026-05-25 v106 Positive Fast E2 Orientation-Margin Probe

### Probe fixed-gate priority recovery on the `+1.0 mm` fast E2 row

- Branch:
  `exp/tase-ur10e-v106-positive-fast-e2-orientation-margin`
- Runs:
  - `runs/positive_fast_e2_orientation_margin/20260525T063817`
- Report:
  `reports/positive_fast_e2_orientation_margin_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_fast_e2_orientation_margin.py`
  - `scripts/run_tests.sh tests/test_positive_fast_e2_orientation_margin.py`
  - `python3 scripts/audit_positive_fast_e2_orientation_margin.py --output-dir runs/positive_fast_e2_orientation_margin/20260525T063817`
  - `rg -n "&id|\*id" runs/positive_fast_e2_orientation_margin/20260525T063817/metrics.yaml`
- Result:
  The E2-only priority matrix keeps `paper_time_scale = 0.0075`,
  `qdot_limit = 0.15 rad/s`, and the `0.12 rad` orientation gate fixed.
  Weighted rows pass E2 (`2 / 6` scenarios) with
  `max_orientation_error_rad = 0.11954627160547111`, qdot saturation `0.0`,
  and tail qdot utilization `0.5177926211135458`. The linear-primary baseline
  still fails qdot saturation, tail qdot utilization, and orientation.
- Limit:
  This is E2-only diagnostic simulation. It does not rerun the full E1-E4
  failed-cell audit, close the v99 `positive_fast_timing_0p0075` failed cell,
  make `weighted` a canonical controller default, accept a relaxed orientation
  gate, calibrate contact geometry, prove robustness, prove strict
  paper-equivalent feasibility, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `1 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `148 passed in 6.81s`; `git diff --check` passed.
  Branch push was verified at
  `716ecde74a428c15ce17445018ca7028b1db9527`.
- Next step:
  Without live approval, continue only non-final offline work. The next
  positive-fast probe can rerun the full E1-E4 failed-cell audit with weighted
  priority while keeping the `0.12 rad` gate fixed; the other clean target is
  the `base_z_plus1mm` start-contact versus terminal-orientation split.

## 2026-05-25 v107 Positive Fast Weighted Full-Cell Probe

### Run exact fixed-gate E1-E4 fast face with weighted priority

- Branch:
  `exp/tase-ur10e-v107-positive-fast-weighted-full-cell`
- Runs:
  - `runs/positive_fast_weighted_full_cell/20260525T064719`
- Report:
  `reports/positive_fast_weighted_full_cell_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_positive_fast_weighted_full_cell.py`
  - `scripts/run_tests.sh tests/test_positive_fast_weighted_full_cell.py`
  - `python3 scripts/audit_positive_fast_weighted_full_cell.py --output-dir runs/positive_fast_weighted_full_cell/20260525T064719`
  - `rg -n "&id|\*id" runs/positive_fast_weighted_full_cell/20260525T064719/metrics.yaml`
  - `find runs/positive_fast_weighted_full_cell/20260525T064719 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The full E1-E4 matrix keeps `paper_time_scale = 0.0075`, `qdot_limit =
  0.15 rad/s`, and the `0.12 rad` orientation gate fixed. The linear-primary
  baseline still fails E2; both weighted scenarios pass `4 / 4`. The weighted
  rows report maximum Stage B orientation `0.11954627160547111`, qdot
  saturation `0.0`, and tail qdot utilization `0.5177926211135458`.
- Limit:
  This is full-cell diagnostic simulation for one face. It does not close the
  original v99 `positive_fast_timing_0p0075` failed cell because it does not
  accept `weighted` as a canonical controller default. It does not accept a
  relaxed orientation gate, calibrate contact geometry, prove robustness, prove
  strict paper-equivalent feasibility, or authorize hardware
  motion/configuration.
- Validation:
  Focused tests passed with `2 passed in 0.12s`; YAML anchor check found no
  anchors in the root summary metrics; raw/heavy artifact scan found no
  payloads; full tests passed with `150 passed in 6.79s`; `git diff --check`
  passed.
  Branch push was verified at
  `2e94f4bbd9ac25228c819bdc789eb6bc1f75f719`.
- Next step:
  Without live approval, continue only non-final offline work. The next
  positive-fast step should audit the acceptance boundary for promoting
  weighted priority into a named diagnostic controller profile; the other clean
  target is the `base_z_plus1mm` start-contact versus terminal-orientation
  split.

## 2026-05-25 v108 Base-Z Plus1mm Split Audit

### Split start-contact, terminal-orientation, path, and handoff blockers

- Branch:
  `exp/tase-ur10e-v108-base-z-plus1mm-split`
- Runs:
  - `runs/base_z_plus1mm_split/20260525T071440`
- Report:
  `reports/base_z_plus1mm_split_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_base_z_plus1mm_split.py`
  - `scripts/run_tests.sh tests/test_base_z_plus1mm_split.py`
  - `python3 scripts/audit_base_z_plus1mm_split.py --output-dir runs/base_z_plus1mm_split/20260525T071440`
  - `rg -n "&id|\*id" runs/base_z_plus1mm_split/20260525T071440/metrics.yaml`
  - `find runs/base_z_plus1mm_split/20260525T071440 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The post-hoc split keeps the exact v99 `base_z_plus1mm` cell unresolved, but
  separates the blockers. Broader seeds recover `+1.0 mm` start contact, so
  the exact start miss is local seed-limited. Terminal force/x-y/contact
  passes, but terminal orientation is `0.11948560786548146 rad`, which exceeds
  the current `0.08 rad` diagnostic gate by `0.039485607865481456 rad`. The
  run-local `0.12 rad` gate recovers terminal and path feasibility with
  minimum path duration `10.018584837157274 s`, but stitched Stage B remains
  unrecovered with handoff counts `3 / 4` at both tested durations.
- Limit:
  This is post-hoc offline bookkeeping over existing metrics. It does not
  rerun MuJoCo, close the v99 `base_z_plus1mm` failed cell, accept the
  `0.12 rad` gate as canonical, change canonical configs, calibrate contact
  geometry, prove robustness, prove strict paper-equivalent feasibility, or
  authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.09s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `153 passed in 7.22s`; `git diff --check` passed.
  Branch push was verified at
  `987e360d9244bf8c98ce549c21c7787ab163868a`.
- Next step:
  Without live approval, continue only non-final offline work. A next branch
  can audit the acceptance boundary for promoting weighted priority into a
  named diagnostic controller profile, or target the relaxed `base_z_plus1mm`
  Stage B handoff timing/qdot blocker while keeping the relaxed orientation
  gate non-canonical.

## 2026-05-25 v109 Relaxed Base-Z Weighted Handoff Probe

### Test weighted priority on the relaxed `base_z_plus1mm` handoff blocker

- Branch:
  `exp/tase-ur10e-v109-relaxed-base-z-weighted-handoff`
- Runs:
  - `runs/relaxed_base_z_weighted_handoff/20260525T073012`
- Report:
  `reports/relaxed_base_z_weighted_handoff_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_relaxed_base_z_weighted_handoff.py`
  - `scripts/run_tests.sh tests/test_relaxed_base_z_weighted_handoff.py`
  - `python3 scripts/audit_relaxed_base_z_weighted_handoff.py --output-dir runs/relaxed_base_z_weighted_handoff/20260525T073012`
  - `rg -n "&id|\*id" runs/relaxed_base_z_weighted_handoff/20260525T073012/metrics.yaml`
  - `find runs/relaxed_base_z_weighted_handoff/20260525T073012 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The relaxed `base_z_plus1mm` handoff matrix keeps the v70 run-local
  `0.12 rad` orientation gate, `paper_time_scale = 0.01`, and
  `qdot_limit = 0.15 rad/s` fixed. The linear-primary baseline fails E2 at
  both tested Stage A durations (`15.0 s`, `16.0 s`) with max orientation
  `0.12043140848858806`, qdot saturation `0.997`, and tail qdot utilization
  `1.0`. Both weighted scenarios pass `4 / 4` at both durations with maximum
  Stage B orientation `0.11956645203696047`, qdot saturation `0.0`, and tail
  qdot utilization `0.520987929048311`.
- Limit:
  This is diagnostic simulation using the run-local relaxed gate. It does not
  close the original v99 `base_z_plus1mm` failed cell, accept the `0.12 rad`
  gate as canonical, accept weighted priority as a canonical controller
  default, change canonical configs, calibrate contact geometry, prove
  robustness, prove strict paper-equivalent feasibility, or authorize hardware
  motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `156 passed in 6.93s`; `git diff --check` passed.
  Branch push was verified at
  `3a766ae641d7d4cda70864da4cfad366786e6515`.
- Next step:
  Without live approval, continue only non-final offline work. The next branch
  can audit the acceptance boundary for promoting weighted priority into a
  named diagnostic controller profile using v107 and v109, while keeping
  canonical controller, orientation-gate, failed-cell closure, and robustness
  boundaries false.

## 2026-05-25 v110 Weighted Priority Profile-Boundary Audit

### Name weighted priority as a diagnostic profile without changing canonical claims

- Branch:
  `exp/tase-ur10e-v110-weighted-priority-profile-boundary`
- Runs:
  - `runs/weighted_priority_profile_boundary/20260525T074100`
- Report:
  `reports/weighted_priority_profile_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_weighted_priority_profile_boundary.py`
  - `scripts/run_tests.sh tests/test_weighted_priority_profile_boundary.py`
  - `python3 scripts/audit_weighted_priority_profile_boundary.py --output-dir runs/weighted_priority_profile_boundary/20260525T074100`
  - `rg -n "&id|\*id" runs/weighted_priority_profile_boundary/20260525T074100/metrics.yaml`
  - `find runs/weighted_priority_profile_boundary/20260525T074100 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The post-hoc audit uses the verified v107 and v109 metrics. It supports
  naming `weighted_zero_angular_stage_b_diagnostic` as a diagnostic profile for
  the covered faces. Weighted rows recover both faces, and baseline failures
  are reproduced in both faces. The profile boundary keeps
  `canonical_controller_change = false`,
  `canonical_orientation_gate_change = false`, `failed_cell_closed = false`,
  `robustness_claim = false`, and `hardware_readiness = false`.
- Limit:
  This is post-hoc offline bookkeeping over existing metrics. It does not
  rerun MuJoCo, change the canonical controller default, accept the `0.12 rad`
  orientation gate, close any original v99 failed cell, prove robustness,
  prove strict paper-equivalent feasibility, calibrate contact geometry, or
  authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.04s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `159 passed in 6.93s`; `git diff --check` passed.
  Branch push was verified at
  `f48240c72188e8d4fd4e18bd69fe37c38e1e1d90`.
- Next step:
  Without live approval, continue only non-final offline work. The next branch
  can audit whether the v98/v99 diagnostic robustness matrix can be restated
  with the named weighted diagnostic profile while keeping canonical
  controller/gate changes, failed-cell closure, and robustness claims false.

## 2026-05-25 v111 Weighted Profile Matrix Restatement

### Restate the v98/v99 matrix with the named weighted profile

- Branch:
  `exp/tase-ur10e-v111-weighted-profile-matrix-restatement`
- Runs:
  - `runs/weighted_profile_matrix_restatement/20260525T075040`
- Report:
  `reports/weighted_profile_matrix_restatement_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_weighted_profile_matrix_restatement.py`
  - `scripts/run_tests.sh tests/test_weighted_profile_matrix_restatement.py`
  - `python3 scripts/audit_weighted_profile_matrix_restatement.py --output-dir runs/weighted_profile_matrix_restatement/20260525T075040`
  - `rg -n "&id|\*id" runs/weighted_profile_matrix_restatement/20260525T075040/metrics.yaml`
  - `find runs/weighted_profile_matrix_restatement/20260525T075040 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The post-hoc audit restates the v98/v99 matrix with
  `weighted_zero_angular_stage_b_diagnostic` as a non-canonical overlay. The
  source matrix still has `12` cells and `4` failed cells. The profile overlay
  supports `base_z_plus1mm` and `positive_fast_timing_0p0075`;
  `positive_orientation_gate_0p119` and `weighted_plus1mm_0p119_gate` remain
  gate-acceptance blocked. Closed cells remain `0`, candidate matrix complete
  remains `false`, accepted-as-robustness-proof remains `false`, and
  `do_not_mark_goal_complete` remains `true`.
- Limit:
  This is post-hoc offline bookkeeping over existing metrics. It does not
  rerun MuJoCo, change the canonical controller default, accept the `0.12 rad`
  orientation gate, close any original v99 failed cell, prove robustness,
  prove strict paper-equivalent feasibility, calibrate contact geometry, or
  authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.04s`; YAML anchor check found no
  anchors in the generated metrics after the no-alias YAML writer update;
  raw/heavy artifact scan found no payloads; full tests passed with
  `162 passed in 7.00s`; `git diff --check` passed.
  Branch push was verified at
  `7900d441e3d072026bdf0f874da98b322cf9628d`.
- Next step:
  Without live approval, continue only non-final offline work. The next branch
  can prioritize remaining non-profile-covered blockers: orientation gate
  acceptance, contact calibration, strict feasibility, and hardware-readiness
  evidence.

## 2026-05-25 v112 Remaining Blocker Prioritization

### Rank remaining blockers using existing offline evidence

- Branch:
  `exp/tase-ur10e-v112-remaining-blocker-prioritization`
- Runs:
  - `runs/remaining_blocker_prioritization/20260525T072557`
- Report:
  `reports/remaining_blocker_prioritization_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_remaining_blocker_prioritization.py`
  - `scripts/run_tests.sh tests/test_remaining_blocker_prioritization.py`
  - `python3 scripts/audit_remaining_blocker_prioritization.py --output-dir runs/remaining_blocker_prioritization/20260525T072557`
  - `rg -n "&id|\*id" runs/remaining_blocker_prioritization/20260525T072557/metrics.yaml`
  - `find runs/remaining_blocker_prioritization/20260525T072557 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The post-hoc audit ranks the current remaining blockers without running
  MuJoCo or touching hardware. The top priority blocker is
  `approved_read_only_calibration_evidence`; remaining blocker count is `6`;
  live/approval-blocked count is `4`; offline-actionable non-final count is
  `2`; profile-overlay supported cell count is `2`; gate-acceptance blocked
  cell count is `2`; closed cells remain `0`; candidate matrix complete is
  `false`; accepted-as-robustness-proof is `false`; and
  `do_not_mark_goal_complete` remains `true`.
- Limit:
  This is post-hoc offline bookkeeping over existing metrics. It does not
  rerun MuJoCo, accept a replacement orientation gate, change the canonical
  controller, close failed cells, prove robustness, prove strict
  paper-equivalent feasibility, calibrate contact geometry, establish hardware
  readiness, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.16s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `165 passed in 7.13s`; `git diff --check` passed.
  Branch push was verified at
  `8ed1b881fae6d27e815feecf0b59724f64cb2a9a`.
- Next step:
  Without live approval, continue only non-final offline work. The next clean
  offline branch can target strict feasibility, because v112 identifies it as
  the highest-priority blocker that can advance offline without approval.

## 2026-05-25 v113 Strict Feasibility Policy Probe

### Probe compact Stage A policies for the strict setup blocker

- Branch:
  `exp/tase-ur10e-v113-strict-feasibility-policy-probe`
- Runs:
  - `runs/strict_feasibility_policy_probe/20260525T073519`
- Report:
  `reports/strict_feasibility_policy_probe_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_feasibility_policy_probe.py`
  - `scripts/run_tests.sh tests/test_strict_feasibility_policy_probe.py`
  - `python3 scripts/audit_strict_feasibility_policy_probe.py --output-dir runs/strict_feasibility_policy_probe/20260525T073519`
  - `rg -n "&id|\*id" runs/strict_feasibility_policy_probe/20260525T073519/metrics.yaml`
  - `find runs/strict_feasibility_policy_probe/20260525T073519 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline E2 policy probe tests eight Stage A policies over baseline,
  linear-primary recenter/settle, weighted recenter/settle, and aggressive
  planar-retention variants. It reports setup terminal-state pass `0 / 8`,
  trajectory feasibility pass `4 / 8`, planned setup-then-trajectory pass
  `0 / 8`, and full staged feasibility pass `0 / 8`. All eight setup rows
  violate qdot saturation and tail qdot utilization. The best x/y row still
  fails orientation, while the best orientation rows still fail x/y and setup
  qdot criteria.
- Limit:
  This is offline simulation only. It does not prove strict paper-equivalent
  feasibility, make a canonical controller change, accept a replacement
  orientation gate, close failed cells, prove robustness, calibrate contact
  geometry, establish hardware readiness, or authorize hardware
  motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `168 passed in 7.11s`; `git diff --check` passed.
  Branch push was verified at
  `98a6b3400901680ae2aeb51f9348963504606d9f`.
- Next step:
  Without live approval, continue only non-final offline work. The next strict
  feasibility branch should change the Stage A formulation beyond the current
  instantaneous weighted or two-level velocity allocation, specifically to
  constrain x/y while restoring force-normal orientation without setup qdot
  saturation.

## 2026-05-25 v114 Strict Command-Limited Stage A Probe

### Test command-limited Stage A before velocity allocation

- Branch:
  `exp/tase-ur10e-v114-strict-command-limited-stage-a`
- Runs:
  - `runs/strict_command_limited_stage_a/20260525T074557`
- Report:
  `reports/strict_command_limited_stage_a_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_command_limited_stage_a.py`
  - `scripts/run_tests.sh tests/test_strict_command_limited_stage_a.py`
  - `python3 scripts/audit_strict_command_limited_stage_a.py --output-dir runs/strict_command_limited_stage_a/20260525T074557`
  - `rg -n "&id|\*id" runs/strict_command_limited_stage_a/20260525T074557/metrics.yaml`
  - `find runs/strict_command_limited_stage_a/20260525T074557 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline command-limited probe changes Stage A command generation before
  allocation by lowering finite-time force gain, capping force-normal angular
  commands, and extending setup durations. It reports strict setup-chain pass
  `0 / 4`, trajectory feasibility pass `2 / 4`, and planned
  setup-then-trajectory pass `0 / 4`. All four rows still fail final x/y,
  setup qdot saturation, and setup tail qdot utilization. The best orientation
  row reaches `0.0003898438945537693 rad` but still has x/y error
  `0.008476991494629436 m` and setup qdot saturation `1.0`.
- Limit:
  This is offline simulation only. It does not prove strict paper-equivalent
  feasibility, make a canonical controller change, accept a replacement
  orientation gate, close failed cells, prove robustness, calibrate contact
  geometry, establish hardware readiness, or authorize hardware
  motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `171 passed in 7.16s`; `git diff --check`
  passed. Branch push was verified at `aaa42097f6778cc0b2c8617c9ffc21f57b5fbfb4`.
- Next step:
  Without live approval, continue only non-final offline work. The next strict
  feasibility branch should stop treating Stage A as a command-limited
  instantaneous velocity problem and test an explicit path or terminal
  constraint formulation.

## 2026-05-25 v115 Explicit Stage A Constraint Probe

### Test terminal/path constraints with qdot-timed setup paths

- Branch:
  `exp/tase-ur10e-v115-explicit-stage-a-constraint-probe`
- Runs:
  - `runs/explicit_stage_a_constraint_probe/20260525T082500`
- Report:
  `reports/explicit_stage_a_constraint_probe_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_explicit_stage_a_constraint_probe.py`
  - `scripts/run_tests.sh tests/test_explicit_stage_a_constraint_probe.py`
  - `python3 scripts/audit_explicit_stage_a_constraint_probe.py --output-dir runs/explicit_stage_a_constraint_probe/20260525T082500`
  - `rg -n "&id|\*id" runs/explicit_stage_a_constraint_probe/20260525T082500/metrics.yaml`
  - `find runs/explicit_stage_a_constraint_probe/20260525T082500 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline explicit-constraint probe uses the v56 contact-manifold terminal
  cases plus the v62 diagnostic contact-path tracking reference. It reports
  strict setup-path pass `0 / 5`, terminal strict-criteria pass `0 / 5`,
  qdot-criteria pass `5 / 5`, and planned setup-then-trajectory pass `0 / 5`.
  Qdot-timed paths remove setup qdot saturation in all rows, but strict
  terminal compatibility remains blocked: x/y plus force fails orientation,
  x/y plus orientation loses target contact/force, force plus orientation
  drifts in x/y, and the best soft strict compromise still fails x/y and
  orientation.
- Limit:
  This is offline simulation only. It does not prove strict paper-equivalent
  feasibility, run a Stage B trajectory, make a canonical controller change,
  accept a replacement orientation gate, close failed cells, prove robustness,
  calibrate contact geometry, establish hardware readiness, or authorize
  hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `174 passed in 7.12s`; `git diff --check`
  passed. Branch push was verified at `315052286c42300dc9cf1665aec8a7b9279587bf`.
- Next step:
  Without live approval, continue only non-final offline work. The strict
  terminal compatibility blocker remains even when qdot saturation is removed
  by explicit timing, so the next offline step should either test a stronger
  constrained optimization over the accepted contact model or wait for
  approved read-only calibration evidence that can justify changing the setup
  target/contact model.

## 2026-05-25 v116 Strict Terminal Constrained Optimization

### Test stronger terminal minimax optimization over the accepted contact model

- Branch:
  `exp/tase-ur10e-v116-strict-terminal-constrained-optimization`
- Runs:
  - `runs/strict_terminal_constrained_optimization/20260525T085000`
- Report:
  `reports/strict_terminal_constrained_optimization_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_terminal_constrained_optimization.py`
  - `scripts/run_tests.sh tests/test_strict_terminal_constrained_optimization.py`
  - `python3 scripts/audit_strict_terminal_constrained_optimization.py --output-dir runs/strict_terminal_constrained_optimization/20260525T085000`
  - `rg -n "&id|\*id" runs/strict_terminal_constrained_optimization/20260525T085000/metrics.yaml`
  - `find runs/strict_terminal_constrained_optimization/20260525T085000 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline strict terminal optimization audit seeds from the v56
  contact-manifold candidates and runs bounded smooth-minimax SLSQP/L-BFGS-B
  optimizers over normalized force, x/y, and orientation errors. It reports
  strict terminal pass `0 / 12`, optimizer success `10 / 12`, best case
  `xy_force_orientation__best_candidate__slsqp`, and improves the v56 strict
  best max-gate ratio from `2.413534442118322` to `2.11994927622362`. The best
  target-contacting row still fails force, x/y, and orientation thresholds.
- Limit:
  This is offline simulation only. It does not prove strict paper-equivalent
  feasibility, run a Stage A controller, run a Stage B trajectory, make a
  canonical controller change, accept a replacement orientation gate, close
  failed cells, prove robustness, calibrate contact geometry, establish
  hardware readiness, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `4 passed in 0.12s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `178 passed in 7.16s`; `git diff --check`
  passed. Branch push was verified at `b956ee36c659fb01bc23fc7d3db3e66bed9e8077`.
- Next step:
  Without live approval, continue only non-final offline work. Avoid repeating
  v113-v116 policy, command-limiting, timing, and terminal minimax matrices
  over the same accepted model. The practical next blocker is approved
  read-only calibration evidence or a new explicitly accepted contact/setup
  target definition.

## 2026-05-25 v117 Contact Setup Target Acceptance Review Scaffold

### Add a non-default review path for contact/setup-target changes

- Branch:
  `exp/tase-ur10e-v117-contact-setup-target-review-scaffold`
- Runs:
  - `runs/contact_setup_target_acceptance_review/20260525T091500`
  - `runs/contact_setup_target_acceptance_review_audit/20260525T091501`
- Report:
  `reports/contact_setup_target_acceptance_review_template_report.md`
- Commands run:
  - `python3 -m py_compile scripts/create_contact_setup_target_acceptance_review.py scripts/audit_contact_setup_target_acceptance_review.py`
  - `scripts/run_tests.sh tests/test_contact_setup_target_acceptance_review_template.py`
  - `python3 scripts/create_contact_setup_target_acceptance_review.py --review-id 20260525T091500`
  - `python3 scripts/audit_contact_setup_target_acceptance_review.py runs/contact_setup_target_acceptance_review/20260525T091500 --run-id 20260525T091501`
  - `rg -n "&id|\*id" runs/contact_setup_target_acceptance_review/20260525T091500/metrics.yaml runs/contact_setup_target_acceptance_review_audit/20260525T091501/metrics.yaml`
  - `find runs/contact_setup_target_acceptance_review/20260525T091500 runs/contact_setup_target_acceptance_review_audit/20260525T091501 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline scaffold creates a separate contact/setup-target acceptance
  review path. The generated review records
  `review_scaffold_not_executed`, cites the v116 strict terminal optimization
  metrics, preserves `strict_terminal_pass_count = 0`, keeps
  `contact_setup_target_acceptance.decision = not_accepted`, and keeps support
  for contact-model update, setup-target update, force-source update, gate
  relaxation, hardware claim, contact calibration, hardware readiness, and goal
  completion false. The audit passed with `violations = []`.
- Limit:
  This is offline scaffold/audit work only. It does not collect live
  measurements, execute the read-only SOP, accept a contact model, accept a
  setup target, relax a gate, calibrate contact geometry, prove strict
  paper-equivalent feasibility, establish hardware readiness, or authorize
  hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.35s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `181 passed in 7.50s`; `git diff --check`
  passed. Branch push was verified at
  `f89b1dc4be31b213a28b493a277137c14e1977a0`.
- Next step:
  Without live approval, continue only non-final offline work. The top
  practical blocker remains approved read-only calibration evidence. If future
  evidence is collected, use this separate review scaffold before accepting any
  contact model or setup-target definition change.

## 2026-05-25 v118 Post-V117 Evidence Readiness Audit

### Scan actual current evidence before any completion claim

- Branch:
  `exp/tase-ur10e-v118-post-v117-evidence-readiness-audit`
- Runs:
  - `runs/post_v117_evidence_readiness/20260525T092500`
- Report:
  `reports/post_v117_evidence_readiness_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_post_v117_evidence_readiness.py`
  - `scripts/run_tests.sh tests/test_post_v117_evidence_readiness.py`
  - `python3 scripts/audit_post_v117_evidence_readiness.py --run-id 20260525T092500`
  - `rg -n "&id|\*id" runs/post_v117_evidence_readiness/20260525T092500/metrics.yaml`
  - `find runs/post_v117_evidence_readiness/20260525T092500 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  The offline audit scans current read-only measurement runs, read-only run
  audits, orientation-gate reviews, contact/setup-target reviews, strict
  terminal metrics, robustness restatement metrics, and the hardware gate
  report path. It reports `overall_goal_complete = false`,
  `completion_claim_allowed = false`, approved read-only runs `0`, passed
  approved-read-only audits `0`, accepted orientation reviews `0`, accepted
  contact/setup-target reviews `0`, strict terminal pass `0`, closed robustness
  cells `0`, no hardware gate report, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline bookkeeping only. It does not collect live measurements,
  execute the read-only SOP, accept a contact model, accept a setup target,
  relax a gate, calibrate contact geometry, prove strict paper-equivalent
  feasibility, establish hardware readiness, or authorize hardware
  motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.24s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `184 passed in 7.74s`; `git diff --check`
  passed. Branch push was verified at
  `a11668032fb01accde9ed55aaaf95c04b5465075`.
- Next step:
  The top blocker remains explicit approval for a safe read-only calibration
  measurement step. Without approval, continue only non-final offline work and
  avoid repeating v113-v116 policy, timing, seed, and terminal-objective
  families over the same accepted model.

## 2026-05-25 v119 Read-Only SOP Step Registry Finalizer Guard

### Require exact registered read-only step IDs before finalization

- Branch:
  `exp/tase-ur10e-v119-readonly-step-registry-finalizer-guard`
- Runs:
  - `runs/read_only_sop_step_registry_audit/20260525T094000`
- Report:
  `reports/read_only_sop_step_registry_guard_report.md`
- Commands run:
  - `python3 -m py_compile scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_read_only_calibration_measurement_run.py scripts/audit_read_only_sop_step_registry.py scripts/create_read_only_calibration_measurement_run.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py`
  - `python3 scripts/audit_read_only_sop_step_registry.py --run-id 20260525T094000`
  - `rg -n "&id|\*id" runs/read_only_sop_step_registry_audit/20260525T094000/metrics.yaml`
  - `find runs/read_only_sop_step_registry_audit/20260525T094000 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  V119 adds `configs/read_only_sop_step_registry.yaml`, audits the registry,
  and updates the read-only finalizer/auditor. The registry has `6` exact
  steps, `5` finalizer-eligible evidence steps, `violations = []`, and all
  registry authorization/acceptance/readiness flags false. Finalization now
  rejects unknown step IDs, non-finalizer step IDs, and worksheet rows outside
  the approved step scope.
- Limit:
  This is offline approval-scoping work only. It does not collect live
  measurements, execute the read-only SOP, accept a contact model, accept a
  setup target, relax a gate, calibrate contact geometry, prove strict
  paper-equivalent feasibility, establish hardware readiness, or authorize
  hardware motion/configuration.
- Validation:
  Focused tests passed with `12 passed in 2.34s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `188 passed in 8.24s`; `git diff --check`
  passed. Branch push was verified at
  `c1c8febca4a41009d1fb8b55e19cfbe64931c17b`.
- Next step:
  The top blocker remains explicit approval for one registered read-only SOP
  step. Without approval, continue only non-final offline work and keep all
  contact/setup-target, orientation-gate, robustness, strict-feasibility, and
  hardware-readiness claims false.

## 2026-05-25 v120 Read-Only Step Approval Packet

### Create a not-approved exact-step packet for phase1 TCP/contact evidence

- Branch:
  `exp/tase-ur10e-v120-readonly-step-approval-packet`
- Runs:
  - `runs/read_only_step_approval_packet/20260525T095500`
  - `runs/read_only_step_approval_packet_audit/20260525T095501`
- Report:
  `reports/read_only_step_approval_packet_report.md`
- Commands run:
  - `python3 -m py_compile scripts/create_read_only_step_approval_packet.py scripts/audit_read_only_step_approval_packet.py`
  - `scripts/run_tests.sh tests/test_read_only_step_approval_packet.py`
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase1_mounted_stack_tcp_contact_measurement --packet-id 20260525T095500`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T095500 --run-id 20260525T095501`
  - `rg -n "&id|\*id" runs/read_only_step_approval_packet/20260525T095500/metrics.yaml runs/read_only_step_approval_packet_audit/20260525T095501/metrics.yaml`
  - `find runs/read_only_step_approval_packet/20260525T095500 runs/read_only_step_approval_packet_audit/20260525T095501 -type f \( -name '*.npz' -o -name '*.npy' -o -name '*.mat' -o -name '*.tar' -o -name '*.gz' -o -name '*.zip' \) -print`
- Result:
  V120 creates an exact-step approval packet for
  `phase1_mounted_stack_tcp_contact_measurement`. The packet is
  `approval_packet_created_not_approved`, allows only
  `tcp_contact_measurements.csv`, records the required confirmation phrase,
  and keeps `packet_authorizes_execution = false`,
  `packet_authorizes_live_access = false`, execution flags false,
  hardware-readiness false, and `do_not_mark_goal_complete = true`. The audit
  passed with `violations = []`.
- Limit:
  This is offline approval-scoping work only. It does not collect live
  measurements, execute the read-only SOP, accept a contact model, accept a
  setup target, relax a gate, calibrate contact geometry, prove strict
  paper-equivalent feasibility, establish hardware readiness, or authorize
  hardware motion/configuration.
- Validation:
  Focused tests passed with `4 passed in 0.32s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `192 passed in 8.56s`; `git diff --check`
  passed. Branch push was verified at
  `c897dfa467b823c8cf6fc68b54f290a29942a704`.
- Next step:
  The top blocker remains explicit approval for one exact read-only SOP step.
  This packet is not approval. If the user approves the packet later, use a
  fresh read-only run and fill only `tcp_contact_measurements.csv`.

## 2026-05-25 v121 Read-Only Approval Packet Coverage

### Cover every finalizer-eligible registered step with not-approved packets

- Branch:
  `exp/tase-ur10e-v121-readonly-approval-packet-coverage`
- Implementation commit:
  `5cd3b3d8d4bb8672a8c74ba5832439c3faba7c7a`
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
  `reports/read_only_step_approval_packet_coverage_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_step_approval_packet_coverage.py`
  - `scripts/run_tests.sh tests/test_read_only_step_approval_packet_coverage.py`
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase2_ksm_contact_patch_convention --packet-id 20260525T100000`
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase3_plane_normal_external_measurement --packet-id 20260525T100100`
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase4_force_source_read_only_comparison --packet-id 20260525T100200`
  - `python3 scripts/create_read_only_step_approval_packet.py --step-id phase5_orientation_gate_semantics_evidence --packet-id 20260525T100300`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T100000 --run-id 20260525T100001`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T100100 --run-id 20260525T100101`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T100200 --run-id 20260525T100201`
  - `python3 scripts/audit_read_only_step_approval_packet.py runs/read_only_step_approval_packet/20260525T100300 --run-id 20260525T100301`
  - `python3 scripts/audit_read_only_step_approval_packet_coverage.py --run-id 20260525T100500`
- Result:
  V121 adds an aggregate packet coverage audit and creates not-approved
  packets for phases 2 through 5. Together with the v120 phase1 packet, the
  coverage audit reports `audit_passed = true`, `coverage_complete = true`,
  finalizer step coverage `5 / 5`, `missing_step_ids = []`, approved packets
  `0`, execution-authorizing packets `0`, live-access-authorizing packets
  `0`, heavy payloads `[]`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline approval-scoping work only. It does not collect live
  measurements, execute the read-only SOP, accept a contact model, accept a
  setup target, relax a gate, calibrate contact geometry, prove strict
  paper-equivalent feasibility, establish hardware readiness, or authorize
  hardware motion/configuration.
- Validation:
  Focused packet tests passed with `7 passed in 1.60s`; YAML anchor check
  found no anchors in the generated metrics; raw/heavy artifact scan found no
  payloads; full tests passed with `195 passed in 9.83s`; `git diff --check`
  passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and keep all claim-closing
  flags false.

## 2026-05-25 v122 Read-Only Step Execution Preflight

### Verify the offline packet-to-finalizer command path without approval

- Branch:
  `exp/tase-ur10e-v122-readonly-execution-preflight`
- Implementation commit:
  `8e3008f5c723444ce95716cd968012d6150d122e`
- Runs:
  - `runs/read_only_step_execution_preflight/20260525T101000`
- Report:
  `reports/read_only_step_execution_preflight_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_step_execution_preflight.py`
  - `scripts/run_tests.sh tests/test_read_only_step_execution_preflight.py`
  - `python3 scripts/audit_read_only_step_execution_preflight.py --run-id 20260525T101000`
- Result:
  V122 adds an offline preflight audit for the exact-step path from audited
  not-approved packet to future scaffold, finalizer, and approved-read-only
  audit. The run reports `audit_passed = true`, finalizer step preflight
  readiness `5 / 5`, `missing_ready_step_ids = []`, approved packets `0`,
  execution-authorizing packets `0`, live-access-authorizing packets `0`,
  `explicit_user_approval_required = true`,
  `preflight_authorizes_live_access = false`,
  `preflight_authorizes_execution = false`,
  `approved_read_only_evidence_created = false`, heavy payloads `[]`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline command-path readiness only. It does not approve a packet,
  instantiate an approved evidence run, collect live measurements, execute the
  read-only SOP, accept a contact model, accept a setup target, relax a gate,
  calibrate contact geometry, prove strict paper-equivalent feasibility,
  establish hardware readiness, or authorize hardware motion/configuration.
- Validation:
  Focused coverage/preflight tests passed with `6 passed in 2.02s`; YAML
  anchor check found no anchors in the generated metrics; raw/heavy artifact
  scan found no payloads; full tests passed with `198 passed in 10.52s`;
  `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and keep all claim-closing
  flags false.

## 2026-05-25 v123 Post-V122 Completion Gate

### Treat packet coverage and preflight as non-evidence readiness artifacts

- Branch:
  `exp/tase-ur10e-v123-post-v122-completion-gate`
- Implementation commit:
  `ae2abb566b12dbc348a0675babe8f33f08c608bc`
- Runs:
  - `runs/post_v122_completion_gate/20260525T102000`
- Report:
  `reports/post_v122_completion_gate_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_post_v122_completion_gate.py`
  - `scripts/run_tests.sh tests/test_post_v122_completion_gate.py`
  - `python3 scripts/audit_post_v122_completion_gate.py --run-id 20260525T102000`
- Result:
  V123 adds a current-state completion gate over the real evidence paths plus
  the v120-v122 readiness artifacts. It reports `audit_passed = true`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`,
  `do_not_mark_goal_complete = true`, top blocker
  `approved_read_only_calibration_evidence`, approved read-only evidence runs
  `0`, passed approved-read-only audits `0`, accepted orientation reviews `0`,
  accepted contact/setup-target reviews `0`, strict terminal pass count `0`,
  closed robustness cells `0`, no hardware gate report, and
  `readiness_artifacts_are_non_evidence = true`.
- Limit:
  This is offline completion bookkeeping only. It does not approve a packet,
  create approved read-only evidence, collect live measurements, execute the
  read-only SOP, accept a contact model, accept a setup target, relax a gate,
  calibrate contact geometry, prove strict paper-equivalent feasibility,
  establish hardware readiness, or authorize hardware motion/configuration.
- Validation:
  Focused tests passed with `3 passed in 0.28s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `201 passed in 10.89s`; `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and keep packet/preflight
  readiness separate from evidence.

## 2026-05-25 v124 Paper-Platform Claim Boundary Regression

### Guard the split formula-convergence and tuned Fig.6 evidence lines

- Branch:
  `exp/tase-ur10e-v124-paper-platform-claim-boundary-regression`
- Implementation commit:
  `e7e1f89849dfd8827123bf74cc02201f7cd1332c`
- Runs:
  - `runs/paper_platform_claim_boundary/20260525T103000`
- Report:
  `reports/paper_platform_claim_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_paper_platform_claim_boundary.py`
  - `scripts/run_tests.sh tests/test_paper_platform_claim_boundary.py`
  - `python3 scripts/audit_paper_platform_claim_boundary.py --run-id 20260525T103000`
- Result:
  V124 adds an offline paper-platform claim-boundary regression audit. The
  run reports `audit_passed = true`,
  `formula_convergence_claim_allowed = true`,
  `tuned_figure_match_claim_allowed = true`,
  `strict_paper_equivalent_claim_allowed = false`,
  `claim_lines_collapsed = false`, `claim_boundary_preserved = true`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline paper-platform bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, accept a contact model, accept
  a setup target, prove strict paper-equivalent feasibility, prove robustness,
  establish hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.17s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `205 passed in 10.96s`; `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and keep formula-convergence,
  tuned Fig.6, and strict paper-equivalent paper-platform claims separate.

## 2026-05-25 v125 Strict Terminal Tradeoff Boundary

### Audit existing v116 rows for force/x-y/orientation tradeoff behavior

- Branch:
  `exp/tase-ur10e-v125-strict-terminal-tradeoff-boundary`
- Implementation commit:
  `a41aada3a50bd59d57652b1ec7dffe2a81d4bde7`
- Runs:
  - `runs/strict_terminal_tradeoff_boundary/20260525T104000`
- Report:
  `reports/strict_terminal_tradeoff_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_terminal_tradeoff_boundary.py`
  - `scripts/run_tests.sh tests/test_strict_terminal_tradeoff_boundary.py`
  - `python3 scripts/audit_strict_terminal_tradeoff_boundary.py --run-id 20260525T104000`
- Result:
  V125 adds a post-hoc offline audit over the existing v116 strict-terminal
  optimization rows. The run reports `audit_passed = true`,
  `strict_terminal_pass_count = 0`, `optimization_case_count = 12`,
  `best_combined_case_id = xy_force_orientation__best_candidate__slsqp`,
  `best_combined_max_gate_ratio = 2.11994927622362`,
  `best_combined_failed_all_three_scalar_gates = true`,
  `force_xy_without_orientation_count = 1`,
  `xy_orientation_without_force_or_contact_count = 2`,
  `tradeoff_boundary_preserved = true`, `new_optimization_run = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline bookkeeping over existing v116 rows only. It does not run a
  new optimizer, collect live measurements, approve any read-only SOP step,
  accept a contact model, accept a setup target, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 0.24s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `208 passed in 11.32s`; `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and do not repeat the v116
  bounded minimax optimizer over the same accepted contact model and seeds as
  a likely closer.

## 2026-05-25 v126 Strict Terminal Relaxation Budget

### Quantify non-accepted scalar gate budgets from existing strict rows

- Branch:
  `exp/tase-ur10e-v126-strict-terminal-relaxation-budget`
- Implementation commit:
  `7ba52057c82f19037916879880af322e8a7132ba`
- Runs:
  - `runs/strict_terminal_relaxation_budget/20260525T105000`
- Report:
  `reports/strict_terminal_relaxation_budget_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_terminal_relaxation_budget.py`
  - `scripts/run_tests.sh tests/test_strict_terminal_relaxation_budget.py`
  - `python3 scripts/audit_strict_terminal_relaxation_budget.py --run-id 20260525T105000`
- Result:
  V126 adds a post-hoc offline budget audit over the existing v116/v125
  strict-terminal rows. The run reports `audit_passed = true`,
  `strict_terminal_pass_count = 0`,
  `minimum_uniform_multiplier = 2.11994927622362`,
  `minimum_uniform_requires_all_three_scalar_gates = true`,
  `orientation_only_multiplier = 4.899002392744376`,
  `contactless_xy_orientation_row_count = 2`,
  `relaxation_budget_acceptance_allowed = false`,
  `new_optimization_run = false`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline bookkeeping over existing rows only. It does not run a new
  optimizer, collect live measurements, approve any read-only SOP step, accept
  a contact model, accept a setup target, relax a gate, prove strict
  paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 0.28s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `211 passed in 11.65s`; `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and do not accept any
  strict-terminal relaxation from this budget audit.

## 2026-05-25 v127 Read-Only Evidence Dependency Map

### Map unresolved evidence blockers to exact registered read-only steps

- Branch:
  `exp/tase-ur10e-v127-readonly-evidence-dependency-map`
- Implementation commit:
  `9b494221728e1ff461fc5f6d6c13381a5f3c12f4`
- Runs:
  - `runs/read_only_evidence_dependency_map/20260525T110000`
- Report:
  `reports/read_only_evidence_dependency_map_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_evidence_dependency_map.py`
  - `scripts/run_tests.sh tests/test_read_only_evidence_dependency_map.py`
  - `python3 scripts/audit_read_only_evidence_dependency_map.py --run-id 20260525T110000`
- Result:
  V127 adds an offline dependency-map audit from the five unresolved
  measured-geometry readiness checks to exact registered read-only SOP
  finalizer steps and worksheets. The run reports `audit_passed = true`,
  `dependency_map_complete = true`, mapped readiness checks `5 / 5`, mapped
  finalizer steps `5 / 5`, packet-covered steps `5 / 5`, preflight-ready
  steps `5 / 5`, approved packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`,
  `approved_read_only_evidence_created = false`,
  `explicit_user_approval_required = true`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline readiness bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 0.21s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `214 passed in 11.67s`; `git diff --check` passed.
- Next step:
  The top blocker remains explicit user approval for one exact registered
  read-only SOP step before any live read-only evidence collection. Without
  approval, continue only non-final offline work and keep the v127 dependency
  map separate from approved evidence.

## 2026-05-25 v128 Read-Only Next-Step Selection

### Select the first exact read-only approval candidate without authorizing it

- Branch:
  `exp/tase-ur10e-v128-readonly-next-step-selection`
- Implementation commit:
  `51793eae7f878f9e6bb721216e2c1820ea178375`
- Runs:
  - `runs/read_only_next_step_selection/20260525T111000`
- Report:
  `reports/read_only_next_step_selection_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_next_step_selection.py`
  - `scripts/run_tests.sh tests/test_read_only_next_step_selection.py`
  - `python3 scripts/audit_read_only_next_step_selection.py --run-id 20260525T111000`
- Result:
  V128 adds an offline selector over the v127 dependency map. The run reports
  `audit_passed = true`, `selection_plan_complete = true`, candidate steps
  `5`, first candidate
  `phase1_mounted_stack_tcp_contact_measurement`, first worksheet
  `tcp_contact_measurements.csv`, required phrase
  `I approve this read-only measurement step`, exact step ID required true,
  approved packets `0`, execution-authorizing packets `0`,
  live-access-authorizing packets `0`,
  `approved_read_only_evidence_created = false`,
  `selection_authorizes_execution = false`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline selection bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 0.13s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `217 passed in 11.80s`; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, the first exact step to name is
  `phase1_mounted_stack_tcp_contact_measurement`. Without approval, continue
  only non-final offline work and keep the v128 selector separate from
  approved evidence.

## 2026-05-25 v129 Read-Only Phase1 Approval Request Freeze

### Freeze the selected phase1 packet request without approving it

- Branch:
  `exp/tase-ur10e-v129-readonly-phase1-approval-request-freeze`
- Implementation commit:
  `4bf07b2373af781eb35b20d13862afd9c5330907`
- Runs:
  - `runs/read_only_phase1_approval_request_freeze/20260525T112000`
- Report:
  `reports/read_only_phase1_approval_request_freeze_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_phase1_approval_request_freeze.py`
  - `scripts/run_tests.sh tests/test_read_only_phase1_approval_request_freeze.py`
  - `python3 scripts/audit_read_only_phase1_approval_request_freeze.py --run-id 20260525T112000`
- Result:
  V129 adds an offline freeze audit for the v128 first candidate approval
  request. The run reports `audit_passed = true`,
  `approval_request_freeze_complete = true`, frozen step
  `phase1_mounted_stack_tcp_contact_measurement`, frozen worksheet
  `tcp_contact_measurements.csv`, required phrase
  `I approve this read-only measurement step`, packet Markdown SHA256
  `91d27eac0d13b988d989353614b0400e1149092af9a631b91f18794d9cdbe93d`,
  packet status `approval_packet_created_not_approved`, packet audit passed
  true, packet approval status `not_approved`,
  `freeze_authorizes_execution = false`,
  `approved_read_only_evidence_created = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline approval-request bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 0.11s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `220 passed in 11.97s`; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, use the frozen phase1 request and
  still create a fresh scaffold, finalize with the exact registered step ID,
  and audit in approved-read-only mode. Without approval, continue only
  non-final offline work.

## 2026-05-25 v130 Read-Only Phase1 Preapproval Finalizer Guard

### Verify phase1 misuse paths reject before evidence creation

- Branch:
  `exp/tase-ur10e-v130-phase1-preapproval-finalizer-guard`
- Implementation commit:
  `292512d7d05eaeea0631fc971a05ce81250d06e2`
- Runs:
  - `runs/read_only_phase1_preapproval_finalizer_guard/20260525T113000`
- Report:
  `reports/read_only_phase1_preapproval_finalizer_guard_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_phase1_preapproval_finalizer_guard.py`
  - `scripts/run_tests.sh tests/test_read_only_phase1_preapproval_finalizer_guard.py`
  - `python3 scripts/audit_read_only_phase1_preapproval_finalizer_guard.py --run-id 20260525T113000`
- Result:
  V130 adds an offline preapproval finalizer guard for the frozen phase1 path.
  The run reports `audit_passed = true`,
  `preapproval_finalizer_guard_complete = true`, case count `5`, rejected
  cases `5`, scaffold-preserved cases `5`,
  `approved_read_only_evidence_created_count = 0`,
  `successful_finalization_count = 0`,
  `repository_evidence_run_created = false`, `temp_only_dry_run = true`,
  `guard_authorizes_execution = false`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline preapproval guard bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `3 passed in 3.21s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `223 passed in 15.10s`; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, use the frozen phase1 request and
  still create a fresh scaffold, finalize with the exact registered step ID,
  and audit in approved-read-only mode. Without approval, continue only
  non-final offline work.

## 2026-05-25 v131 Phase1 Approved Evidence Acceptance Boundary

### Scan current evidence directories after v130 without approving phase1

- Branch:
  `exp/tase-ur10e-v131-phase1-evidence-acceptance-boundary`
- Implementation commit:
  `54ce004acb9e1f82cf31daed0e6ddbb9a308dbfc`
- Runs:
  - `runs/phase1_approved_evidence_acceptance_boundary/20260525T114000`
- Report:
  `reports/phase1_approved_evidence_acceptance_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_phase1_approved_evidence_acceptance_boundary.py`
  - `scripts/run_tests.sh tests/test_phase1_approved_evidence_acceptance_boundary.py`
  - `python3 scripts/audit_phase1_approved_evidence_acceptance_boundary.py --run-id 20260525T114000`
- Result:
  V131 adds an offline acceptance-boundary audit for the frozen phase1 path.
  It cross-checks v127-v130 and scans the current read-only evidence
  directories. The run reports `audit_passed = true`,
  `phase1_acceptance_boundary_complete = true`,
  `current_repository_scan_finds_no_approved_evidence = true`, read-only runs
  `3`, read-only audits `4`, approved read-only runs `0`, phase1 approved
  read-only runs `0`, finalization records `0`, passed approved-read-only
  audits `0`, `guard_rejected_case_count = 5`,
  `guard_approved_evidence_created_count = 0`,
  `approved_read_only_evidence_created = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline acceptance-boundary bookkeeping only. It does not collect
  live measurements, approve any read-only SOP step, create approved
  calibration evidence, accept a contact model, accept a setup target, relax a
  gate, prove strict paper-equivalent feasibility, prove robustness, establish
  hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.25s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `227 passed in 15.56s`; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, use the frozen phase1 request and
  still create a fresh scaffold, finalize with the exact registered step ID,
  and audit in approved-read-only mode. Without approval, continue only
  non-final offline work.

## 2026-05-25 v132 Read-Only Evidence Sequence Boundary

### Freeze the full read-only evidence sequence without bundling approval

- Branch:
  `exp/tase-ur10e-v132-readonly-sequence-boundary`
- Implementation commit:
  `23fdb09504792e1f9b1add0dcf607c6cccc3b7fa`
- Runs:
  - `runs/read_only_evidence_sequence_boundary/20260525T115000`
- Report:
  `reports/read_only_evidence_sequence_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_evidence_sequence_boundary.py`
  - `scripts/run_tests.sh tests/test_read_only_evidence_sequence_boundary.py`
  - `python3 scripts/audit_read_only_evidence_sequence_boundary.py --run-id 20260525T115000`
- Result:
  V132 adds an offline sequence-boundary audit over the v127 dependency map,
  v128 selector, and v131 evidence scan. The run reports
  `audit_passed = true`, `sequence_boundary_complete = true`, ordered step
  count `5`, first step `phase1_mounted_stack_tcp_contact_measurement`, first
  worksheet `tcp_contact_measurements.csv`, remaining steps after phase1 `4`,
  all steps packet-covered true, all steps preflight-ready true, all steps
  separate approval required true,
  `phase1_alone_completes_measured_geometry_chain = false`,
  `phase1_alone_completes_overall_goal = false`, current approved read-only
  runs `0`, current phase1 approved runs `0`, finalization records `0`,
  passed approved-read-only audits `0`, approved packets `0`,
  execution-authorizing packets `0`, live-access-authorizing packets `0`,
  `bundle_approval_authorized = false`,
  `approved_read_only_evidence_created = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline sequence-boundary bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.22s`; YAML anchor check found no
  anchors in the generated metrics; raw/heavy artifact scan found no payloads;
  full tests passed with `231 passed in 15.64s`; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, use only the frozen phase1
  request for phase1 and do not bundle phase2-phase5 into that approval.
  Without approval, continue only non-final offline work.

## 2026-05-25 v133 Phase1 Row-Quality Guard

### Reject malformed phase1 TCP/contact rows before finalization

- Branch:
  `exp/tase-ur10e-v133-phase1-row-quality-guard`
- Implementation commit:
  `329bff1605c3a20ed0f9b53b08493f364d887f32`
- Runs:
  - `runs/phase1_row_quality_guard/20260525T120000`
- Report:
  `reports/phase1_row_quality_guard_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_phase1_row_quality_guard.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_phase1_row_quality_guard.py`
  - `python3 scripts/audit_phase1_row_quality_guard.py --run-id 20260525T120000`
- Result:
  V133 adds an offline row-quality guard for the selected phase1 path. It
  extends the read-only run auditor and finalizer so malformed
  `tcp_contact_measurements.csv` rows reject before approved evidence can be
  written. The audit run reports `audit_passed = true`,
  `phase1_row_quality_guard_complete = true`, case count `5`, rejected cases
  `5`, scaffold-preserved cases `5`,
  `approved_read_only_evidence_created_count = 0`,
  `repository_evidence_run_created = false`, `temp_only_dry_run = true`,
  guarded step `phase1_mounted_stack_tcp_contact_measurement`, guarded
  worksheet `tcp_contact_measurements.csv`,
  `guard_authorizes_execution = false`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and `do_not_mark_goal_complete = true`.
- Limit:
  This is offline row-quality guard bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `17 passed in 6.00s`; full tests passed with
  `236 passed in 19.47s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use the frozen phase1 request,
  fill only valid `tcp_contact_measurements.csv` rows, finalize with the exact
  registered step ID, and audit in approved-read-only mode. Without approval,
  continue only non-final offline work.

## 2026-05-25 v134 Downstream Row-Quality Guard

### Reject malformed downstream read-only rows before finalization

- Branch:
  `exp/tase-ur10e-v134-downstream-row-quality-guard`
- Implementation commit:
  `cd5ef9e5a93f0523109fdbc5491e7cb523f77439`
- Runs:
  - `runs/downstream_row_quality_guard/20260525T121000`
- Report:
  `reports/downstream_row_quality_guard_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_calibration_measurement_run.py scripts/finalize_read_only_calibration_measurement_evidence.py scripts/audit_downstream_row_quality_guard.py`
  - `scripts/run_tests.sh tests/test_read_only_calibration_measurement_template.py tests/test_downstream_row_quality_guard.py`
  - `python3 scripts/audit_downstream_row_quality_guard.py --run-id 20260525T121000`
- Result:
  V134 adds an offline row-quality guard for the four registered downstream
  read-only evidence steps. It extends the read-only run auditor and finalizer
  so malformed KSM contact-patch convention, plane-normal, force-source
  comparison, and orientation-gate semantics rows reject before approved
  evidence can be written. The audit run reports `audit_passed = true`,
  `downstream_row_quality_guard_complete = true`, case count `4`, rejected
  cases `4`, scaffold-preserved cases `4`,
  `approved_read_only_evidence_created_count = 0`,
  `repository_evidence_run_created = false`, `temp_only_dry_run = true`,
  guarded downstream step count `4`, `guard_authorizes_execution = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline row-quality guard bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create approved calibration
  evidence, accept a contact model, accept a setup target, relax a gate, prove
  strict paper-equivalent feasibility, prove robustness, establish hardware
  readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `21 passed in 6.27s`; full tests passed with
  `243 passed in 23.16s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use one exact registered
  approval packet, fill only valid rows for that step's worksheet scope,
  finalize with the exact registered step ID, and audit in approved-read-only
  mode. Without approval, continue only non-final offline work.

## 2026-05-25 v135 Read-Only Finalization Rehearsal Boundary

### Rehearse the finalizer and verifier path without creating repository evidence

- Branch:
  `exp/tase-ur10e-v135-finalization-rehearsal-boundary`
- Implementation commit:
  `c891174470b9ad3ec50d9e3eab911ca5dfba2ee8`
- Runs:
  - `runs/read_only_finalization_rehearsal_boundary/20260525T122000`
- Report:
  `reports/read_only_finalization_rehearsal_boundary_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_read_only_finalization_rehearsal_boundary.py`
  - `scripts/run_tests.sh tests/test_read_only_finalization_rehearsal_boundary.py`
  - `python3 scripts/audit_read_only_finalization_rehearsal_boundary.py --run-id 20260525T122000`
- Result:
  V135 adds an offline non-persistent finalization rehearsal boundary for all
  five registered read-only finalizer steps. It creates temporary scaffolds,
  writes one valid synthetic row for exactly each step's registered worksheet,
  runs the finalizer and approved-read-only verifier in the temporary area,
  and verifies that the repository read-only evidence directories remain
  unchanged. The audit run reports `audit_passed = true`,
  `finalization_rehearsal_boundary_complete = true`, registered finalizer
  step count `5`, rehearsal passed step count `5`, temporary finalization
  count `5`, approved-read-only verifier passed count `5`, synthetic-row-only
  count `5`, live hardware accessed count `0`, temporary root removed true,
  repository approved-read-only run delta `0`, repository finalization record
  delta `0`, repository approved-read-only audit delta `0`,
  `approved_read_only_evidence_created = false`,
  `rehearsal_authorizes_execution = false`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline finalization rehearsal bookkeeping only. It does not collect
  live measurements, approve any read-only SOP step, create repository
  approved calibration evidence, accept a contact model, accept a setup target,
  relax a gate, prove strict paper-equivalent feasibility, prove robustness,
  establish hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 6.16s`; broader focused finalizer
  tests passed with `25 passed in 12.74s`; full tests passed with
  `247 passed in 29.31s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use one exact registered approval
  packet, fill only valid rows for that step's worksheet scope, finalize with
  the exact registered step ID, and audit in approved-read-only mode. Without
  approval, continue only non-final offline work.

## 2026-05-25 v136 Post-V135 Completion Gate

### Keep finalization rehearsal separate from completion evidence

- Branch:
  `exp/tase-ur10e-v136-post-rehearsal-completion-gate`
- Implementation commit:
  `b0cad5d0e3f077de805437f3a7954df73893c106`
- Runs:
  - `runs/post_v135_completion_gate/20260525T123000`
- Report:
  `reports/post_v135_completion_gate_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_post_v135_completion_gate.py`
  - `scripts/run_tests.sh tests/test_post_v135_completion_gate.py`
  - `python3 scripts/audit_post_v135_completion_gate.py --run-id 20260525T123000`
- Result:
  V136 adds an offline post-v135 completion gate. It scans the actual current
  read-only evidence, review, strict terminal, robustness, and hardware-gate
  paths, then classifies not-approved packet coverage, execution preflight,
  and finalization rehearsal as non-evidence readiness artifacts. The audit
  reports `audit_passed = true`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, `do_not_mark_goal_complete = true`,
  top blocker `approved_read_only_calibration_evidence`, approved read-only
  runs `0`, passed approved-read-only audits `0`, accepted orientation reviews
  `0`, accepted contact/setup-target reviews `0`, strict terminal pass count
  `0`, closed robustness cells `0`, hardware gate report false, readiness
  artifact count `3`, `readiness_completion_evidence_ids = []`,
  `readiness_artifacts_are_non_evidence = true`, and
  `finalization_rehearsal_is_non_evidence = true`.
- Limit:
  This is offline completion-gate bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create repository approved
  calibration evidence, accept a contact model, accept a setup target, relax a
  gate, prove strict paper-equivalent feasibility, prove robustness, establish
  hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.45s`; compatibility focused gate
  tests passed with `10 passed in 0.95s`; full tests passed with
  `251 passed in 29.98s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use one exact registered approval
  packet, fill only valid rows for that step's worksheet scope, finalize with
  the exact registered step ID, and audit in approved-read-only mode. Without
  approval, continue only non-final offline work.

## 2026-05-25 v137 Strict Vs Diagnostic Margin Separation

### Keep diagnostic orientation margin separate from strict feasibility

- Branch:
  `exp/tase-ur10e-v137-strict-diagnostic-margin-separation`
- Implementation commit:
  `b1567daef58ec7e7a034f0532fefea4bdc430400`
- Runs:
  - `runs/strict_vs_diagnostic_margin_separation/20260525T124000`
- Report:
  `reports/strict_vs_diagnostic_margin_separation_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_strict_vs_diagnostic_margin_separation.py`
  - `scripts/run_tests.sh tests/test_strict_vs_diagnostic_margin_separation.py`
  - `python3 scripts/audit_strict_vs_diagnostic_margin_separation.py --run-id 20260525T124000`
- Result:
  V137 adds an offline post-hoc scale-separation audit over the existing v85,
  v126, and v136 metrics. It confirms that the v85 diagnostic
  orientation/contact definition margin is not large enough to close the v126
  strict-terminal gap. The audit reports `audit_passed = true`,
  `strict_vs_diagnostic_margin_separation_complete = true`,
  diagnostic required normal rotation `0.0005664520369604714 rad`, strict
  orientation increase `0.0335984782867086 rad`,
  strict/diagnostic orientation ratio `59.31389790209757`, minimum uniform
  multiplier `2.11994927622362`, force increase
  `0.01697482058387756 N`, tangential increase
  `0.0019405568802957048 m`,
  `minimum_uniform_requires_all_three_scalar_gates = true`,
  `v85_margin_can_close_strict_paper_equivalent_goal = false`,
  `replacement_gate_accepted = false`, approved read-only runs `0`, passed
  approved-read-only audits `0`, `overall_goal_complete = false`,
  `completion_claim_allowed = false`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is offline metrics bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create repository approved
  calibration evidence, accept a contact model, accept a setup target, relax a
  gate, prove strict paper-equivalent feasibility, prove robustness, establish
  hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.17s`; temporary verifier rerun
  completed under `/tmp/tase_v137_margin_verify`; full tests passed with
  `255 passed in 29.95s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use one exact registered approval
  packet, fill only valid rows for that step's worksheet scope, finalize with
  the exact registered step ID, and audit in approved-read-only mode. Without
  approval, continue only non-final offline work that does not repeat the
  v113-v116 strict-feasibility families over the same accepted model and
  seeds.

## 2026-05-25 v138 Post-V137 Completion Gate

### Keep margin separation separate from completion evidence

- Branch:
  `exp/tase-ur10e-v138-post-margin-completion-gate`
- Implementation commit:
  `da2f7bee8a21b60b583e1824a6f7108c2e782b65`
- Runs:
  - `runs/post_v137_completion_gate/20260525T125000`
- Report:
  `reports/post_v137_completion_gate_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_post_v137_completion_gate.py`
  - `scripts/run_tests.sh tests/test_post_v137_completion_gate.py`
  - `python3 scripts/audit_post_v137_completion_gate.py --run-id 20260525T125000`
- Result:
  V138 adds an offline post-v137 completion gate. It scans the actual current
  read-only evidence, review, strict terminal, robustness, and hardware-gate
  paths, then classifies not-approved packet coverage, execution preflight,
  finalization rehearsal, and strict-vs-diagnostic margin separation as
  non-evidence readiness artifacts. The audit reports `audit_passed = true`,
  `overall_goal_complete = false`, `completion_claim_allowed = false`,
  `do_not_mark_goal_complete = true`, top blocker
  `approved_read_only_calibration_evidence`, approved read-only runs `0`,
  passed approved-read-only audits `0`, accepted orientation reviews `0`,
  accepted contact/setup-target reviews `0`, strict terminal pass count `0`,
  closed robustness cells `0`, hardware gate report false, readiness artifact
  count `4`, `readiness_completion_evidence_ids = []`,
  `readiness_artifacts_are_non_evidence = true`,
  `finalization_rehearsal_is_non_evidence = true`,
  `margin_separation_is_non_evidence = true`,
  strict/diagnostic orientation ratio `59.31389790209757`,
  `margin_v85_can_close_strict_paper_equivalent_goal = false`, and
  `margin_replacement_gate_accepted = false`.
- Limit:
  This is offline completion-gate bookkeeping only. It does not collect live
  measurements, approve any read-only SOP step, create repository approved
  calibration evidence, accept a contact model, accept a setup target, relax a
  gate, prove strict paper-equivalent feasibility, prove robustness, establish
  hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.43s`; full tests passed with
  `259 passed in 30.32s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads; `git diff --check`
  passed.
- Next step:
  If the user later gives explicit approval, use one exact registered approval
  packet, fill only valid rows for that step's worksheet scope, finalize with
  the exact registered step ID, and audit in approved-read-only mode. Without
  approval, continue only non-final offline work that does not repeat the
  v113-v116 strict-feasibility families over the same accepted model and
  seeds.

## 2026-05-25 v139 Full Reproduction Status After V138

### Answer the completion question from audited evidence

- Branch:
  `exp/tase-ur10e-v139-full-reproduction-status`
- Implementation commit:
  `7691b0dc7396fd1a8374b75e91d54908bee6c30b`
- Runs:
  - `runs/full_reproduction_status_after_v138/20260525T130000`
- Report:
  `reports/full_reproduction_status_after_v138_report.md`
- Commands run:
  - `python3 -m py_compile scripts/audit_full_reproduction_status_after_v138.py`
  - `scripts/run_tests.sh tests/test_full_reproduction_status_after_v138.py`
  - `python3 scripts/audit_full_reproduction_status_after_v138.py --run-id 20260525T130000`
- Result:
  V139 adds an offline status audit that directly answers whether the current
  repository evidence supports a full reproduction claim. The audit reports
  `audit_passed = true`, `user_question_answer = not_fully_reproduced`,
  `full_reproduction_complete = false`, `continue_required = true`,
  safe continuation mode
  `explicit_read_only_approval_or_nonfinal_offline`, top blocker
  `approved_read_only_calibration_evidence`, incomplete requirement count `6`,
  approved read-only runs `0`, passed approved-read-only audits `0`, accepted
  orientation reviews `0`, accepted contact/setup-target reviews `0`, strict
  terminal pass count `0`, closed robustness cells `0`, hardware gate report
  false, readiness completion evidence IDs `[]`, and
  `do_not_mark_goal_complete = true`.
- Limit:
  This is a status audit over existing metrics only. It does not collect live
  measurements, approve any read-only SOP step, create repository approved
  calibration evidence, accept a contact model, accept a setup target, relax a
  gate, prove strict paper-equivalent feasibility, prove robustness, establish
  hardware readiness, or authorize hardware work.
- Validation:
  Focused tests passed with `4 passed in 0.13s`; full tests passed with
  `263 passed in 30.31s`; YAML anchor check found no anchors in the generated
  metrics; raw/heavy artifact scan found no payloads in the v139 run
  artifact; `git diff --check` passed.
- Next step:
  If the user later gives explicit approval, use one exact registered approval
  packet, fill only valid rows for that step's worksheet scope, finalize with
  the exact registered step ID, and audit in approved-read-only mode. Without
  approval, continue only non-final offline work that does not repeat the
  v113-v116 strict-feasibility families over the same accepted model and
  seeds.
