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
