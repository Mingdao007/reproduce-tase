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
