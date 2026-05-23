# Repository Migration Audit

## Objective

Move the existing TASE/UR10e reproduction work into
`Mingdao007/reproduce-tase` without importing unrelated UR10e workspace state
or large raw artifacts blindly.

## Evidence Inspected

- Remote repo `Mingdao007/reproduce-tase`: empty at migration start.
- Legacy source directory size: about `1.3G`.
- New repo clone path: `/home/andy/reproduce-tase`.
- New branch: `exp/tase-ur10e-v0-paper-audit`.
- Legacy UR10e workspace had many unrelated untracked experiment folders.

## Migrated Into Repo

- `REPRODUCTION_PLAN.md`
- `docs/goal.md`
- `configs/*.yaml`
- `assets/mjcf/ur10e_nominal.xml`
- `assets/urdf/ur10e_nominal.urdf`
- `scripts/*.py`
- `src/tase_repro/*`
- Existing reports:
  - `reports/v1_simulation_start_report.md`
  - `reports/full_article_reproduction_report.md`
- Lightweight run metadata and plots:
  - `runs/fig5_r_sweep/20260523T113301/*`
  - `runs/full_article_experiments/20260523T114332/*`
  - `runs/ur10e_smoke/*`
  - selected Markdown reports and PNG verification figures from
    `runs/full_paper_matlab/20260523T114034/worktree/RNN_F2/results/`

## Not Migrated As Ordinary Git Files

- Raw `.npz` arrays.
- MATLAB `.mat` files.
- Tarball snapshots.
- MATLAB source worktree, `.mat` files, tarballs, logs, and snapshot archives
  under the legacy `runs/full_paper_matlab` directory.

## Verification Status

- GitHub repo exists and was empty before migration.
- Local clone exists.
- Dedicated branch exists.
- Mandatory Markdown files have been created.
- Smoke scripts still need to be run from the new repo path before the v0
  branch is considered verified.

## Remaining Gaps

- Paper truth is not PDF-verified.
- UR10e math transfer is preliminary.
- MuJoCo smoke has not yet been re-run from this new clone.
- Initial commit and push are still pending.
