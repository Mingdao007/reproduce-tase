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

